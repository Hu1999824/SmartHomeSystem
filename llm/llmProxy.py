from typing import List, Optional, Any
from langchain_ollama import ChatOllama
# Fixed import: use the new create_agent
from langchain.agents import create_agent
# Core components of LangChain v1.0+, unchanged
from langchain_core.tools import BaseTool, Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable  # create_agent returns a Runnable
import os
from langchain_core.messages import HumanMessage
from Vectordb.assicentVectorDb import AssicentVectorDB

# from tools.homeassistant_tool import HomeAssistantTool
from device.deviceController import DeviceController


class LLMProxy:
    def __init__(
        self,
        llm_model: str = "qwen3:14b",      # Ollama LLM model
        embedding_model: str = "qwen3-embedding:0.6b",
        temperature: float = 0.0,
        persist_directory: str = './data/chroma_db'
    ):
        #Init LLm
        self.llm = ChatOllama(
            model=llm_model,
            temperature=temperature,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://192.168.124.155:8080")
        )
        self.tools: List[BaseTool] = []
        # agent to  Runnable
        self.agent: Optional[Runnable] = None 
        
        self.device_controller = DeviceController()

        # Init vector db
        self.vector_db = AssicentVectorDB(
            persist_directory=persist_directory,
            embedding_model=embedding_model
        )

    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the agent's toolkit."""
        self.tools.append(tool)

    def _create_retrieval_tool(self) -> BaseTool:
        """Create a tool for querying the local knowledge base."""
        def _search_local_knowledge(query: str) -> str: 
            from datetime import datetime, timedelta

            # === Step 1:Analyze query ===
            now = datetime.now()
            base_date_str = now.strftime("%Y-%m-%d")
            tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
            after_tomorrow_str = (now + timedelta(days=2)).strftime("%Y-%m-%d")

            candidates = [query]

            if "tomorrow" in query:
                candidates.append(query.replace("tomorrow", tomorrow_str))
                candidates.append(f"{tomorrow_str} meeting schedule")

            if "today" in query:
                candidates.append(query.replace("today", base_date_str))
                candidates.append(f"{base_date_str} meeting")

            if "the day after tomorrow" in query:
                candidates.append(query.replace("the day after tomorrow", after_tomorrow_str))

            if any(kw in query for kw in ["meeting", "schedule", "agenda", "any", "check"]):
                candidates.append("meeting schedule")

            # === Step 2: Search for quey and merge the result ===
            all_results = []
            seen = set()
            for q in candidates:
                results = self.vector_db.get_llm_data(q, k=2) 
                for r in results:
                    if r not in seen:
                        seen.add(r)
                        all_results.append(r)

            if not all_results:
                return "No relevant information was found in your private knowledge base."
            
            return "\n".join(all_results[:3])

        return Tool(
            name="LocalKnowledgeSearch",
            func=_search_local_knowledge,  
            description=(
                "Search the user's private knowledge base, such as device manuals, "
                "house rules, or personal notes. Use this tool whenever the query "
                "mentions 'my home', 'my device', 'the manual says', or 'previously mentioned'."
            )
        )

    def create_agent(self) -> None:
        if not any(t.name == "LocalKnowledgeSearch" for t in self.tools):
            self.add_tool(self._create_retrieval_tool())
            
        if not any(t.name == "HomeAssistantControl" for t in self.tools):
            from tools.homeassistant_tool import HomeAssistantTool
            ha_tool = HomeAssistantTool(self.device_controller)
            self.add_tool(ha_tool.as_tool())
            
        if not any(t.name == "GetWeather" for t in self.tools):
            from tools.weather_tool import WeatherTool
            weather_tool = WeatherTool()
            self.add_tool(weather_tool.as_tool())
            
        if not any(t.name == "AddToKnowledgeBase" for t in self.tools):
            from tools.add_knowledge_tool import AddKnowledgeTool
            add_knowledge_tool = AddKnowledgeTool(self)
            self.add_tool(add_knowledge_tool.as_tool())
            
        if not any(t.name == "GetCurrentTime" for t in self.tools):
            from tools.time_tool import as_time_tool
            self.add_tool(as_time_tool())
        
        # use system_prompt rather prompt
        # system_prompt = (
        #     "You are a smart home assistant capable of using the user's private knowledge base "
        #     "and external tools to control devices. Respond accurately and concisely."
        # )
        system_prompt = (
            "You are a thoughtful personal and smart home assistant named Assicent. You have three core abilities:\n"
            "1. **Read the user's private knowledge base** (schedule, item locations, rules, etc.);\n"
            "2. **Write new information into the knowledge base** (when the user asks you to remember something);\n"
            "3. **Control devices & check the weather**.\n\n"
            "Response strategy:\n"
            "- When the user says 'remember...', 'note down...', or 'later...', **use the `AddToKnowledgeBase` tool**, "
            "  with input containing only the factual content (remove words like 'remember').\n"
            "- If the question involves personal information (meeting, where the remote is, etc.), **first check `LocalKnowledgeSearch`**.\n"
            "- Before controlling any device, confirm the entity ID comes from the knowledge base.\n"
            "- Politely refuse unrelated requests.\n"
            "**Important: Never fabricate information. If uncertain, check the knowledge base; "
            "if something must be remembered, call the writing tool.**"
            "**Additional rule:** When possible, output responses primarily in English, unless the user explicitly requests Chinese."
        )
        

        #  langgraph.create_agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,  
            # other checkpointer 
        )


    def handle_complex_query(self, query: str, chat_history=None) -> str:
        if self.agent is None:
            raise RuntimeError("Agent not initialized. Call create_agent() first.")

        # build messages list
        messages = []
        if chat_history:
            messages.extend(chat_history)
        messages.append(HumanMessage(content=query))

        try:
            response = self.agent.invoke({"messages": messages})
            # response is State，include "messages" list
            last_msg = response["messages"][-1]
            return last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        except Exception as e:
            return f"Processing failed: {str(e)}"


# test/llm_test.py
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from llm.llmProxy import LLMProxy


class TestLLMProxy(unittest.TestCase):

    def setUp(self):
        # Mock dependencies during initialization
        with patch('llm.llmProxy.ChatOllama') as mock_chat_ollama, \
             patch('llm.llmProxy.AssicentVectorDB') as mock_vector_db_class, \
             patch('llm.llmProxy.DeviceController') as mock_device_ctrl_class:

            self.mock_llm = MagicMock()
            mock_chat_ollama.return_value = self.mock_llm

            self.mock_vector_db = MagicMock()
            mock_vector_db_class.return_value = self.mock_vector_db

            self.mock_device_ctrl = MagicMock()
            mock_device_ctrl_class.return_value = self.mock_device_ctrl

            self.proxy = LLMProxy(
                llm_model="test-model",
                embedding_model="test-embed",
                persist_directory="./test_db"
            )

    def test_initialization(self):
        from llm.llmProxy import ChatOllama, AssicentVectorDB
        # Just ensure mocks were called correctly
        self.assertIsNotNone(self.proxy.llm)
        self.assertIsNotNone(self.proxy.vector_db)
        self.assertIsNone(self.proxy.agent)

    @patch('llm.llmProxy.Tool')
    def test_create_retrieval_tool(self, mock_tool_class):
        mock_tool_instance = MagicMock()
        mock_tool_class.return_value = mock_tool_instance

        self.proxy.vector_db.get_llm_data.return_value = ["Meeting at 9 AM"]

        tool = self.proxy._create_retrieval_tool()
        self.assertEqual(tool, mock_tool_instance)

        # Call the wrapped function
        func = mock_tool_class.call_args[1]['func']
        result = func("What's my schedule for tomorrow?")
        self.assertIn("Meeting at 9 AM", result)

    @patch('llm.llmProxy.create_agent')
    @patch('llm.llmProxy.Tool')
    def test_create_agent_registers_all_tools(self, mock_tool_class, mock_create_agent):
        # Mock external tool modules
        mock_ha_tool = MagicMock()
        mock_weather_tool = MagicMock()
        mock_add_kb_tool = MagicMock()
        mock_time_tool = MagicMock()

        with patch.dict('sys.modules', {
            'tools.homeassistant_tool': MagicMock(),
            'tools.weather_tool': MagicMock(),
            'tools.add_knowledge_tool': MagicMock(),
            'tools.time_tool': MagicMock(),
        }):
            # Setup return values for tool constructors
            sys.modules['tools.homeassistant_tool'].HomeAssistantTool.return_value.as_tool.return_value = mock_ha_tool
            sys.modules['tools.weather_tool'].WeatherTool.return_value.as_tool.return_value = mock_weather_tool
            sys.modules['tools.add_knowledge_tool'].AddKnowledgeTool.return_value.as_tool.return_value = mock_add_kb_tool
            sys.modules['tools.time_tool'].as_time_tool.return_value = mock_time_tool

            # Mock LocalKnowledgeSearch
            mock_tool_class.return_value = MagicMock(name="LocalKnowledgeSearch")

            self.proxy.create_agent()

            # Should have 5 tools
            self.assertEqual(len(self.proxy.tools), 5)
            mock_create_agent.assert_called_once()
            self.assertIsNotNone(self.proxy.agent)

    def test_handle_complex_query_without_agent_raises_error(self):
        with self.assertRaises(RuntimeError) as cm:
            self.proxy.handle_complex_query("Hello")
        self.assertIn("Agent not initialized", str(cm.exception))

    # ✅ NO @patch HERE — this is the key fix!
    def test_handle_complex_query_calls_agent_and_returns_content(self):
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [MagicMock(content="The light is on.")]
        }
        self.proxy.agent = mock_agent

        query = "Is the living room light on?"
        result = self.proxy.handle_complex_query(query)

        mock_agent.invoke.assert_called_once()
        args = mock_agent.invoke.call_args[0][0]
        self.assertIn("messages", args)
        self.assertEqual(len(args["messages"]), 1)

        # Import real HumanMessage to check type
        from langchain_core.messages import HumanMessage
        actual_msg = args["messages"][0]
        self.assertIsInstance(actual_msg, HumanMessage)
        self.assertEqual(actual_msg.content, query)

        self.assertEqual(result, "The light is on.")

    def test_handle_complex_query_handles_agent_exception(self):
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = Exception("LLM timeout")
        self.proxy.agent = mock_agent

        result = self.proxy.handle_complex_query("Test")
        self.assertIn("Processing failed", result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
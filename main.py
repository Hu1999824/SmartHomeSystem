# main.py  —— Orchestrator & Demo
import os
import sys

# Ensure local packages can be imported (run from repo root: python main.py)
sys.path.append(os.path.dirname(__file__))

# ===== Imports according to your current directory structure =====
from Voice.audio.recordAudio import recordAudio
from Voice.audio.whisperAsr import WhisperAsr

from Classifier.task_classifier import TaskClassifier, Intent  # Ensure both exist
# If Intent does not exist, add enum in task_classifier: TURN_ON / TURN_OFF / QUERY_STATUS / COMPLEX

# from llm.llmProxy import LlmProxy
from llm.llmProxy import LLMProxy
from device.deviceController import DeviceController
from langchain_core.documents import Document

# (Optional) Read runtime configuration
try:
    from Voice.config.settings import RECORD_DURATION
except Exception:
    RECORD_DURATION = 4


class SmartHomeSystem:
    """
    Orchestrator:
    - Integrate Voice/ASR → Classifier → (Rule / LLM) → Device
    - Support both voice and text modes
    - Feedback confirmation (log + dynamic rule/vector DB)
    - Friendly demo output
    """
    def __init__(self):
        self.asr = WhisperAsr()
        self.classifier = TaskClassifier()
        # self.llmProxy = LlmProxy()
        self.llmProxy = LLMProxy()
        
        self._initialize_knowledge_base() 
    
    def _initialize_knowledge_base(self):
        print("[KB] Initializing local knowledge base...")
        
        # Example of private information to be retrievable by LLM
        documents = [
            Document(page_content="The air conditioner remote manual states: the blue button activates cooling mode.", 
                     metadata={"source": "ac_manual"}),
            Document(page_content="The home Wi-Fi password is: HomeSmart123.", 
                     metadata={"source": "personal_note"}),
            Document(page_content="At 7 AM, the living room light will automatically turn on.", 
                     metadata={"source": "automation_rule"}),
            Document(page_content="My schedule: Every Monday at 9:30 AM there is a team meeting. A reminder should be set 15 minutes before.", 
                    metadata={"source": "schedule"}),
            Document(page_content="Scene: Sleep mode executes the following actions when triggered: turn off all lights in the living room, kitchen, and hallway. Gradually dim the bedroom main light to 20% brightness and set color temperature to 2700K warm light. Automatically close smart curtains. Turn on the air conditioner sleep mode and adjust temperature to 26°C. Play sleep white noise on the smart speaker and stop automatically after 30 minutes.", 
                    metadata={"source": "automation_rule"}),
            Document(page_content="The device's average power consumption is 8 watts.",
                    metadata={"source": "device_energy"}),
        ]

        try:
            # Check if the database already exists (if so, skip adding again)
            # Note: Chroma stores persistently by default, but we add each time for simplicity.
            
            # Optionally clear old data on startup to ensure a fresh run
            # self.llmProxy.vector_db.delete_collection() 
            
            self.llmProxy.vector_db.add_documents(documents)
            print(f"✅ [KB] Successfully added {len(documents)} documents to the vector database.")
            
        except Exception as e:
            print(f"❌ [KB] Knowledge base loading failed: {e}")
            # If loading fails, continue system execution
        
        self.llmProxy.create_agent() 
        self.deviceCtrl = DeviceController()
        # self.mode = "voice"   # Default voice mode; input 'text' to switch
        self.mode = "text"

    # # —— Device entity resolver: a simple example mapping, extend as needed —— #
    # def resolveEntityId(self, userInput: str) -> str:
    #     text = userInput.lower()
    #     if ("light" in text) or ("灯" in text):
    #         return "light.living_room"
    #     if ("heater" in text) or ("暖气" in text):
    #         return "switch.heater"
    #     if ("sensor" in text) or ("传感" in text):
    #         return "sensor.living_room"
    #     # Default entity to ensure demo continuity
    #     return "light.living_room"

        # —— Smart Home Device Detailed Analysis: Supports Multiple Rooms and Multiple Device Types —— #
    def resolveEntityId(self, userInput: str) -> str:
        text = userInput.lower()

        # Room reflection
        room_map = {
            "客厅": "living_room",
            "living room": "living_room",
            "卧室": "bedroom",
            "bedroom": "bedroom",
            "餐厅": "dining_room",
            "dining room": "dining_room",
            "厨房": "kitchen",
            "kitchen": "kitchen",
            "浴室": "bathroom",
            "bathroom": "bathroom",
        }

        # Default room (if not recognized)
        target_room = "living_room"
        for key, val in room_map.items():
            if key in text:
                target_room = val
                break

        # Device type mapping
        device_map = {
            ("灯", "light"): "light",
            ("空调", "冷气", "ac", "air conditioner"): "ac",
            ("窗帘", "curtain"): "curtain",
            ("电视", "tv"): "tv",
            ("暖气", "heater", "switch"): "switch",
            ("传感器", "sensor"): "sensor",
        }

        target_device = None
        for keywords, dev in device_map.items():
            if any(k in text for k in keywords):
                target_device = dev
                break

        # If no device type is matched, the default is to return a light.
        if not target_device:
            target_device = "light"

        # Concatenate entity_id
        entity_id = f"{target_device}.{target_room}"
        return entity_id


    def handleSimpleIntent(self, intent: Intent, userInput: str) -> str:
        entityId = self.resolveEntityId(userInput)
        if intent == Intent.TURN_ON:
            return self.deviceCtrl.executeCommand(entityId, "turn_on")
        if intent == Intent.TURN_OFF:
            return self.deviceCtrl.executeCommand(entityId, "turn_off")
        if intent == Intent.QUERY_STATUS:
            return self.deviceCtrl.getDeviceStatus(entityId)
        return "Unknown intent"

    def loopOnce(self) -> bool:
        """
        Return False to exit the main loop
        """
        # 1) Obtain input (voice or text)
        if self.mode == "voice":
            audioFile = recordAudio(duration=RECORD_DURATION)
            if not os.path.exists(audioFile):
                print("⚠️ Audio file not found")
                return True
            userInput = self.asr.transcribeAudio(audioFile)
            if not userInput:
                print("⚠️ No valid speech recognized")
                return True
        else:
            userInput = input("> ").strip()
            if userInput in ("text", "voice"):
                self.mode = userInput
                print(f"✅ Switched to {self.mode} mode")
                return True
            if userInput in ("quit", "exit"):
                print("👋 Goodbye!")
                return False

        # 2) Intent classification
        intent = self.classifier.classify(userInput) if hasattr(self.classifier, "classify") \
            else self.classifier.classifyText(userInput)
        print(f"[Predicted Intent] {getattr(intent, 'value', str(intent))}")

        # 3) Feedback confirmation (optional correction & learning trigger)
        # correct = input("Is recognition correct? (y/n): ").strip().lower()
        # actualIntent = intent
        # if correct == "n":
        #     print("Select actual intent: 1.turn_on  2.turn_off  3.query_status  4.complex")
        #     choice = input("Enter number: ").strip()
        #     mapping = {"1": Intent.TURN_ON, "2": Intent.TURN_OFF,
        #                "3": Intent.QUERY_STATUS, "4": Intent.COMPLEX}
        #     actualIntent = mapping.get(choice, Intent.COMPLEX)

        #     # Allow different feedback API names: record_feedback / recordFeedback
        #     if hasattr(self.classifier, "record_feedback"):
        #         self.classifier.record_feedback(userInput, intent, actualIntent)
        #     elif hasattr(self.classifier, "recordFeedback"):
        #         self.classifier.recordFeedback(userInput, intent, actualIntent)
        #     print("✅ Feedback recorded and memory/rules updated")
        #     intent = actualIntent

        # 4) Route execution
        if intent == Intent.COMPLEX:
            print("[LLM Path] Processing via LangChain tools...")
            result = self.llmProxy.handle_complex_query(userInput)
            print("System response:", result)
        else:
            result = self.handleSimpleIntent(intent, userInput)
            print("[Device Control]", result)

        return True

    def run(self):
        print("=== Smart Voice Home System (Orchestrator) ===")
        print("Commands: 'text' to switch text mode | 'voice' for voice mode | 'quit' to exit\n")
        while True:
            if not self.loopOnce():
                break


if __name__ == "__main__":
    SmartHomeSystem().run()

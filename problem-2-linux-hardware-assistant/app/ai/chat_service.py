
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

from app.ai.tool_registry import TOOL_REGISTRY, execute_tool


# ==========================================
# 1. Configuration
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=30000)
)


# ==========================================
# 2. Gemini Tool Declarations
# ==========================================

def create_tool_declaration(name, description):
    return types.FunctionDeclaration(
        name=name,
        description=description,
        parameters_json_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    )


tool_declarations = [
    create_tool_declaration(
        "get_cpu_info",
        "Get CPU model, architecture, core count and frequency."
    ),
    create_tool_declaration(
        "get_memory_info",
        "Get total, used and available RAM and swap memory."
    ),
    create_tool_declaration(
        "get_storage_info",
        "Get storage devices, partitions and disk usage."
    ),
    create_tool_declaration(
        "get_gpu_info",
        "Get detected GPU and available GPU information."
    ),
    create_tool_declaration(
        "get_environment_info",
        "Detect the operating system, Linux distribution, kernel, "
        "and whether the application runs in WSL or native Linux."
    )
]

hardware_tool = types.Tool(
    function_declarations=tool_declarations
)


# ==========================================
# 3. System Instructions
# ==========================================

SYSTEM_INSTRUCTION = """
You are a Linux Hardware Assistant.

Answer questions about the user's actual Linux hardware.

Rules:
1. Use hardware tools to retrieve factual hardware information.
2. Never invent hardware specifications.
3. Only use information returned by the tools.
4. If information is unavailable, clearly say so.
5. Explain technical information in simple language.
6. Always consider environment information when interpreting
   hardware results.
7. If running inside WSL, distinguish virtualized resources
   from physical Windows hardware.
8. Never claim that WSL memory represents the complete
   physical RAM installed in the laptop.
9. Never claim that a virtual disk represents the physical
   drive capacity.
10. Do not identify a physical GPU from a virtual display driver.
11. General Linux questions can be answered without tools.
12. Do not execute arbitrary shell commands.
"""


# ==========================================
# 4. Hardware Chat Service
# ==========================================

class HardwareChatService:

    def __init__(self):
        self.history = []
        self.max_tool_calls = 3

    def generate_response(self, contents):
        """Call Gemini and handle API failures."""

        try:
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[hardware_tool]
                )
            )

        except errors.APIError as error:

            status_code = getattr(error, "code", None)

            print(f"\n[Gemini API error: HTTP {status_code}]")

            if status_code == 429:
                raise RuntimeError(
                    "Gemini request limit reached. Please try again later."
                )

            if status_code == 503:
                raise RuntimeError(
                    "Gemini is temporarily unavailable. Please try again."
                )

            if status_code in (400, 401, 403):
                raise RuntimeError(
                    "Gemini rejected the request. Check the model, "
                    "API key and request configuration."
                )

            raise RuntimeError(
                "Gemini API request failed. Please try again."
            )

        except Exception:
            raise RuntimeError(
                "Unable to connect to Gemini. "
                "Please check your internet connection."
            )

    def chat(self, user_message: str) -> str:

        if not user_message or not user_message.strip():
            return "Please enter a question."

        self.history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=user_message)
                ]
            )
        )

        print("\n[Connecting to Gemini...]", flush=True)

        response = self.generate_response(self.history)

        print("[Gemini responded]", flush=True)

        tool_call_count = 0

        while True:

            function_calls = response.function_calls

            if not function_calls:

                answer = response.text or "I couldn't generate an answer."

                if response.candidates:
                    self.history.append(
                        response.candidates[0].content
                    )

                return answer

            if response.candidates:
                self.history.append(
                    response.candidates[0].content
                )

            function_response_parts = []

            for function_call in function_calls:

                tool_name = function_call.name
                arguments = function_call.args or {}

                print(
                    f"\n[Tool requested: {tool_name}]",
                    flush=True
                )

                if tool_call_count >= self.max_tool_calls:

                    result = {
                        "status": "error",
                        "message": "Maximum tool-call limit reached."
                    }

                elif tool_name not in TOOL_REGISTRY:

                    result = {
                        "status": "error",
                        "message": "This tool is not allowed."
                    }

                elif arguments:

                    result = {
                        "status": "error",
                        "message": "Unexpected tool arguments rejected."
                    }

                else:

                    tool_call_count += 1
                    result = execute_tool(tool_name)

                print(
                    f"[Tool completed: {tool_name}]",
                    flush=True
                )

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={
                            "result": result
                        }
                    )
                )

            # Send tool results back to Gemini.
            self.history.append(
                types.Content(
                    role="user",
                    parts=function_response_parts
                )
            )

            print("\n[Sending hardware results to Gemini...]")

            response = self.generate_response(self.history)

    def reset_conversation(self):
        self.history.clear()
        print("Conversation history cleared.")


# ==========================================
# 5. CLI Application
# ==========================================

if __name__ == "__main__":

    assistant = HardwareChatService()

    print("\n====================================")
    print("       Linux Hardware Assistant")
    print("====================================")

    print("Ask questions about your computer.")
    print("Type 'reset' to clear conversation history.")
    print("Type 'exit' to quit.\n")

    while True:

        try:

            question = input("You: ").strip()

            if question.lower() in ["exit", "quit"]:
                print("\nAssistant: Goodbye!")
                break

            if question.lower() == "reset":
                assistant.reset_conversation()
                continue

            answer = assistant.chat(question)

            print(f"\nAssistant: {answer}\n")

        except RuntimeError as error:
            print(f"\nAssistant Error: {error}\n")

        except KeyboardInterrupt:
            print("\n\nAssistant: Goodbye!")
            break

        except Exception:
            print(
                "\nAssistant: Something unexpected happened. "
                "Please try again.\n"
            )

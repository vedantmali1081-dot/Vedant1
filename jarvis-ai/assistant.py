import json

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT, api_key_is_valid
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS


class JarvisAssistant:
    def __init__(self) -> None:
        if not api_key_is_valid():
            raise ValueError("OpenAI API key set nahi hai. .env file mein sahi key daalein.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    def ask(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})

        for _ in range(5):
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=self.messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            message = response.choices[0].message
            tool_calls = message.tool_calls or []

            if not tool_calls:
                reply = message.content or "Done."
                self.messages.append({"role": "assistant", "content": reply})
                return reply

            self.messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in tool_calls
                    ],
                }
            )

            for call in tool_calls:
                args = json.loads(call.function.arguments or "{}")
                func = TOOL_FUNCTIONS[call.function.name]
                result = func(**args)
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    }
                )

        return "I could not finish that request."

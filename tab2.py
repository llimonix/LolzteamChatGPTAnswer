import json
from fake_useragent import UserAgent
import requests

headers = {
    "authority": "chatbot.theb.ai",
    "content-type": "application/json",
    "origin": "https://chatbot.theb.ai",
    "user-agent": UserAgent()['google chrome']
}

class ThabAi:
    def get_response(self, prompt: str) -> str:
        while True:
            response = requests.post(
                "https://chatbot.theb.ai/api/chat-process",
                json={"prompt": prompt, "options": {}},
                headers=headers,
            )
            if response.status_code == 403 or response.status_code == 429:
                headers["user-agent"] = UserAgent().random
                continue
            response.raise_for_status()
            response_data = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "utterances" in data:
                        response_data += " ".join(
                            utterance["text"] for utterance in data["utterances"]
                        )
                    elif "delta" in data:
                        response_data += data["delta"]
            return response_data

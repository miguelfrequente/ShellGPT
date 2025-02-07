import json
import requests

url = "http://localhost:11434/api/chat"

def get_response(prompt):
    input = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": prompt

            }
        ],
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=input)
    return response.json()["message"]["content"]


if __name__ == "__main__":
    print(get_response("What is the capital of France?"))

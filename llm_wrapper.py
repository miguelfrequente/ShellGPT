import json
import requests

import sys
import os 

import subprocess

from pydantic import BaseModel
from ollama import chat

url = "http://localhost:11434/api/chat"

system_prompt = """
You are an expert using the command line interface with the bash and zsh shell. 
The user will ask you how to do particular things with the command line interface and you will provide two things:
First, the command that will fulfill the user's intent.
Second, an explanation of the command and the options that are intended to be used.
"""


class CommandResponse(BaseModel):         
    command: str
    explanation: str

def get_response(prompt):
    response = chat(
        messages=[
            {
                "role": "system",
                "content": system_prompt
                },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama3",
        format=CommandResponse.model_json_schema(),
    )

    return CommandResponse.model_validate_json(response.message.content)

def get_response_o(prompt):
    input = {
        "model": "llama3",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
                },
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

def check_ollama_running():
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama is not running. Please start the server by running `ollama` in the terminal.")



def validate_shell_arguments(argv):

    if len(argv) == 1:
        print("Usage: omni <prompt>. The prompt should be in quotes!")
        exit(1)
    elif len(argv) > 2:
        print("")
        print("## CAUTION: Please provide your prompt in quotes! ##")
        print("")
        print("Your input was devided into:")
        output_string = ""
        for i, arg in enumerate(argv):
            output_string = output_string + str(i) +" : " + arg + " -- "

        print(output_string)

        exit(1)
    
    return argv[1]


if __name__ == "__main__":
    check_ollama_running()

    user_input = validate_shell_arguments(sys.argv)

    ollama_response = get_response(user_input)

    print("> Command to be executed according to your request:")
    print("")
    print(ollama_response.command)
    print("")
    print("> Explanation of the command:")
    print("")
    print(ollama_response.explanation.strip())

    print("")
    user_feedback = input("Should the command be executed?[yes/no]")

    if user_feedback == "yes":
        print("Executing command...")
        result = subprocess.run(ollama_response.command, shell = True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        #os.system(ollama_response.command)

    


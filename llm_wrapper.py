import json
import requests

import sys
import os 

import subprocess

import platform 

from pydantic import BaseModel
from ollama import chat

url = "http://localhost:11434/api/chat"


class SystemPrompts:
    platform = "bac"

    @classmethod
    def decision_maker(cls):
        return f"""
            You are an expert using the command line interface with the bash and zsh shell. 
            Also, you are an expert regarding the topics of IT, computer science and software engineering.
            The user will ask you particular questions and your objective is to decide whether it is necessary to use the command line interface to fulfill the user's intent.
            You can only provide two answers: Yes or No.

            The user uses the platform: {cls.platform}
        """

    @classmethod
    def information_provider(cls):
        return f"""
            You are an expert using the command line interface with the bash and zsh shell. 
            Also, you are an expert regarding the topics of IT, computer science and software engineering.
            The user will ask you particular questions and your objective is to provide information about the topic from your own knowledge.
            You will respond briefly and informatively.

            The user uses the platform: {cls.platform}
        """

    @classmethod
    def command_generator(cls):
        return f"""
            You are an expert using the command line interface with the bash and zsh shell. 
            The user will ask you how to do particular things with the command line interface and you will provide two things:
            First, the command that will fulfill the user's intent.
            Second, an explanation of the command and the options that are intended to be used.

            The user uses the platform: {cls.platform}
        """


class CommandResponse(BaseModel):         
    command: str
    explanation: str

class Engine:
    model = "deepseek-r1:7b" #"llama3"
    @staticmethod
    def get_command(prompt):
        response = chat(
            messages=[
                {
                    "role": "system",
                    "content": SystemPrompts.command_generator()
                    },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=Engine.model,
            format=CommandResponse.model_json_schema(),
        )

        return CommandResponse.model_validate_json(response.message.content)

    @staticmethod
    def get_decision(prompt):
        response = chat(
            messages=[
                {
                    "role": "system",
                    "content": SystemPrompts.decision_maker()
                    },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=Engine.model,
        )

        return response.message.content

    @staticmethod
    def get_information(prompt):
        response = chat(
            messages=[
                {
                    "role": "system",
                    "content": SystemPrompts.information_provider()
                    },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=Engine.model,
        )

        return response.message.content

"""
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
"""

def check_ollama_running():
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama is not running. Please start the server by running `ollama` in the terminal.")

def check_platform():
    system_name = platform.system()

    if system_name == "Linux":
        return "Linux"
    elif system_name == "Darwin":
        return "macOS"
    elif system_name == "Windows":
        return "Windows"
    else:
        return "Unknown"

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

    SystemPrompts.platform = check_platform()

    user_input = validate_shell_arguments(sys.argv)


    while True:
        ollama_response = Engine.get_decision(user_input)

        additional_context = ""

        print(ollama_response)

        if ollama_response == "Yes":
            ollama_response = Engine.get_command(user_input)

            print("> Command to be executed according to your request:")
            print("")
            print(ollama_response.command)
            print("")
            print("> Explanation of the command:")
            print("")
            print(ollama_response.explanation.strip())

            print("")
            user_feedback = input("Should the command be executed [yes/no]? ")

            if user_feedback == "yes":
                print("Executing command...")
                result = subprocess.run(ollama_response.command, shell = True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(result.stdout)
                print(result.stderr)

                additional_context = result.stdout + "\n\n" + result.stderr

        elif ollama_response == "No":
            ollama_response = Engine.get_information(user_input)
            print(ollama_response)
            print("")

        user_feedback = input("Can I help you further? ")

        if "no" in user_feedback or "No" in user_feedback or "NO" in user_feedback or "n" in user_feedback or "N" in user_feedback:
            break

        user_input = additional_context + "\n" + user_feedback

        print(user_input)



    


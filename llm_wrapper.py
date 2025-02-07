import json
import requests

import sys
import os 

import subprocess

url = "http://localhost:11434/api/chat"

system_prompt = """
You are an expert using the command line interface with the bash and zsh shell. 
The user will ask you how to do particular things with the command line interface and you will provide to things:
First, the command that will fulfill the user's intent.
Second, the explanation of the command and the options that you used.
"""
            

def get_response(prompt):
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

    user_input = validate_shell_arguments(sys.argv)

    print(get_response(user_input))

    user_feedback = input("Should the command be executed?[yes/no]")

    


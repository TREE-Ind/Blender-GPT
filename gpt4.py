import sys
import os

# Get the current directory of the __init__.py file
current_dir = os.path.dirname(os.path.realpath(__file__))

# Add the 'libs' directory to the sys.path
libs_path = os.path.join(current_dir, "lib")
if libs_path not in sys.path:
    sys.path.append(libs_path)

import openai
import bpy

def get_api_key():
    preferences = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    return preferences.api_key

def get_gpt4_response(prompt, max_tokens=250):

    preferences = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    system_prompt = preferences.system_prompt

    openai.api_key = get_api_key()

    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": system_prompt},{"role": "user", "content": prompt}])
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

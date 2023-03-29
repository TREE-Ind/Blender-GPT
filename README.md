# BlenderGPT
An all-in-one Blender assistant powered by GPT3/4 + Whisper integration

## Installation

Download the add-on as a zip file from this repository

Open Blender editor preferences and install the zip file you just download

Enable the newly installed Blender-GPT add-on and enter your OpenAI api key in the preferences.

## Features

Carry out editor tasks via natural language including somewhat complicated prompts
Whisper integration for accurate ASR allowing one to control Blender by voice with relative ease

Uses new API structure with chat completion endpoint + System Role (we plan to make this editable via an add-on preference)

# Usage

Open the GPT-4 Assistant tab in the 3D view.

There are two way to interact with the add-on

1) Clicking on the "Execute by voice" button will record speech via whisper and automatically execute the request
2) Enter a prompt in the input field and click on the "Execute by text" button

## Limitations

The tasks this add-on is capable of is limited to the data used to train GPT3.5/4.  Soon we expect things like the OpenAI retrieval plugin to make it possible to embed the entirety of the Blender python docs which may open more possibilities.

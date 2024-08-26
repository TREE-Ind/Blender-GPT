import sys
import os
import bpy
import subprocess
import pyaudio

import wave
import openai
import numpy as np


# Add the 'libs' folder to the Python path
libs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if libs_path not in sys.path:
    sys.path.append(libs_path)



bl_info = {
    "name": "GPT-4 Blender Assistant",
    "blender": (2, 93, 0),
    "category": "AI",
    "author": "TREE Industries",
    "version": (1, 0, 0),
    "location": "View3D > Tool Shelf > GPT-4 Blender Assistant",
    "description": "A Blender editor assistant powered by GPT-4"
}

class GPT4AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    api_key: bpy.props.StringProperty(
        name="API Key",
        description="Enter your GPT-4 API key",
        default="",
        subtype="PASSWORD",
    )

    system_prompt: bpy.props.StringProperty(
        name="System Prompt",
        description="Custom system prompt for GPT-4 Blender Assistant",
        default="You are a Blender editor assistant. You will respond to all requests by writing python code based on the user request. Only respond with the raw python code and to not explain anything. Do not include markdown formatting, do not include the word python at the start",
    )

    model: bpy.props.StringProperty(
        name="Model To Use",
        description="Enter the GPT model to use",
        default="gpt-3.5-turbo",
    )

    audio_path: bpy.props.StringProperty(
        name="Whisper Save Path",
        description="Path to save whisper transcription",
        default="recorded_audio.wav",
    )

    api_base: bpy.props.StringProperty(
        name="API Base URL",
        description="Enter the custom API base URL (leave empty for default OpenAI URL)",
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "audio_path")
        layout.prop(self, "model")
        layout.prop(self, "api_key")
        layout.prop(self, "system_prompt")
        layout.prop(self, "api_base")

# Dependencies
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False
    return True

def check_and_install_dependencies():
    packages = ["openai", "numpy"]
    installed = True

    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            success = install_package(package)
            if success:
                print(f"{package} installed successfully.")
            else:
                installed = False
                print(f"Failed to install {package}.")
    
    if not installed:
        bpy.ops.ui.show_message_box(message="Some dependencies failed to install. Check the Blender console for details.")

# GPT4
def get_api_key():
    preferences = bpy.context.preferences.addons[__name__].preferences
    return preferences.api_key

def get_gpt4_response(prompt, max_tokens=250):
    preferences = bpy.context.preferences.addons[__name__].preferences
    system_prompt = preferences.system_prompt
    model = preferences.model
    api_base = preferences.api_base

    openai.api_key = get_api_key()
    if api_base:
        openai.api_base = api_base

    # Maintain conversation history
    conversation_history = [{"role": "system", "content": system_prompt}]
    
    # Add previous user inputs and assistant replies to the conversation history
    for item in bpy.context.scene.gpt4_chat_log:
        conversation_history.append({"role": "user", "content": item.user_input})
        conversation_history.append({"role": "assistant", "content": item.gpt4_response})

    conversation_history.append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=conversation_history,
        max_tokens=max_tokens
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

# Operators
class GPT4BlenderAssistantTextOperator(bpy.types.Operator):
    bl_idname = "wm.gpt4_blender_assistant_text"
    bl_label = "Execute by Text"

    def execute(self, context):
        input_text = context.scene.gpt4_blender_assistant_input
        response = get_gpt4_response(input_text)

        def remove_triple_backticks(text: str) -> str:
            if text.startswith("```") and text.endswith("```"):
                return text[3:-3]
            return text

        response = remove_triple_backticks(response)
        context.scene.gpt4_blender_assistant_output = response
        self.update_chat_log(context, input_text, response)

        try:
            exec(response, {"bpy": bpy, "context": context})
        except Exception as e:
            context.scene.gpt4_blender_assistant_output += "\n\nError: " + str(e)

        return {'FINISHED'}

    def update_chat_log(self, context, input_text, response):
        chat_log_item = context.scene.gpt4_chat_log.add()
        chat_log_item.user_input = input_text
        chat_log_item.gpt4_response = response

class GPT4BlenderAssistantVoiceOperator(bpy.types.Operator):
    bl_idname = "wm.gpt4_blender_assistant_voice"
    bl_label = "Execute by Voice"

    def execute(self, context):
        transcription = transcribe_audio()
        context.scene.gpt4_blender_assistant_input = transcription
        bpy.ops.wm.gpt4_blender_assistant_text()
        return {'FINISHED'}

# UI
class GPT4ChatLogItem(bpy.types.PropertyGroup):
    user_input: bpy.props.StringProperty(name="User Input")
    gpt4_response: bpy.props.StringProperty(name="GPT-4 Response")

class GPT4BlenderAssistantPanel(bpy.types.Panel):
    bl_label = "BlenderGPT"
    bl_idname = "OBJECT_PT_gpt4_blender_assistant"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GPT-4 Assistant'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Input:")
        layout.operator("wm.gpt4_blender_assistant_voice", text="Execute by Voice", icon='PLUS')
        layout.prop(scene, "gpt4_blender_assistant_input", text="")
        layout.operator("wm.gpt4_blender_assistant_text", icon='PLUS')

        layout.label(text="Chat Log:")
        layout.operator("wm.gpt4_clear_chat_log", text="Clear Chat Log", icon='X')
        for item in scene.gpt4_chat_log:
            copy_user_input_op = layout.operator("wm.gpt4_copy_user_input", text="You: " + item.user_input)
            copy_user_input_op.user_input = item.user_input
            layout.label(text="GPT-4: " + item.gpt4_response)

class GPT4ClearChatLogOperator(bpy.types.Operator):
    bl_idname = "wm.gpt4_clear_chat_log"
    bl_label = "Clear Chat Log"

    def execute(self, context):
        context.scene.gpt4_chat_log.clear()
        return {'FINISHED'}

class GPT4CopyUserInputOperator(bpy.types.Operator):
    bl_idname = "wm.gpt4_copy_user_input"
    bl_label = "Copy User Input and Paste to Input Field"
    user_input: bpy.props.StringProperty(name="User Input")

    def execute(self, context):
        bpy.context.window_manager.clipboard = self.user_input
        context.scene.gpt4_blender_assistant_input = self.user_input
        return {'FINISHED'}

# Whisper
def get_audio_path():
    preferences = bpy.context.preferences.addons[__name__].preferences
    return preferences.audio_path

def transcribe_audio():
    preferences = bpy.context.preferences.addons[__name__].preferences
    openai.api_key = get_api_key()
    api_base = preferences.api_base
    if api_base:
        openai.api_base = api_base

    audio_file = get_audio_path()
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms chunks
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    WAVE_OUTPUT_FILENAME = audio_file

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Start speaking...")

    frames = []
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        # Stop recording if silence is detected or after a certain number of frames
        if len(frames) > 50 and np.mean(np.abs(np.frombuffer(b''.join(frames[-50:]), dtype=np.int16))) < 300:
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the audio data to a WAV file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Call the Whisper API using the correct method
    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Remove the local WAV file after transcription
    os.remove(WAVE_OUTPUT_FILENAME)

    return transcript["text"]

def register():
    bpy.utils.register_class(GPT4AddonPreferences)
    bpy.utils.register_class(GPT4ChatLogItem)
    bpy.utils.register_class(GPT4BlenderAssistantPanel)
    bpy.utils.register_class(GPT4ClearChatLogOperator)
    bpy.utils.register_class(GPT4CopyUserInputOperator)
    bpy.utils.register_class(GPT4BlenderAssistantTextOperator)
    bpy.utils.register_class(GPT4BlenderAssistantVoiceOperator)
    bpy.types.Scene.gpt4_blender_assistant_input = bpy.props.StringProperty(
        name="Input",
        description="Input text for GPT-4 Blender Assistant",
        default="",
    )
    bpy.types.Scene.gpt4_blender_assistant_output = bpy.props.StringProperty(
        name="Output",
        description="Output text from GPT-4 Blender Assistant",
        default="",
    )
    bpy.types.Scene.gpt4_chat_log = bpy.props.CollectionProperty(type=GPT4ChatLogItem)
    check_and_install_dependencies()

def unregister():
    bpy.utils.unregister_class(GPT4AddonPreferences)
    bpy.utils.unregister_class(GPT4ChatLogItem)
    bpy.utils.unregister_class(GPT4BlenderAssistantPanel)
    bpy.utils.unregister_class(GPT4ClearChatLogOperator)
    bpy.utils.unregister_class(GPT4CopyUserInputOperator)
    bpy.utils.unregister_class(GPT4BlenderAssistantTextOperator)
    bpy.utils.unregister_class(GPT4BlenderAssistantVoiceOperator)
    del bpy.types.Scene.gpt4_blender_assistant_input
    del bpy.types.Scene.gpt4_blender_assistant_output
    del bpy.types.Scene.gpt4_chat_log

if __name__ == "__main__":
    register()
import sys
import os

# Get the current directory of the __init__.py file
current_dir = os.path.dirname(os.path.realpath(__file__))

# Add the 'libs' directory to the sys.path
libs_path = os.path.join(current_dir, "lib")
if libs_path not in sys.path:
    sys.path.append(libs_path)

import bpy
from . import gpt4, whisper

class GPT4BlenderAssistantTextOperator(bpy.types.Operator):
    bl_idname = "wm.gpt4_blender_assistant_text"
    bl_label = "Execute by Text"

    def execute(self, context):
        input_text = context.scene.gpt4_blender_assistant_input
        response = gpt4.get_gpt4_response(input_text)

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
        input_text = whisper.transcribe_audio()
        response = gpt4.get_gpt4_response(input_text)
        context.scene.gpt4_blender_assistant_output = response
        GPT4BlenderAssistantTextOperator.update_chat_log(self, context, input_text, response)

        try:
            exec(response, {"bpy": bpy, "context": context})
        except Exception as e:
            context.scene.gpt4_blender_assistant_output += "\n\nError: " + str(e)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(GPT4BlenderAssistantTextOperator)
    bpy.utils.register_class(GPT4BlenderAssistantVoiceOperator)

def unregister():
    bpy.utils.unregister_class(GPT4BlenderAssistantTextOperator)
    bpy.utils.unregister_class(GPT4BlenderAssistantVoiceOperator)

import bpy

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

def register():
    bpy.utils.register_class(GPT4ChatLogItem)
    bpy.utils.register_class(GPT4BlenderAssistantPanel)
    bpy.utils.register_class(GPT4ClearChatLogOperator)
    bpy.utils.register_class(GPT4CopyUserInputOperator)
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

def unregister():
    bpy.utils.unregister_class(GPT4ChatLogItem)
    bpy.utils.unregister_class(GPT4BlenderAssistantPanel)
    bpy.utils.unregister_class(GPT4ClearChatLogOperator)
    bpy.utils.unregister_class(GPT4CopyUserInputOperator)
    del bpy.types.Scene.gpt4_blender_assistant_input
    del bpy.types.Scene.gpt4_blender_assistant_output
    del bpy.types.Scene.gpt4_chat_log

if __name__ == "__main__":
    register

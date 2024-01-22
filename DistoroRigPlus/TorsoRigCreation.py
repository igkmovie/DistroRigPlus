import bpy
import mathutils
from . import RigPlus_Defs
from . import RigPlus_Data
from . import Property_Panel

class CreateTorsoRig(bpy.types.Operator):
    bl_idname = "object.createtorso_rig"
    bl_label = "Set Torso Rig Custom Shapes"
    bl_options = {'REGISTER', 'UNDO'}

    # Scale properties for each bone
    center_scale: bpy.props.FloatProperty(name="Center Scale", default=3)
    hips_scale: bpy.props.FloatProperty(name="Hips Scale", default=5)
    spine_scale: bpy.props.FloatProperty(name="Spine Scale", default=3)
    chest_scale: bpy.props.FloatProperty(name="Chest Scale", default=2.5)
    upper_chest_scale: bpy.props.FloatProperty(name="Upper Chest Scale", default=4)
    neck_scale: bpy.props.FloatProperty(name="Neck Scale", default=2)
    head_scale: bpy.props.FloatProperty(name="Head Scale", default=1)

    def execute(self, context):
        armature_name = "RigPlus"
        armature = bpy.data.objects.get(armature_name)
        
        if not armature:
            self.report({'ERROR'}, f"No armature named {armature_name} found!")
            return {'CANCELLED'}

        bone_scales = {
            "center": self.center_scale,
            "hips": self.hips_scale,
            "spine": self.spine_scale,
            "chest": self.chest_scale,
            "upper_chest": self.upper_chest_scale,
            "neck": self.neck_scale,
            "head": self.head_scale,
        }
        for bone, scale in bone_scales.items():
            if bone == "head":
                custom_shape = RigPlus_Defs.create_custom_shape("cube", scale)
                RigPlus_Defs.assign_bone_to_group(bone,Property_Panel.BoneGroups.BODY_HANDLE)
            elif bone == "center":
                custom_shape = RigPlus_Defs.create_custom_shape("plane", scale)
                RigPlus_Defs.assign_bone_to_group(bone,Property_Panel.BoneGroups.CENTER_HANDLE)
            else:
                custom_shape = RigPlus_Defs.create_custom_shape("circle", scale,"Y")
                RigPlus_Defs.assign_bone_to_group(bone,Property_Panel.BoneGroups.BODY_HANDLE)
            armature.pose.bones[bone].custom_shape = custom_shape

        #head_rotの作成(頭が正面を向く処理)
        bpy.ops.object.mode_set(mode='EDIT')
        head_rot_bone = armature.data.edit_bones.new("head_rot")
        # headボーンとneckボーンを取得
        head_bone = armature.data.edit_bones.get("head")
        neck_bone = armature.data.edit_bones.get("neck")
        # headボーンやneckボーンが存在しない場合、エラーメッセージを表示して終了
        if not head_bone or not neck_bone:
            print("Required bones (head or neck) not found!")
            return
        # Connectedをオフにする
        head_bone.use_connect = False
        neck_bone.use_connect = False
        # head_rotボーンの位置を設定
        head_rot_bone.head = head_bone.head
        head_rot_bone.tail = head_rot_bone.head + mathutils.Vector((0, 0.1, 0))
        # 親子関係を設定
        head_rot_bone.parent = neck_bone
        head_bone.parent = head_rot_bone
        # ポーズモードに切り替えてコンストレイントを追加
        bpy.ops.object.mode_set(mode='POSE')
        head_rot_pose_bone = armature.pose.bones["head_rot"]
        copy_rot_constraint = head_rot_pose_bone.constraints.new(type='COPY_ROTATION')
        copy_rot_constraint.target = bpy.data.objects["RigPlus"]
        copy_rot_constraint.subtarget = "center"
        copy_rot_constraint.target_space = 'WORLD'
        copy_rot_constraint.owner_space = 'WORLD'
        copy_rot_constraint.influence = 1.0


        # ポーズモードからオブジェクトモードに切り替え
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
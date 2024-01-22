import bpy
from bpy.types import Operator, Panel
import mathutils
from . import RigPlus_Defs
from . import Property_Panel
import math 


#ポーズモードですべてのボーンを表示する
def show_all_bones(armature_obj):

    # アーマチュアをアクティブにし、ポーズモードに切り替え
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    # すべてのボーンを表示
    for bone in armature_obj.data.bones:
        bone.hide = False
#つま先と踵のリグ
class OBJECT_OT_CreateToeHeelRig(bpy.types.Operator):
    bl_idname = "object.create_toe_heel_rig"
    bl_label = "Create Toe and Heel Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature_obj = context.object
        # Ensure the selected object is an Armature
        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected object must be an Armature.")
            return {'CANCELLED'}
        # Switch to Edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        armature = context.object.data
        edit_bones = armature.edit_bones

        root_bone = edit_bones.get('Root')
        if not root_bone:
            self.report({'ERROR'}, "No 'Root' bone found.")
            return {'CANCELLED'}

        # Helper function to set up the new bone based on an existing bone
        def setup_bone(new_bone_name, ref_bone, use_tail=False, offset=(0, 0.01, 0)):
            new_bone = edit_bones.new(new_bone_name)
            new_bone.head = ref_bone.tail if use_tail else ref_bone.head
            new_bone.tail.x = ref_bone.head.x
            new_bone.tail.y = ref_bone.head.y + offset[1]
            new_bone.tail.z = offset[2] if use_tail else ref_bone.head.z
            new_bone.parent = ref_bone
            new_bone.use_connect = False
            return new_bone

        # Create the necessary bones for each side
        for side in ['L', 'R']:
            bpy.ops.object.mode_set(mode='EDIT')
            foot_ik_name = f"{side}_foot_IK"
            foot_ik_p_name = f"{side}_foot_IK_P"
            heel_dummy_name = f"{side}_heel_dummy"
            toe_base_dummy_name = f"{side}_toeBase_dummy"
            toe_base_name = f"{side}_toeBase"
            foot_name = f"{side}_foot"
            foot_dummy_name = f"{side}_foot_dummy"
            foot_ik_target_name = f"{side}_foot_IK_target"
            footRot = f"{side}_footRot"
            lower_leg = f"{side}_lower_leg"
            toeBaseRot = f"{side}_toeBaseRot"


            # Check for the main IK bone or use the foot bone
            # ref_bone = edit_bones.get(foot_ik_name) or edit_bones.get(f"{side}_foot")
            ref_bone = edit_bones.get(foot_ik_name)
            ref_bone2 = edit_bones.get("L_hand_IK")
            if not ref_bone:
                RigPlus_Defs.show_popup("Please create the foot IK before proceeding with the creation/足IKを作成してから作成して下さい")
                return {'CANCELLED'}
                # self.report({'ERROR'}, f"Reference bone '{foot_ik_name}' or '{side}_foot' not found.")
            if not ref_bone2:
                RigPlus_Defs.show_popup("Please create the hand IK before proceeding with the creation/腕IKを作成してから作成して下さい")
                return {'CANCELLED'}


            # Create foot IK parent bone
            foot_ik_p_bone = edit_bones.new(foot_ik_p_name)
            foot_ik_bone = edit_bones.get(foot_ik_name)
            foot_ik_p_bone.head = foot_ik_bone.head
            foot_ik_p_bone.head.z = 0
            foot_ik_p_bone.tail = foot_ik_bone.tail
            foot_ik_p_bone.tail.z = 0
            foot_ik_p_bone.use_connect = False
            foot_ik_p_bone.parent = root_bone  # Parent to root bone

            # Create heel dummy bone
            heel_dummy_bone = setup_bone(heel_dummy_name, foot_ik_p_bone, use_tail=True)

            # Decide which bone to use as a reference for the toe base dummy bone
            ref_bone = edit_bones.get(toe_base_name) or ref_bone

            # Create toe base dummy bone
            toe_base_dummy_bone = setup_bone(toe_base_dummy_name, ref_bone, use_tail=True)
            toe_base_dummy_bone.parent = heel_dummy_bone  # Parent to heel dummy bone
            # SetUp foot_dummy_bone
            foot_bone = edit_bones.get(foot_name)
            foot_dummy_bone = edit_bones.get(foot_dummy_name)
            if not foot_dummy_bone:
                # If foot_dummy bone does not exist, create it
                foot_dummy_bone = edit_bones.new(foot_dummy_name)
            foot_dummy_bone.head = foot_bone.tail
            foot_dummy_bone.tail = foot_bone.head
            foot_dummy_bone.tail.z = 0  # Set Z position to 0
            foot_dummy_bone.parent = toe_base_dummy_bone  # Set parent to toe base dummy
            foot_dummy_bone.use_connect = False
            foot_dummy_bone.hide = False
            # Create IK target bones for L and R foot IK bones
            foot_ik_bone = edit_bones.get(foot_ik_name)
            if not foot_ik_bone:
                self.report({'ERROR'}, f"Foot IK bone '{foot_ik_name}' not found.")
                return {'CANCELLED'}
            foot_ik_target_bone = edit_bones.new(foot_ik_target_name)
            foot_ik_target_bone.head = foot_ik_bone.head
            foot_ik_target_bone.tail = foot_ik_bone.tail
            foot_ik_target_bone.use_connect = False
            foot_ik_target_bone.parent = foot_dummy_bone

            # Create footRot for L and R foot
            foot_bone = edit_bones.get(foot_name)
            foot_bone.use_connect = False
            footRot_bone = edit_bones.new(footRot)
            footRot_bone.head = foot_bone.head
            footRot_bone.tail = foot_bone.tail

            lower_leg_bone = edit_bones.get(lower_leg)
            footRot_bone.use_connect = False

            footRot_bone.parent = lower_leg_bone
            foot_bone.parent = footRot_bone
            # Create toeBaseRot for L and R toeBase
            toeBase_bone = edit_bones.get(toe_base_name)
            toeBaseRot_bone = edit_bones.new(toeBaseRot)
            toeBaseRot_bone.use_connect = False
            toeBaseRot_bone.head= toeBase_bone.head
            toeBaseRot_bone.tail = toeBase_bone.tail
            foot_bone = edit_bones.get(foot_name)
            toeBaseRot_bone.parent = foot_bone
            # root_bone = edit_bones.get("Root")
            # toeBase_bone.parent = root_bone
            toeBase_bone.use_connect = False
            toeBase_bone.parent = toeBaseRot_bone

        for side in ['L', 'R']:
            bpy.ops.object.mode_set(mode='POSE')
            foot_ik_name = f"{side}_foot_IK"
            foot_ik_p_name = f"{side}_foot_IK_P"
            heel_dummy_name = f"{side}_heel_dummy"
            toe_base_dummy_name = f"{side}_toeBase_dummy"
            toe_base_name = f"{side}_toeBase"
            foot_name = f"{side}_foot"
            foot_dummy_name = f"{side}_foot_dummy"
            foot_ik_target_name = f"{side}_foot_IK_target"
            footRot = f"{side}_footRot"
            lower_leg = f"{side}_lower_leg"
            toeBaseRot = f"{side}_toeBaseRot"

            footbone = armature_obj.pose.bones[foot_name]
            # コンストレイントを検索して非表示にする
            for constraint in footbone.constraints:
                if constraint.name == "Copy Transforms_rig":
                    constraint.mute = True

            # Copy Location Constraint
            foot_ik = armature_obj.pose.bones[foot_ik_name]
            foot_ik_target = armature_obj.pose.bones[foot_ik_target_name]
            copy_loc_constraint = foot_ik.constraints.new('COPY_LOCATION')
            copy_loc_constraint.target = armature_obj
            copy_loc_constraint.subtarget = foot_ik_target.name
            copy_loc_constraint.target_space = 'WORLD'
            copy_loc_constraint.owner_space = 'WORLD'
            # Damped Track Constraint
            foot_rot = armature_obj.pose.bones[footRot]
            foot_dummy = armature_obj.pose.bones[foot_dummy_name]
            damped_track_constraint = foot_rot.constraints.new('DAMPED_TRACK')
            damped_track_constraint.target = armature_obj
            damped_track_constraint.subtarget = foot_dummy.name
            damped_track_constraint.track_axis = 'TRACK_Y'

            toe_base_rot = armature_obj.pose.bones[toeBaseRot]
            toe_base_dummy = armature_obj.pose.bones[toe_base_dummy_name]
            damped_track_constraint = toe_base_rot.constraints.new('DAMPED_TRACK')
            damped_track_constraint.target = armature_obj
            damped_track_constraint.subtarget = toe_base_dummy.name
            damped_track_constraint.track_axis = 'TRACK_Y'
        
        #カスタムシェイプ設定
        for side in ['L', 'R']:
            bpy.ops.object.mode_set(mode='EDIT')
            foot_ik_p_name = f"{side}_foot_IK_P"
            heel_dummy_name = f"{side}_heel_dummy"
            toe_base_dummy_name = f"{side}_toeBase_dummy"
            L_foot_dummy_name = f"{side}_foot_dummy"
            custom_shape = RigPlus_Defs.create_custom_shape("cube", 1)
            RigPlus_Defs.assign_bone_to_group(foot_ik_p_name,Property_Panel.BoneGroups.IK_HANDLE)
            armature_obj.pose.bones[foot_ik_p_name].custom_shape = custom_shape
            custom_shape1 = RigPlus_Defs.create_custom_shape("sphere", 0.5)
            RigPlus_Defs.assign_bone_to_group(heel_dummy_name,Property_Panel.BoneGroups.CONTROLLER_HANDLE)
            armature_obj.pose.bones[heel_dummy_name].custom_shape = custom_shape1
            custom_shape2 = RigPlus_Defs.create_custom_shape("sphere", 0.5)
            RigPlus_Defs.assign_bone_to_group(toe_base_dummy_name,Property_Panel.BoneGroups.CONTROLLER_HANDLE)
            armature_obj.pose.bones[toe_base_dummy_name].custom_shape = custom_shape2
            custom_shape3 = RigPlus_Defs.create_custom_shape("sphere", 0.25)
            RigPlus_Defs.assign_bone_to_group(L_foot_dummy_name,Property_Panel.BoneGroups.CONTROLLER_HANDLE)
            armature_obj.pose.bones[L_foot_dummy_name].custom_shape = custom_shape3
        #指定したボーンを非表示にする
        bone_names = [
            f"{side}_{bone}"
            for side in ['L', 'R']
            for bone in ['footRot', 'toeBaseRot', 'foot_IK_target', 'foot_IK']
        ]
        for bone_name in bone_names:
            RigPlus_Defs.move_bone_to_last_layer_and_hide(armature_obj, bone_name)
        show_all_bones(armature_obj)

        # Switch back to Object mode at the end
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
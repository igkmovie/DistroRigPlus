import bpy
from bpy.types import Operator, Panel
import mathutils
from . import RigPlus_Defs
from . import Property_Panel
import math 

class CreateLegIKOperator(bpy.types.Operator):
    bl_idname = "object.create_leg_ik"
    bl_label = "Create Leg IK"

    def execute(self, context):
        armature_obj = bpy.data.objects.get("RigPlus")
        if armature_obj and armature_obj.type == 'ARMATURE':
            armature = armature_obj.data
            bpy.ops.object.mode_set(mode='POSE')

            # Remove constraints from specified bones
            bones_to_remove_constraints = ["R_foot", "R_lower_leg", "R_upper_leg", "L_foot", "L_lower_leg", "L_upper_leg"]
            for bone_name in bones_to_remove_constraints:
                bone = armature_obj.pose.bones.get(bone_name)
                if bone:
                    for constraint in bone.constraints:
                        bone.constraints.remove(constraint)
            bpy.ops.object.mode_set(mode='EDIT')

            leg_bones_sets = [
                ("R_foot", "R_lower_leg", "R_upper_leg", "hips"),
                ("L_foot", "L_lower_leg", "L_upper_leg", "hips")
            ]

            # Create IK bones for the legs
            for bone_names in leg_bones_sets:
                end_bone_name = bone_names[0]
                ik_bone_name = end_bone_name + "_IK"
                if ik_bone_name not in armature.edit_bones:
                    end_bone = armature.edit_bones.get(end_bone_name)
                    if end_bone:
                        new_bone = armature.edit_bones.new(ik_bone_name)
                        new_bone.head = end_bone.head
                        new_bone.tail = new_bone.head + mathutils.Vector((0, 0.1, 0))
                        new_bone.parent = armature.edit_bones["Root"]

            # Create dummy bones for the legs
            for bone_names in leg_bones_sets:
                end_bone_name, middle_bone_name, base_bone_name, root_name = bone_names
                dummy_bone_names = [name + "_dummy" for name in bone_names[:-1]]
                dummy_end_bone_name, dummy_middle_bone_name, dummy_base_bone_name = dummy_bone_names

                for original, dummy in zip(bone_names[:-1], dummy_bone_names):
                    original_bone = armature.edit_bones.get(original)
                    new_dummy_bone = armature.edit_bones.new(dummy)
                    new_dummy_bone.head = original_bone.head
                    new_dummy_bone.tail = original_bone.tail
                    new_dummy_bone.roll = original_bone.roll
                    new_dummy_bone.hide = True;

                armature.edit_bones[dummy_base_bone_name].parent = armature.edit_bones[root_name]
                armature.edit_bones[dummy_middle_bone_name].parent = armature.edit_bones[dummy_base_bone_name]
                armature.edit_bones[dummy_end_bone_name].parent = armature.edit_bones[dummy_middle_bone_name]

            leg_bones_sets = [
            ("R_foot", "R_lower_leg", "hips"),
            ("L_foot", "L_lower_leg", "hips")
            ]

            for bone_names in leg_bones_sets:
                end_bone_name, lower_leg_name, hips_name = bone_names
                pole_bone_name = end_bone_name + "_pole"
                
                # 1. ポールボーンを作成（L_foot_IKまたはR_foot_IKの位置とtailに設定）
                if pole_bone_name not in armature.edit_bones:
                    ik_bone_name = end_bone_name + "_IK"
                    ik_bone = armature.edit_bones.get(ik_bone_name)
                    if ik_bone:
                        pole_bone = armature.edit_bones.new(pole_bone_name)
                        pole_bone.head = ik_bone.head  # IKボーンの位置に設定
                        pole_bone.tail = ik_bone.tail  # IKボーンのtailの位置に設定
                        pole_bone.parent = None

                # 2. ポールボーンの親を設定
                if pole_bone_name in armature.edit_bones:
                    pole_bone = armature.edit_bones[pole_bone_name]
                    if ik_bone_name in armature.edit_bones:
                        pole_bone.parent = armature.edit_bones["Root"]

                # 3. ポールボーンの位置を設定（L_lower_legのheadの高さに設定）
                if pole_bone_name in armature.edit_bones:
                    pole_bone = armature.edit_bones[pole_bone_name]
                    lower_leg_bone = armature.edit_bones.get(lower_leg_name)
                    if pole_bone and lower_leg_bone:
                        pole_bone.head.z = lower_leg_bone.head.z
                        pole_bone.tail.z = lower_leg_bone.head.z
                        pole_bone.head.y = ik_bone.tail.y -0.25
                        pole_bone.tail.y = ik_bone.tail.y - 0.35  # -0.1を調整することで望む位置に設定

            # Switch to pose mode and add constraints
            bpy.ops.object.mode_set(mode='POSE')
            custom_shape = RigPlus_Defs.create_custom_shape("cube",1.0)
            custom_shapePole = RigPlus_Defs.create_custom_shape("cube",0.5)

            for bone_names in leg_bones_sets:
                middle_bone_name = bone_names[1]
                dummy_middle_bone_name = middle_bone_name + "_dummy"

                for bone_name in [middle_bone_name, dummy_middle_bone_name]:
                    bone = armature_obj.pose.bones.get(bone_name)
                    ik_bone_name = bone_names[0] + "_IK"
                    if bone and ik_bone_name in armature.bones:
                        ik_constraint = bone.constraints.new('IK')
                        ik_constraint.target = armature_obj
                        ik_constraint.subtarget = ik_bone_name
                        ik_constraint.chain_count = 2
                        ik_constraint.use_tail = True

                        # ポールターゲットを設定
                        pole_target_name = ""
                        if "L_lower_leg" in bone_name:
                            pole_target_name = "L_foot_pole"
                        elif "R_lower_leg" in bone_name:
                            pole_target_name = "R_foot_pole"

                        pole_target = armature_obj.pose.bones.get(pole_target_name)
                        if pole_target:
                            ik_constraint.pole_target = armature_obj
                            ik_constraint.pole_subtarget = pole_target_name
                            ik_constraint.pole_angle = math.radians(-90)

                        pbone = armature_obj.pose.bones[ik_bone_name]
                        pbone.custom_shape = custom_shape
                        RigPlus_Defs.assign_bone_to_group(ik_bone_name,Property_Panel.BoneGroups.IK_HANDLE)
                        pbone0 = armature_obj.pose.bones[pole_target_name]
                        pbone0.custom_shape = custom_shapePole
                        RigPlus_Defs.assign_bone_to_group(pole_target_name,Property_Panel.BoneGroups.POLE_HANDLE)

            # Add Inverse Kinematics Limit to specified bones
            bones_to_add_ik_limit = ["L_lower_leg", "R_lower_leg", "L_lower_leg_dummy", "R_lower_leg_dummy"]
            for bone_name in bones_to_add_ik_limit:
                bone = armature_obj.pose.bones.get(bone_name)
                if bone:
                    bone.use_ik_limit_x = True
                    bone.use_ik_limit_y = True
                    bone.use_ik_limit_z = True
                    bone.ik_min_x = math.radians(0)
                    bone.ik_max_x = math.radians(180)
                    bone.ik_min_y = math.radians(0)
                    bone.ik_max_y = math.radians(0)
                    bone.ik_min_z = math.radians(0)
                    bone.ik_max_z = math.radians(0)      

            bones_foots = ["L_foot", "R_foot"]
            for bone_name in bones_foots:
                bone = armature_obj.pose.bones.get(bone_name)
                if(bone_name == "L_foot"):
                    copy_bone = "L_foot_IK"
                else:
                    copy_bone = "R_foot_IK"
                copy_transform_constraint = bone.constraints.new('COPY_TRANSFORMS')
                copy_transform_constraint.target = armature_obj
                copy_transform_constraint.subtarget = copy_bone
                copy_transform_constraint.owner_space = 'LOCAL_WITH_PARENT'
                copy_transform_constraint.target_space = 'LOCAL_OWNER_ORIENT'
                copy_transform_constraint.influence = 0    
            RigPlus_Defs.hide_dummy_bones(armature_obj) 
            settings = context.scene.rigplus_settings
            if (settings.prop_vrm0 == True):
                RigPlus_Defs.apply_ik_settings_and_pole_angle("VROID", "Foot")
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "アクティブなオブジェクトがアーマチュアではありません")
            return {'CANCELLED'}
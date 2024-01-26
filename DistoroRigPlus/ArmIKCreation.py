import bpy
from bpy.types import Operator, Panel
import mathutils
from . import RigPlus_Defs
from . import Property_Panel
import math 
import json

class CreateWristIKOperator(Operator):
    bl_idname = "object.create_wrist_ik"
    bl_label = "腕IKを作成"

    def execute(self, context):
        armature_obj = bpy.data.objects.get("RigPlus")
        if armature_obj and armature_obj.type == 'ARMATURE':
            armature = armature_obj.data
            bpy.ops.object.mode_set(mode='EDIT')

            arm_bones_sets = [("R_hand", "R_lower_arm", "R_upper_arm", "R_shoulder"), 
                              ("L_hand", "L_lower_arm", "L_upper_arm", "L_shoulder")]

            for bone_names in arm_bones_sets:
                hand_bone_name = bone_names[0]
                ik_bone_name = hand_bone_name + "_IK"
                if ik_bone_name not in armature.edit_bones:
                    hand_bone = armature.edit_bones.get(hand_bone_name)
                    if hand_bone:
                        new_bone = armature.edit_bones.new(ik_bone_name)
                        new_bone.head = hand_bone.head
                        new_bone.tail = new_bone.head + mathutils.Vector((0, 0, -0.1))
                        new_bone.parent = armature.edit_bones["Root"]

            for bone_names in arm_bones_sets:
                hand_bone_name, lower_arm_name, upper_arm_name, shoulder_name = bone_names
                dummy_bone_names = [name + "_dummy" for name in bone_names[:-1]]
                dummy_hand_bone_name, dummy_lower_arm_name, dummy_upper_arm_name = dummy_bone_names

                for original, dummy in zip(bone_names[:-1], dummy_bone_names):
                    original_bone = armature.edit_bones.get(original)
                    new_dummy_bone = armature.edit_bones.new(dummy)
                    new_dummy_bone.head = original_bone.head
                    new_dummy_bone.tail = original_bone.tail
                    new_dummy_bone.roll = original_bone.roll
                    new_dummy_bone.hide = True;

                armature.edit_bones[dummy_upper_arm_name].parent = armature.edit_bones[shoulder_name]
                armature.edit_bones[dummy_lower_arm_name].parent = armature.edit_bones[dummy_upper_arm_name]
                armature.edit_bones[dummy_hand_bone_name].parent = armature.edit_bones[dummy_lower_arm_name]
            
            hand_bones_sets = [
            ("R_hand", "R_lower_arm", "hips"),
            ("L_hand", "L_lower_arm", "hips")
            ]

            for bone_names in hand_bones_sets:
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
                        pole_bone.head.x = lower_leg_bone.head.x
                        pole_bone.tail.x = lower_leg_bone.head.x
                        pole_bone.head.y = ik_bone.tail.y+ 0.2
                        pole_bone.tail.y = ik_bone.tail.y + 0.3  # 0.3を調整することで望む位置に設定
                        pole_bone.tail.z = pole_bone.head.z

            bpy.ops.object.mode_set(mode='POSE')
            custom_shape = RigPlus_Defs.create_custom_shape("cube",1)
            custom_shapePole = RigPlus_Defs.create_custom_shape("cube",0.5)
            
            for bone_name in ["L_lower_arm", "R_lower_arm","L_lower_arm_dummy","R_lower_arm_dummy"]:
                bone = armature_obj.pose.bones.get(bone_name)
                ik_target_name = ""
                if "L_lower_arm" in bone_name:
                        ik_target_name = "L_hand_IK"
                elif "R_lower_arm" in bone_name:
                        ik_target_name = "R_hand_IK"      
                if bone and ik_bone_name in armature.bones:
                    ik_constraint = bone.constraints.new('IK')
                    ik_constraint.target = armature_obj
                    ik_constraint.subtarget = ik_target_name
                    ik_constraint.chain_count = 2
                    ik_constraint.use_tail = True

                    # ポールターゲットを設定
                    pole_target_name = ""
                    if "L_lower_arm" in bone_name:
                        pole_target_name = "L_hand_pole"
                    elif "R_lower_arm" in bone_name:
                        pole_target_name = "R_hand_pole"

                    pole_target = armature_obj.pose.bones.get(pole_target_name)
                    if pole_target:
                        ik_constraint.pole_target = armature_obj
                        ik_constraint.pole_subtarget = pole_target_name
                        ik_constraint.pole_angle = math.radians(-90)

                pbone0 = armature_obj.pose.bones["L_hand_IK"]
                pbone0.custom_shape = custom_shape
                # print("test")
                RigPlus_Defs.assign_bone_to_group("L_hand_IK",Property_Panel.BoneGroups.IK_HANDLE)
                pbone1 = armature_obj.pose.bones["R_hand_IK"]
                pbone1.custom_shape = custom_shape
                RigPlus_Defs.assign_bone_to_group("R_hand_IK",Property_Panel.BoneGroups.IK_HANDLE)
                pbone2 = armature_obj.pose.bones["L_hand_pole"]
                pbone2.custom_shape = custom_shapePole
                RigPlus_Defs.assign_bone_to_group("L_hand_pole",Property_Panel.BoneGroups.POLE_HANDLE)
                pbone3 = armature_obj.pose.bones["R_hand_pole"]
                pbone3.custom_shape = custom_shapePole
                RigPlus_Defs.assign_bone_to_group("R_hand_pole",Property_Panel.BoneGroups.POLE_HANDLE)

            # Add Inverse Kinematics Limit to specified bones
            bones_to_add_ik_limit = ["L_lower_arm", "R_lower_arm", "L_lower_arm_dummy", "R_lower_arm_dummy"]
            for bone_name in bones_to_add_ik_limit:
                bone = armature_obj.pose.bones.get(bone_name)
                if bone:
                    bone.use_ik_limit_x = True
                    bone.use_ik_limit_y = False
                    bone.use_ik_limit_z = True
                    bone.ik_min_x = math.radians(0)
                    bone.ik_max_x = math.radians(180)
                    bone.ik_min_z = math.radians(0)
                    bone.ik_max_z = math.radians(0)
            bones_hands = ["L_hand", "R_hand",]
            for bone_name in bones_hands:
                if(bone_name == "L_hand"):
                    copy_bone = "L_hand_IK"
                else:
                    copy_bone = "R_hand_IK"
                bone = armature_obj.pose.bones.get(bone_name)
                copy_transform_constraint = bone.constraints.new('COPY_TRANSFORMS')
                copy_transform_constraint.target = armature_obj
                copy_transform_constraint.subtarget = copy_bone
                copy_transform_constraint.owner_space = 'LOCAL_WITH_PARENT'
                copy_transform_constraint.target_space = 'LOCAL_OWNER_ORIENT'
                copy_transform_constraint.influence = 0
                #腕IKのチャイルドコンストレイントを付ける
                hand_IK_bone = armature_obj.pose.bones.get(copy_bone)
                # チャイルドコンストレイントを追加
                child_constraint = hand_IK_bone.constraints.new('CHILD_OF')
                child_constraint.target = armature_obj
                child_constraint.subtarget = "upper_chest"
                child_constraint.influence = 0

            RigPlus_Defs.hide_dummy_bones(armature_obj)
            hand_sets = ["R_hand","L_hand"]
            for hand in hand_sets:
                RigPlus_Defs.assign_bone_to_group(hand, Property_Panel.BoneGroups.BODY_HANDLE)
                custom = RigPlus_Defs.create_custom_shape("circle",3,"Y")
                pbonehand = armature_obj.pose.bones[hand]
                pbonehand.custom_shape = custom
            settings = context.scene.rigplus_settings
            if (settings.prop_vrm0 == True):
                RigPlus_Defs.apply_ik_settings_and_pole_angle("VROID", "Hand")
            elif(settings.prop_pmx == True):
                RigPlus_Defs.apply_ik_settings_and_pole_angle("MMD", "Hand")
            # 必要なオブジェクトを取得
            armature_obj = bpy.data.objects.get("RigPlus")
            # アーマチュアが存在し、正しいタイプであることを確認
            if armature_obj and armature_obj.type == 'ARMATURE':
                # アーマチュアをアクティブオブジェクトとして設定
                bpy.context.view_layer.objects.active = armature_obj
                # アーマチュアを選択状態にする
                armature_obj.select_set(True)
                # オブジェクトモードに切り替える
                bpy.ops.object.mode_set(mode='EDIT')
            #IKが動くようにするために若干Y方向へボーンを動かす
            bpy.ops.object.mode_set(mode='EDIT')
            # アーマチュアの編集ボーンを取得
            edit_bones = armature_obj.data.edit_bones
            bones_move = ["L_lower_arm","L_lower_arm_dummy", "R_lower_arm","R_lower_arm_dummy", "L_upper_arm","L_upper_arm_dummy", "R_upper_arm","R_upper_arm_dummy"]
            for bone_name in bones_move:
                bone = edit_bones.get(bone_name)
                if bone:
                    # ボーン名に 'lower' が含まれる場合、head を動かす
                    if 'lower' in bone_name:
                        bone.head[1] += 0.005  # headをY軸方向に0.005移動
                    # ボーン名に 'upper' が含まれる場合、tail を動かす
                    elif 'upper' in bone_name:
                        bone.tail[1] += 0.005  # tailをY軸方向に0.005移動
                else:
                    print(f"{bone_name} という名前のボーンが見つかりません。")
            
            # 編集モードを終了
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "アクティブなオブジェクトがアーマチュアではありません")
            return {'CANCELLED'}
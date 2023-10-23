bl_info = {
    "name": "DistroRigPlus",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
from bpy.types import Operator, Panel
import mathutils
import math 

def hide_dummy_bones(active_object):
    # アクティブなオブジェクトが存在しない場合、エラーメッセージを表示
    if active_object is None:
        print("アクティブなオブジェクトが存在しません")
        return

    # ポーズモードに切り替え
    bpy.context.view_layer.objects.active = active_object
    bpy.ops.object.mode_set(mode='POSE')

    # ポーズモードで非表示にしたいボーン名の一部
    target_bone_name_part = "_dummy"

    # ポーズモードのすべてのボーンを対象にする
    for bone in active_object.pose.bones:
        # ボーン名に指定した文字列が含まれている場合、ボーンを非表示にする
        if target_bone_name_part in bone.name:
            bone.bone.hide = True

def create_custom_shape():
    # 新しいコレクション "WGT" を作成
    if "WGT" not in bpy.data.collections:
        wgt_collection = bpy.data.collections.new("WGT")
        bpy.context.scene.collection.children.link(wgt_collection)
    else:
        wgt_collection = bpy.data.collections["WGT"]

    # カスタムシェイプオブジェクトを作成
    bpy.ops.mesh.primitive_cube_add(size=0.5)
    custom_shape = bpy.context.active_object
    custom_shape.name = "WGT-Bone_cube"

    # カスタムシェイプオブジェクトを "WGT" コレクションに追加
    wgt_collection.objects.link(custom_shape)
    # カスタムシェイプをデフォルトのシーンコレクションから削除
    bpy.context.collection.objects.unlink(custom_shape)

    # カスタムシェイプオブジェクトを非表示に設定
    custom_shape.hide_viewport = True

    return custom_shape

def draw_bone_constraints(context, layout):
    armature_obj = context.active_object
    if armature_obj:
        lowArm_names =["R_lower_arm", "L_lower_arm"]
        row = layout.row()
        row.label(text="IK_ON/OFF",icon='CONSTRAINT_BONE')
        for bone_name in lowArm_names:
            bone = armature_obj.pose.bones.get(bone_name)

            if bone:
                for constraint in bone.constraints:
                    # IK制約のinfluenceをコントロールするスライダーを追加
                    if(bone_name == "R_lower_arm"):
                        displayName = "R_hand"
                    else:
                        displayName = "L_hand"

                    if constraint.type == 'IK':
                        row = layout.row()
                        row.label(text=displayName)
                        row.prop(constraint, "influence", slider=True)
        bone_names = ["R_hand", "L_hand"]
        row = layout.row()
        row.label(text="腕切IK_ON/OFF",icon='CONSTRAINT_BONE')
        for bone_name in bone_names:
            bone = armature_obj.pose.bones.get(bone_name)
            if bone:
                for constraint in bone.constraints:             
                    # COPY_TRANSFORMS制約のinfluenceをコントロールするスライダーを追加
                    if(bone_name == "R_hand"):
                        displayName = "R_hand"
                    else:
                        displayName = "L_hand"
                    if constraint.type == 'COPY_TRANSFORMS':
                        row = layout.row()
                        row.label(text=displayName)
                        row.prop(constraint, "influence", slider=True)

def draw_leg_constraints(context, layout):
    armature_obj = context.active_object
    if armature_obj:
        lowleg_names =["R_lower_leg", "L_lower_leg"]
        row = layout.row()
        row.label(text="IK_ON/OFF",icon='CONSTRAINT_BONE')
        for bone_name in lowleg_names:
            bone = armature_obj.pose.bones.get(bone_name)
            if bone:
                for constraint in bone.constraints:
                    if(bone_name == "R_lower_leg"):
                        displayName = "R_foot"
                    else:
                        displayName = "L_foot"
                    # IK制約のinfluenceをコントロールするスライダーを追加
                    if constraint.type == 'IK':
                        row = layout.row()
                        row.label(text=displayName)
                        row.prop(constraint, "influence", slider=True)
        bone_names = ["R_foot", "L_foot"]
        row = layout.row()
        row.label(text="足切IK_ON/OFF",icon='CONSTRAINT_BONE')
        for bone_name in bone_names:
            bone = armature_obj.pose.bones.get(bone_name)
            if bone:
                for constraint in bone.constraints:                 
                    # COPY_TRANSFORMS制約のinfluenceをコントロールするスライダーを追加
                    if(bone_name == "R_foot"):
                        displayName = "R_foot"
                    else:
                        displayName = "L_foot"
                    if constraint.type == 'COPY_TRANSFORMS':
                        row = layout.row()
                        row.label(text=displayName)
                        row.prop(constraint, "influence", slider=True)



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
                        new_bone.parent = None

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
                    ik_bone_name = end_bone_name + "_IK"
                    if ik_bone_name in armature.edit_bones:
                        pole_bone.parent = armature.edit_bones[ik_bone_name]

                # 3. ポールボーンの位置を設定（L_lower_legのheadの高さに設定）
                if pole_bone_name in armature.edit_bones:
                    pole_bone = armature.edit_bones[pole_bone_name]
                    lower_leg_bone = armature.edit_bones.get(lower_leg_name)
                    if pole_bone and lower_leg_bone:
                        pole_bone.head.x = lower_leg_bone.head.x
                        pole_bone.tail.x = lower_leg_bone.head.x
                        pole_bone.head.y = ik_bone.tail.y- 0.1
                        pole_bone.tail.y = ik_bone.tail.y - 0.2  # -0.1を調整することで望む位置に設定
                        pole_bone.tail.z = pole_bone.head.z

            bpy.ops.object.mode_set(mode='POSE')
            custom_shape = create_custom_shape()
            
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
                        ik_constraint.pole_angle = math.radians(90)

                pbone0 = armature_obj.pose.bones["L_hand_IK"]
                pbone0.custom_shape = custom_shape
                pbone1 = armature_obj.pose.bones["R_hand_IK"]
                pbone1.custom_shape = custom_shape
                pbone2 = armature_obj.pose.bones["L_hand_pole"]
                pbone2.custom_shape = custom_shape
                pbone3 = armature_obj.pose.bones["R_hand_pole"]
                pbone3.custom_shape = custom_shape

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
            hide_dummy_bones(armature_obj)    
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "アクティブなオブジェクトがアーマチュアではありません")
            return {'CANCELLED'}
        
class MakeRigOperator(bpy.types.Operator):
    bl_idname = "object.make_rig"
    bl_label = "Make Rig"
    
    def execute(self, context):
        # 選択中のオブジェクトを取得
        selected_obj = context.active_object
        
        if selected_obj and selected_obj.type == 'ARMATURE':
            # 選択中のアーマチュアをコピーしてrigという名前で新しいアーマチュアを作成
            bpy.ops.object.duplicate()
            bpy.context.active_object.name = "RigPlus"
            rig = bpy.context.active_object
            
            # アーマチュアのボーンをポーズモードに切り替え
            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.mode_set(mode='POSE')
            
            # originalのボーンとrigのボーンを対応付けてコンストレイントを追加
            for bone in selected_obj.pose.bones:
                constraint = bone.constraints.new(type='COPY_TRANSFORMS')
                constraint.target = rig  # rigアーマチュアをターゲットにする
                constraint.subtarget = bone.name
                # ターゲットのボーンも設定
                constraint.target_space = 'WORLD'
                constraint.owner_space = 'WORLD'
            
            # ポーズモードからオブジェクトモードに切り替え
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.report({'INFO'}, "Rig created and constraints added.")
        else:
            self.report({'ERROR'}, "Please select an armature in Object Mode.")
        
        return {'FINISHED'}
    
import bpy
import mathutils

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
                        new_bone.tail = new_bone.head + mathutils.Vector((0, 0, -0.1))
                        new_bone.parent = None

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
                    ik_bone_name = end_bone_name + "_IK"
                    if ik_bone_name in armature.edit_bones:
                        pole_bone.parent = armature.edit_bones[ik_bone_name]

                # 3. ポールボーンの位置を設定（L_lower_legのheadの高さに設定）
                if pole_bone_name in armature.edit_bones:
                    pole_bone = armature.edit_bones[pole_bone_name]
                    lower_leg_bone = armature.edit_bones.get(lower_leg_name)
                    if pole_bone and lower_leg_bone:
                        pole_bone.head.z = lower_leg_bone.head.z
                        pole_bone.tail.z = lower_leg_bone.head.z
                        pole_bone.head.y = ik_bone.tail.y
                        pole_bone.tail.y = ik_bone.tail.y - 0.1  # -0.1を調整することで望む位置に設定

            # Switch to pose mode and add constraints
            bpy.ops.object.mode_set(mode='POSE')
            custom_shape = create_custom_shape()

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
                        pbone0 = armature_obj.pose.bones[pole_target_name]
                        pbone0.custom_shape = custom_shape

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
            hide_dummy_bones(armature_obj) 
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "アクティブなオブジェクトがアーマチュアではありません")
            return {'CANCELLED'}
class IK2FKRightOperator(bpy.types.Operator):
    bl_idname = "pose.ik_to_fk_right"
    bl_label = "IK to FK (Right Arm)"
    bl_options = {'REGISTER', 'UNDO'}

    def set_translation(self, bone, loc):
        mat = bone.matrix.copy()
        mat[0][3] = loc[0]
        mat[1][3] = loc[1]
        mat[2][3] = loc[2]
        bone.matrix = mat

    def ik2fk(self,target, pole, upper_fk, fore_fk):
        self.set_translation(target, fore_fk.tail)
        self.set_translation(pole, upper_fk.tail)

    def execute(self, context):
        pose_bones = context.active_object.pose.bones
        upper_fk_r = pose_bones.get('R_upper_arm')
        fore_fk_r = pose_bones.get('R_lower_arm')
        target_r = pose_bones.get('R_hand_IK')
        pole_r = pose_bones.get('R_hand_pole')
        upper_Ik_r = pose_bones.get('R_upper_arm_dummy')

        if upper_fk_r and fore_fk_r and target_r and pole_r:
            ik2fk_Hand(context, target_r, pole_r, upper_fk_r, fore_fk_r,upper_Ik_r)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "右腕のボーンが見つかりません")
            return {'CANCELLED'}

class IK2FKLeftOperator(bpy.types.Operator):
    bl_idname = "pose.ik_to_fk_left"
    bl_label = "IK to FK (Left Arm)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pose_bones = context.active_object.pose.bones
        upper_fk_l = pose_bones.get('L_upper_arm')
        fore_fk_l = pose_bones.get('L_lower_arm')
        target_l = pose_bones.get('L_hand_IK')
        pole_l = pose_bones.get('L_hand_pole')
        upper_Ik_l = pose_bones.get('L_upper_arm_dummy')

        if upper_fk_l and fore_fk_l and target_l and pole_l:
            ik2fk_Hand(context, target_l, pole_l, upper_fk_l, fore_fk_l,upper_Ik_l)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "左腕のボーンが見つかりません")
            return {'CANCELLED'}
        
def ik2fk_Hand(context,target, pole, upper_fk, fore_fk,upper_Ik):
    amt = bpy.context.object
    set_translation(target, fore_fk.tail)
    upper_fk_global_location = amt.matrix_world @ amt.pose.bones[upper_fk.name].tail
    context.scene.cursor.location = upper_fk_global_location;
    for bone in amt.data.bones:
        bone.select = False
    amt.pose.bones[pole.name].bone.select = True
    bpy.ops.view3d.snap_selected_to_cursor(False)
    upper_Ik_l_global_location = amt.matrix_world @ amt.pose.bones[upper_Ik.name].tail
    context.scene.cursor.location = upper_Ik_l_global_location
    for bone in amt.data.bones:
        bone.select = False
    amt.pose.bones[pole.name].bone.select = True
    bpy.ops.view3d.snap_selected_to_cursor(False)
    pole.location.z = pole.location.z+0.01

# 右腕のIKからFKへの情報のコピーを行うオペレーター
class CopyIKtoFKRightOperator(bpy.types.Operator):
    bl_idname = "pose.copy_ik_to_fk_right"
    bl_label = "Copy Right Arm IK to FK"

    def copy_bone_transform(self, fk_bone, ik_bone):
        # IKボーンの情報をFKボーンにコピー
        fk_bone.matrix = ik_bone.matrix
        # ボーンの更新
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')

    def execute(self, context):
        # アクティブなオブジェクトを取得
        active_object = bpy.context.active_object
        if active_object and active_object.type == 'ARMATURE':
            pose_bones = active_object.pose.bones

            # ボーン名を指定
            upper_arm_fk_bone_name = "R_upper_arm"
            lower_arm_fk_bone_name = "R_lower_arm"
            upper_arm_ik_bone_name = "R_upper_arm_dummy"
            lower_arm_ik_bone_name = "R_lower_arm_dummy"

            # IKからFKへの情報のコピー
            if (
                upper_arm_fk_bone_name in pose_bones
                and lower_arm_fk_bone_name in pose_bones
                and upper_arm_ik_bone_name in pose_bones
                and lower_arm_ik_bone_name in pose_bones
            ):
                upper_arm_fk = pose_bones[upper_arm_fk_bone_name]
                lower_arm_fk = pose_bones[lower_arm_fk_bone_name]
                upper_arm_ik = pose_bones[upper_arm_ik_bone_name]
                lower_arm_ik = pose_bones[lower_arm_ik_bone_name]

                # ボーンの情報をコピー
                self.copy_bone_transform(upper_arm_fk, upper_arm_ik)
                self.copy_bone_transform(lower_arm_fk, lower_arm_ik)

        return {'FINISHED'}
# 左腕のIKからFKへの情報のコピーを行うオペレーター
class CopyIKtoFKLeftOperator(bpy.types.Operator):
    bl_idname = "pose.copy_ik_to_fk_left"
    bl_label = "Copy Left Arm IK to FK"

    def copy_bone_transform(self, fk_bone, ik_bone):
        # IKボーンの情報をFKボーンにコピー
        fk_bone.matrix = ik_bone.matrix
        # ボーンの更新
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')

    def execute(self, context):
        # アクティブなオブジェクトを取得
        active_object = bpy.context.active_object
        if active_object and active_object.type == 'ARMATURE':
            pose_bones = active_object.pose.bones

            # ボーン名を指定
            upper_arm_fk_bone_name = "L_upper_arm"
            lower_arm_fk_bone_name = "L_lower_arm"
            upper_arm_ik_bone_name = "L_upper_arm_dummy"
            lower_arm_ik_bone_name = "L_lower_arm_dummy"

            # IKからFKへの情報のコピー
            if (
                upper_arm_fk_bone_name in pose_bones
                and lower_arm_fk_bone_name in pose_bones
                and upper_arm_ik_bone_name in pose_bones
                and lower_arm_ik_bone_name in pose_bones
            ):
                upper_arm_fk = pose_bones[upper_arm_fk_bone_name]
                lower_arm_fk = pose_bones[lower_arm_fk_bone_name]
                upper_arm_ik = pose_bones[upper_arm_ik_bone_name]
                lower_arm_ik = pose_bones[lower_arm_ik_bone_name]

                # ボーンの情報をコピー
                self.copy_bone_transform(upper_arm_fk, upper_arm_ik)
                self.copy_bone_transform(lower_arm_fk, lower_arm_ik)

        return {'FINISHED'}
    
# 右脚のIKからFKへの情報のコピーを行うオペレーター
class CopyRightLegIKtoFKOperator(bpy.types.Operator):
    bl_idname = "pose.copy_right_leg_ik_to_fk"
    bl_label = "Copy Right Leg IK to FK"

    def copy_bone_transform(self, fk_bone, ik_bone):
        # IKボーンの情報をFKボーンにコピー
        fk_bone.matrix = ik_bone.matrix
        # ボーンの更新
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')

    def execute(self, context):
        # アクティブなオブジェクトを取得
        active_object = bpy.context.active_object
        if active_object and active_object.type == 'ARMATURE':
            pose_bones = active_object.pose.bones

            # ボーン名を指定
            upper_leg_fk_bone_name = "R_upper_leg"
            lower_leg_fk_bone_name = "R_lower_leg"
            upper_leg_ik_bone_name = "R_upper_leg_dummy"
            lower_leg_ik_bone_name = "R_lower_leg_dummy"

            # IKからFKへの情報のコピー
            if (
                upper_leg_fk_bone_name in pose_bones
                and lower_leg_fk_bone_name in pose_bones
                and upper_leg_ik_bone_name in pose_bones
                and lower_leg_ik_bone_name in pose_bones
            ):
                upper_leg_fk = pose_bones[upper_leg_fk_bone_name]
                lower_leg_fk = pose_bones[lower_leg_fk_bone_name]
                upper_leg_ik = pose_bones[upper_leg_ik_bone_name]
                lower_leg_ik = pose_bones[lower_leg_ik_bone_name]

                # ボーンの情報をコピー
                self.copy_bone_transform(upper_leg_fk, upper_leg_ik)
                self.copy_bone_transform(lower_leg_fk, lower_leg_ik)

        return {'FINISHED'}


# 左脚のIKからFKへの情報のコピーを行うオペレーター
class CopyLeftLegIKtoFKOperator(bpy.types.Operator):
    bl_idname = "pose.copy_left_leg_ik_to_fk"
    bl_label = "Copy Left Leg IK to FK"

    def copy_bone_transform(self, fk_bone, ik_bone):
        # IKボーンの情報をFKボーンにコピー
        fk_bone.matrix = ik_bone.matrix
        # ボーンの更新
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')
    
    def execute(self, context):
        # アクティブなオブジェクトを取得
        active_object = bpy.context.active_object
        if active_object and active_object.type == 'ARMATURE':
            pose_bones = active_object.pose.bones

            # ボーン名を指定
            upper_leg_fk_bone_name = "L_upper_leg"
            lower_leg_fk_bone_name = "L_lower_leg"
            upper_leg_ik_bone_name = "L_upper_leg_dummy"
            lower_leg_ik_bone_name = "L_lower_leg_dummy"

            # IKからFKへの情報のコピー
            if (
                upper_leg_fk_bone_name in pose_bones
                and lower_leg_fk_bone_name in pose_bones
                and upper_leg_ik_bone_name in pose_bones
                and lower_leg_ik_bone_name in pose_bones
            ):
                upper_leg_fk = pose_bones[upper_leg_fk_bone_name]
                lower_leg_fk = pose_bones[lower_leg_fk_bone_name]
                upper_leg_ik = pose_bones[upper_leg_ik_bone_name]
                lower_leg_ik = pose_bones[lower_leg_ik_bone_name]

                # ボーンの情報をコピー
                self.copy_bone_transform(upper_leg_fk, upper_leg_ik)
                self.copy_bone_transform(lower_leg_fk, lower_leg_ik)

        return {'FINISHED'}
    


class IK2FKRightLegOperator(bpy.types.Operator):
    bl_idname = "pose.ik_to_fk_right_leg"
    bl_label = "IK to FK (Right Leg)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pose_bones = context.active_object.pose.bones
        upper_fk_r = pose_bones.get('R_upper_leg')
        fore_fk_r = pose_bones.get('R_lower_leg')
        target_r = pose_bones.get('R_foot_IK')
        pole_r = pose_bones.get('R_foot_pole')

        if upper_fk_r and fore_fk_r and target_r and pole_r:
            ik2fk(context, target_r, pole_r, upper_fk_r, fore_fk_r)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "右足のボーンが見つかりません")
            return {'CANCELLED'}
        
class IK2FKLeftLegOperator(bpy.types.Operator):
    bl_idname = "pose.ik_to_fk_left_leg"
    bl_label = "IK to FK (Left Leg)"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        pose_bones = context.active_object.pose.bones
        upper_fk_l = pose_bones.get('L_upper_leg')
        fore_fk_l = pose_bones.get('L_lower_leg')
        target_l = pose_bones.get('L_foot_IK')
        pole_l = pose_bones.get('L_foot_pole')

        if upper_fk_l and fore_fk_l and target_l and pole_l:
            ik2fk(context,target_l, pole_l, upper_fk_l, fore_fk_l)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "左足のボーンが見つかりません")
            return {'CANCELLED'}
        
def ik2fk(context,target, pole, upper_fk, fore_fk):
    amt = bpy.context.object
    set_translation(target, fore_fk.tail)
    upper_fk_global_location = amt.matrix_world @ amt.pose.bones[upper_fk.name].tail
    context.scene.cursor.location = upper_fk_global_location;
    for bone in amt.data.bones:
        bone.select = False
    amt.pose.bones[pole.name].bone.select = True
    bpy.ops.view3d.snap_selected_to_cursor(False)

def set_translation(bone, loc):
    mat = bone.matrix.copy()
    mat[0][3] = loc[0]
    mat[1][3] = loc[1]
    mat[2][3] = loc[2]
    bone.matrix = mat

# 1. Define a custom property group
class IKToolSettings(bpy.types.PropertyGroup):
    show_arm_ik: bpy.props.BoolProperty(
        name="Show 腕IKSetting",
        description="Toggle visibility of 腕IK作成 section",
        default=True
    )
    show_leg_ik: bpy.props.BoolProperty(
        name="Show 足IKSettig",
        description="Toggle visibility of 足IK作成 section",
        default=True
    )


class IKToolPanel(bpy.types.Panel):
    bl_label = "DistroRigPlus"
    bl_idname = "OBJECT_PT_ik_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DistroRigPlus'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ik_tool_settings

        # Rigを作成
        box = layout.box()
        box.label(text="Rig Tools:", icon='ARMATURE_DATA')
        box.operator("object.make_rig", text="Rigを作成")
        # Checkbox for toggling visibility
        layout.prop(settings, "show_arm_ik")
        if settings.show_arm_ik:
            # Draw 腕IK作成 section
            box = layout.box()
            box.label(text="腕IK作成:", icon='CONSTRAINT_BONE')
            box.operator("object.create_wrist_ik", text="腕IK作成")
            draw_bone_constraints(context, box)
            box.label(text="Right Arm:", icon='CONSTRAINT_BONE')
            box.operator("pose.ik_to_fk_right", text="IK to FK βver")
            box.operator("pose.copy_ik_to_fk_right", text="FK to IK")
            box.label(text="Left Arm:", icon='CONSTRAINT_BONE')
            box.operator("pose.ik_to_fk_left", text="IK to FK βver")
            box.operator("pose.copy_ik_to_fk_left", text="FK to IK")

        layout.prop(settings, "show_leg_ik")
        if settings.show_leg_ik:
            # Draw 足IK作成 section
            box = layout.box()
            box.label(text="足IK Tools:", icon='CONSTRAINT_BONE')
            box.operator("object.create_leg_ik", text="足IK作成")
            draw_leg_constraints(context, box)
            box.label(text="Right leg:", icon='CONSTRAINT_BONE')
            box.operator("pose.ik_to_fk_right_leg", text="IK to FK βver")
            box.operator("pose.copy_right_leg_ik_to_fk", text="FK to IK")
            box.label(text="Left leg:", icon='CONSTRAINT_BONE')
            box.operator("pose.ik_to_fk_left_leg", text="IK to FK βver")
            box.operator("pose.copy_left_leg_ik_to_fk", text="FK to IK ")

def register():
    bpy.utils.register_class(CreateLegIKOperator)
    bpy.utils.register_class(CreateWristIKOperator)
    bpy.utils.register_class(MakeRigOperator)
    bpy.utils.register_class(IK2FKRightOperator)
    bpy.utils.register_class(IK2FKLeftOperator)
    bpy.utils.register_class(CopyIKtoFKLeftOperator)
    bpy.utils.register_class(CopyIKtoFKRightOperator)

    bpy.utils.register_class(CopyLeftLegIKtoFKOperator)
    bpy.utils.register_class(CopyRightLegIKtoFKOperator)
    bpy.utils.register_class(IK2FKLeftLegOperator)
    bpy.utils.register_class(IK2FKRightLegOperator)
    bpy.utils.register_class(IKToolSettings)
    bpy.utils.register_class(IKToolPanel)
    bpy.types.Scene.ik_tool_settings = bpy.props.PointerProperty(type=IKToolSettings)

def unregister():
    bpy.utils.unregister_class(CreateLegIKOperator)
    bpy.utils.unregister_class(MakeRigOperator)
    bpy.utils.unregister_class(CreateWristIKOperator)
    bpy.utils.unregister_class(IK2FKRightOperator)
    bpy.utils.unregister_class(IK2FKLeftOperator)
    bpy.utils.unregister_class(CopyIKtoFKLeftOperator)
    bpy.utils.unregister_class(CopyIKtoFKRightOperator)

    bpy.utils.unregister_class(CopyLeftLegIKtoFKOperator)
    bpy.utils.unregister_class(CopyRightLegIKtoFKOperator)
    bpy.utils.unregister_class(IK2FKLeftLegOperator)
    bpy.utils.unregister_class(IK2FKRightLegOperator)
    del bpy.types.Scene.ik_tool_settings
    bpy.utils.unregister_class(IKToolPanel)
    bpy.utils.unregister_class(IKToolSettings)

if __name__ == "__main__":
    register()

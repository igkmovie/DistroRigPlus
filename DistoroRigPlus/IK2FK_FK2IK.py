import bpy

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
            ik2fk(context, target_r, pole_r, upper_fk_r, fore_fk_r)
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
        
#IKをFKにする計算もメソッド     
def ik2fk_Hand(context,target, pole, upper_fk, fore_fk,upper_Ik):
    amt = bpy.context.object
    set_translation(target, fore_fk.tail)
    upper_fk_global_location = amt.matrix_world @ amt.pose.bones[upper_fk.name].tail
    context.scene.cursor.location = upper_fk_global_location;
    for bone in amt.data.bones:
        bone.select = False
    amt.pose.bones[pole.name].bone.select = True
    bpy.ops.view3d.snap_selected_to_cursor(False)
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
#右足IKをFKにするパネル
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
#左足IKをFKにするパネル        
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
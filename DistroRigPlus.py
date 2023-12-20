bl_info = {
    "name": "DistroRigPlus",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
from bpy.types import Operator, Panel
import mathutils
import math 
from enum import Enum

#とりあえずHairのボーンとHairのコンストレイントを削除するメソッドを作成、いずれ消す
def modify_bones_with_string(armature_name="RigPlus", target_string="hair"):
    # アーマチュアを取得
    armature = bpy.data.objects.get(armature_name)
    
    # アーマチュアが存在しない場合、エラーメッセージを表示して終了
    if not armature:
        print(f"No armature named {armature_name} found!")
        return

    # エディットモードに切り替え
    bpy.context.view_layer.objects.active = armature

    if armature_name == "RigPlus":
        bpy.ops.object.mode_set(mode='EDIT')
        # 指定された文字列を含むボーンを検索して削除
        bones_to_delete = [bone for bone in armature.data.edit_bones if target_string in bone.name]
        for bone in bones_to_delete:
            armature.data.edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        bpy.ops.object.mode_set(mode='POSE')
        # 指定された文字列を含むボーンを検索してコンストレイントを削除
        bones_to_clear_constraints = [bone for bone in armature.pose.bones if target_string in bone.name]
        for bone in bones_to_clear_constraints:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
        bpy.ops.object.mode_set(mode='OBJECT')

# 指定したアーマチュアのすべてのボーンのコンストレイントを非表示にするメソッド
# ただし、コンストレイントの名前にexclude_stringが含まれている場合は非表示にしない
def hide_constraints_of_armature(armature_name="RigPlus", exclude_string="_rig"):
    # アーマチュアを取得
    armature = bpy.data.objects.get(armature_name)
    
    # アーマチュアが存在しない場合、エラーメッセージを表示して終了
    if not armature:
        print(f"No armature named {armature_name} found!")
        return
    
    # ポーズモードに切り替え
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    # すべてのボーンのコンストレイントを非表示にする
    # ただし、コンストレイントの名前に exclude_string が含まれている場合は除外
    for bone in armature.pose.bones:
        for constraint in bone.constraints:
            if exclude_string not in constraint.name:
                constraint.mute = True

    bpy.ops.object.mode_set(mode='OBJECT')


def create_colored_bone_groups(active_obj):
    """
    active_obj: 対象のArmatureオブジェクト
    この関数は、指定の名前と色でボーングループを作成します。
    """
    if active_obj.type != 'ARMATURE':
        print("The provided object is not an armature.")
        return

    # Edit modeに切り替え
    bpy.context.view_layer.objects.active = active_obj
    bpy.ops.object.mode_set(mode='EDIT')

    bone_group_data = {
        'IK_handle': (0.0, 0.0, 1.0),  # 青色
        'Pole_handle': (1.0, 1.0, 0.0),  # 黄色
        'body_handle': (1.0, 0.5, 0.0),  # オレンジ色
        'center_handle': (0.5, 0.0, 0.5),  # 紫色
        'controller_handle': (0.0, 1.0, 0.0)  # 緑色
    }
    for name, color in bone_group_data.items():
        if name not in active_obj.pose.bone_groups:
            bg = active_obj.pose.bone_groups.new(name=name)
            bg.color_set = 'CUSTOM'
            bg.colors.normal = color
    bpy.ops.object.mode_set(mode='OBJECT')
            
def assign_bone_to_group(bone_name, bone_group_enum):
    # 'RigPlus'という名前のアーマチュアを取得
    armature = bpy.data.objects.get("RigPlus")
    
    if not armature or armature.type != 'ARMATURE':
        print("'RigPlus'という名前のアーマチュアが見つかりません。")
        return

    # アーマチュアをアクティブに設定
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)

    # ポーズモードに切り替える
    bpy.ops.object.mode_set(mode='POSE')
    
    # ボーングループの存在を確認
    if bone_group_enum.value not in armature.pose.bone_groups:
        print(f"{bone_group_enum.value} という名前のボーングループは存在しません。")
        return

    group = armature.pose.bone_groups[bone_group_enum.value]

    # ボーンの存在を確認して、ボーングループに追加
    if bone_name in armature.pose.bones:
        armature.pose.bones[bone_name].bone_group = group
    else:
        print(f"{bone_name} という名前のボーンは存在しません。")

    # 元のモードに戻す
    # bpy.ops.object.mode_set(mode='OBJECT')

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

def create_custom_shape(shape_type="cube", size=0.5, up_axis='Z'):
    # 新しいコレクション "WGT" を作成
    if "WGT" not in bpy.data.collections:
        wgt_collection = bpy.data.collections.new("WGT")
        bpy.context.scene.collection.children.link(wgt_collection)
    else:
        wgt_collection = bpy.data.collections["WGT"]

    # shape_typeに基づいてカスタムシェイプオブジェクトを作成
    if shape_type == "cube":
        bpy.ops.mesh.primitive_cube_add(size=size)
    elif shape_type == "plane":
        bpy.ops.mesh.primitive_plane_add(size=size)
    elif shape_type == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size/2)  # radiusはsizeの半分
    elif shape_type == "circle":  # ここで"circle"を追加
        bpy.ops.mesh.primitive_circle_add(radius=size/2, fill_type='NGON')  # NGONで塗りつぶし
    else:
        raise ValueError(f"Unknown shape_type: {shape_type}")

    custom_shape = bpy.context.active_object
    custom_shape.name = f"WGT-Bone_{shape_type}"

    # up_axisに合わせてオブジェクトを回転
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    if up_axis == 'X':
        bpy.ops.transform.rotate(value=-1.5708, orient_axis='Y')  # Y軸を中心に-90度回転
    elif up_axis == 'Y':
        bpy.ops.transform.rotate(value=1.5708, orient_axis='X')   # X軸を中心に90度回転
    elif up_axis != 'Z':
        raise ValueError(f"Invalid up_axis: {up_axis}")
    
    bpy.ops.object.mode_set(mode='OBJECT')

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
                custom_shape = create_custom_shape("cube", scale)
                assign_bone_to_group(bone,BoneGroups.BODY_HANDLE)
            elif bone == "center":
                custom_shape = create_custom_shape("plane", scale)
                assign_bone_to_group(bone,BoneGroups.CENTER_HANDLE)
            else:
                custom_shape = create_custom_shape("circle", scale,"Y")
                assign_bone_to_group(bone,BoneGroups.BODY_HANDLE)
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

class BoneGroups(Enum):
    IK_HANDLE = "IK_handle"
    POLE_HANDLE = "Pole_handle"
    BODY_HANDLE = "body_handle"
    CENTER_HANDLE = "center_handle"
    CONTROLLER_HANDLE = "controller_handle"

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
            custom_shape = create_custom_shape("cube",1)
            custom_shapePole = create_custom_shape("sphere",0.5)
            
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
                print("test")
                assign_bone_to_group("L_hand_IK",BoneGroups.IK_HANDLE)
                pbone1 = armature_obj.pose.bones["R_hand_IK"]
                pbone1.custom_shape = custom_shape
                assign_bone_to_group("R_hand_IK",BoneGroups.IK_HANDLE)
                pbone2 = armature_obj.pose.bones["L_hand_pole"]
                pbone2.custom_shape = custom_shapePole
                assign_bone_to_group("L_hand_pole",BoneGroups.POLE_HANDLE)
                pbone3 = armature_obj.pose.bones["R_hand_pole"]
                pbone3.custom_shape = custom_shapePole
                assign_bone_to_group("R_hand_pole",BoneGroups.POLE_HANDLE)

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
            hand_sets = ["R_hand","L_hand"]
            for hand in hand_sets:
                assign_bone_to_group(hand, BoneGroups.BODY_HANDLE)
                custom = create_custom_shape("circle",3,"Y")
                pbonehand = armature_obj.pose.bones[hand]
                pbonehand.custom_shape = custom
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
                # コンストレイントの名前に[_rig]を追加
                constraint.name = constraint.name + "_rig"
            hide_constraints_of_armature(selected_obj.name,"_rig")
            # ポーズモードからオブジェクトモードに切り替え
            bpy.ops.object.mode_set(mode='OBJECT')
            # ボーングループの作成
            create_colored_bone_groups(rig)
            #暫定でもとのアーマチュアの髪のコンストレイントを削除/RigPlusのHairボーンを削除
            modify_bones_with_string(selected_obj.name,"Hair")
            modify_bones_with_string(rig.name,"Hair")


            
            self.report({'INFO'}, "Rig created and constraints added.")
        else:
            self.report({'ERROR'}, "Please select an armature in Object Mode.")
        
        return {'FINISHED'}
    

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
            custom_shape = create_custom_shape("cube",0.5)
            custom_shapePole = create_custom_shape("sphere",0.5)

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
                        assign_bone_to_group(ik_bone_name,BoneGroups.IK_HANDLE)
                        pbone0 = armature_obj.pose.bones[pole_target_name]
                        pbone0.custom_shape = custom_shapePole
                        assign_bone_to_group(pole_target_name,BoneGroups.POLE_HANDLE)

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
            bpy.ops.object.mode_set(mode='OBJECT')
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
    # upper_Ik_l_global_location = amt.matrix_world @ amt.pose.bones[upper_Ik.name].tail
    # context.scene.cursor.location = upper_Ik_l_global_location
    # for bone in amt.data.bones:
    #     bone.select = False
    # amt.pose.bones[pole.name].bone.select = True
    # bpy.ops.view3d.snap_selected_to_cursor(False)
    # pole.location.z = pole.location.z+0.01
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
        
# パネル設定用
class IKToolSettings(bpy.types.PropertyGroup):
    show_arm_ik: bpy.props.BoolProperty(
        name="Show 腕IKSetting",
        description="Toggle visibility of 腕IK作成 section",
        default=False
    )
    show_leg_ik: bpy.props.BoolProperty(
        name="Show 足IKSettig",
        description="Toggle visibility of 足IK作成 section",
        default=False
    )
    show_toe_rig: bpy.props.BoolProperty(
        name="Show つま先・踵Rig",
        description="Toggle visibility of つま先・踵Rig section",
        default=False
    )
#パネル設定用
def draw_head_constraint(context, layout):
    # ポーズボーンを取得
    ob = context.active_object
    pbone = ob.pose.bones.get("head_rot")
    
    # head_rotボーンが存在し、そのボーンにCopyRotationコンストレイントがあるかを確認
    if pbone and any(c.type == 'COPY_ROTATION' for c in pbone.constraints):
        # CopyRotationコンストレイントを見つける
        copy_rot_constraint = next(c for c in pbone.constraints if c.type == 'COPY_ROTATION')
        # スライダーをUIに追加
        row = layout.row()
        row.prop(copy_rot_constraint, "influence", slider=True, text="Head Rot Influence")
#パネル設定用
class IKToolPanel(bpy.types.Panel):
    bl_label = "DistroRigPlus"
    bl_idname = "OBJECT_PT_ik_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DistroRigPlus'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ik_tool_settings

        # Rigを作成のみのボックス
        box = layout.box()
        box.label(text="Rig Tools:", icon='ARMATURE_DATA')
        box.operator("object.make_rig", text="Rigを作成")
        
        # 別のボックスに「体幹のRigを作成」を配置
        box = layout.box()
        box.label(text="Torso Rig Tools:", icon='ARMATURE_DATA')
        box.operator("object.createtorso_rig", text="体幹のRigを作成")
        draw_head_constraint(context, box)  # ここで関数を呼び出す

        # 腕IKの表示設定
        layout.prop(settings, "show_arm_ik")
        if settings.show_arm_ik:
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

        # 足IKの表示設定
        layout.prop(settings, "show_leg_ik")
        if settings.show_leg_ik:
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

        # 足IKの表示設定
        layout.prop(settings, "show_toe_rig")
        if settings.show_toe_rig:
            box = layout.box()
            box.label(text="つま先・踵Rig:", icon='CONSTRAINT_BONE')
            box.operator("object.create_toe_heel_rig", text="Toes & Heels Rig")

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
            if not ref_bone:
                self.report({'ERROR'}, f"Reference bone '{foot_ik_name}' or '{side}_foot' not found.")
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
            toeBaseRot_bone.head = toeBase_bone.head
            toeBaseRot_bone.tail = toeBase_bone.tail
            foot_bone = edit_bones.get(foot_name)
            toeBaseRot_bone.use_connect = False
            toeBaseRot_bone.parent = foot_bone
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
        # Switch back to Object mode at the end
        # bpy.ops.object.mode_set(mode='OBJECT')
        # # 
        # for side in ['L', 'R']:
        #     bpy.ops.object.mode_set(mode='EDIT')
        #     foot_ik_p_name = f"{side}_foot_IK_P"
        #     heel_dummy_name = f"{side}_heel_dummy"
        #     toe_base_dummy_name = f"{side}_toeBase_dummy"

        #     custom_shape = create_custom_shape("cube", 1)
        #     assign_bone_to_group(foot_ik_p_name,BoneGroups.IK_HANDLE)
        #     armature.pose.bones[foot_ik_p_name].custom_shape = custom_shape
        # return {'FINISHED'}

def register():
    bpy.utils.register_class(CreateLegIKOperator)
    bpy.utils.register_class(CreateWristIKOperator)
    bpy.utils.register_class(MakeRigOperator)
    bpy.utils.register_class(IK2FKRightOperator)
    bpy.utils.register_class(IK2FKLeftOperator)
    bpy.utils.register_class(CopyIKtoFKLeftOperator)
    bpy.utils.register_class(CopyIKtoFKRightOperator)
    bpy.utils.register_class(CreateTorsoRig)
    bpy.utils.register_class(CopyLeftLegIKtoFKOperator)
    bpy.utils.register_class(CopyRightLegIKtoFKOperator)
    bpy.utils.register_class(IK2FKLeftLegOperator)
    bpy.utils.register_class(IK2FKRightLegOperator)
    bpy.utils.register_class(OBJECT_OT_CreateToeHeelRig)
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
    bpy.utils.unregister_class(CreateTorsoRig)
    bpy.utils.unregister_class(CopyLeftLegIKtoFKOperator)
    bpy.utils.unregister_class(CopyRightLegIKtoFKOperator)
    bpy.utils.unregister_class(IK2FKLeftLegOperator)
    bpy.utils.unregister_class(IK2FKRightLegOperator)
    bpy.utils.unregister_class(OBJECT_OT_CreateToeHeelRig)
    del bpy.types.Scene.ik_tool_settings
    bpy.utils.unregister_class(IKToolPanel)
    bpy.utils.unregister_class(IKToolSettings)

if __name__ == "__main__":
    register()

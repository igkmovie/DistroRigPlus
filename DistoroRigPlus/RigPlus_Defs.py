import bpy
from bpy.types import Operator, Panel
import mathutils
import math 
from enum import Enum
import json
from . import RigPlus_Data
#メッセージポップアップを表示するためのクラス
class MessagePopupOperator(bpy.types.Operator):
    bl_idname = "wm.message_popup_operator"
    bl_label = "Message Popup Operator"

    message: bpy.props.StringProperty(
        name="Message",
        description="Message to display in the popup",
        default="This is a message"
    )

    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}
#メッセージポップアップのラッパー
def show_popup(message):
    bpy.ops.wm.message_popup_operator(message)

#選択中にアーマチュア内にボーンがあるかないか？を判断するメソッド
def bone_exist(bone_name):
    # 現在のコンテキストからアクティブなオブジェクトを取得
    obj = bpy.context.active_object

    # オブジェクトがアーマチュアであること、およびボーンが存在することを確認
    if obj and obj.type == 'ARMATURE' and bone_name in obj.data.bones:
        return True
    else:
        return False

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
    blender_version = bpy.app.version
    for name, color in bone_group_data.items():
        if blender_version < (3, 80, 0):
            if name not in active_obj.pose.bone_groups:
                bg = active_obj.pose.bone_groups.new(name=name)
                bg.color_set = 'CUSTOM'
                bg.colors.normal = color
        else:
            if name not in active_obj.data.collections:
                bg = active_obj.data.collections.new(name=name)
                bg.color = color            
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
#指定したボーン(名)の別レイヤーに移して非表示にするやつ。 
def move_bone_to_last_layer_and_hide(armature_obj, bone_name,target_layer = 31 ):
     # 最後のレイヤー
    bpy.ops.object.mode_set(mode='EDIT')

    # 特定のボーンを選択
    bone = armature_obj.data.edit_bones[bone_name]
    bone.select = True
    armature_obj.data.edit_bones.active = bone

    # ボーンを最後のレイヤーに移動
    bone.layers[target_layer] = True
    for i in range(len(bone.layers)):
        if i != target_layer:
            bone.layers[i] = False
    # オブジェクトモードに戻る
    bpy.ops.object.mode_set(mode='OBJECT')

    # 元のレイヤーを非表示にする
    armature_obj.data.layers[target_layer] = False

#VroidやMMDによってIK設定とPoleAngle
def apply_ik_settings_and_pole_angle(name, limb_type):
    # IK設定文字列を解析
    ik_settings = json.loads(RigPlus_Data.ik_setting_str)
    print("apply_ik_settings_and_pole_angle: " + name)
    # 指定された名前の設定を抽出
    settings = next((item for item in ik_settings if item["name"] == name), None)
    if settings is None:
        print("指定された名前の設定が見つかりません。")
        return
    # アーマチュアにアクセスして設定を適用
    armature_obj = bpy.data.objects.get("RigPlus")
    if armature_obj is None or armature_obj.type != 'ARMATURE':
        print("アーマチュアオブジェクトを選択してください。")
        return
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    # 肢体のタイプに基づいてボーンを定義
    bone_type = "arm" if limb_type == "Hand" else "leg"
    bones = [f"L_lower_{bone_type}", f"R_lower_{bone_type}",f"R_lower_{bone_type}_dummy",f"L_lower_{bone_type}_dummy"]

    for bone_name in bones:
        bone = armature_obj.pose.bones.get(bone_name)
        if bone is None:
            print(f"アーマチュアに {bone_name} というボーンが見つかりません。")
            continue
        # ボーンのIK制約のポール角度と制限を更新
        update_ik_settings_and_pole_angle(bone, settings, limb_type)

    bpy.ops.object.mode_set(mode='OBJECT')

def update_ik_settings_and_pole_angle(bone, settings, limb_type):
    # ボーンのIK制約を見つける
    ik_constraint = next((c for c in bone.constraints if c.type == 'IK'), None)
    if ik_constraint is None:
        print(f"{bone.name} にはIK制約が見つかりません。")
        return
    # ボーン名から左右を判断
    side = "L" if "L_" in bone.name else "R"

    # ポール角度の設定キーを生成
    pole_angle_key = f"{side}_{limb_type}_Pole_angle"
    print(bone.name+"/"+pole_angle_key+"/"+str(settings[pole_angle_key]))
    ik_constraint.pole_angle = math.radians(float(settings[pole_angle_key]))
    # IK制限を設定
    # X軸の制限
    limit_x_min_key = f"{side}_{limb_type}_Limt_x_min"
    limit_x_max_key = f"{side}_{limb_type}_Limt_x_Max"
    bone.use_ik_limit_x = True
    bone.ik_min_x = math.radians(float(settings[limit_x_min_key]))
    bone.ik_max_x = math.radians(float(settings[limit_x_max_key]))
    # print(limit_x_min_key+"/"+str(settings[limit_x_min_key])+"/"+limit_x_max_key+"/"+str(settings[limit_x_max_key]))
    # X軸と同様に 'use_ik_limit_y', 'ik_min_y', 'ik_max_y' を使用する
    # Z軸の制限
    limit_z_min_key = f"{side}_{limb_type}_Limt_z_min"
    limit_z_max_key = f"{side}_{limb_type}_Limt_z_Max"
    bone.use_ik_limit_z = True
    bone.ik_min_z = math.radians(float(settings[limit_z_min_key]))
    bone.ik_max_z = math.radians(float(settings[limit_z_max_key]))
    # print(limit_z_min_key+"/"+str(settings[limit_z_min_key])+"/"+limit_z_max_key+"/"+str(settings[limit_z_max_key]))

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
import bpy
import json
from . import RigPlus_Data

# アーマチュア内のボーン名をチェックしてリストを作成するクラス
class MapBonesToRigPlus(bpy.types.Operator):
    bl_idname = "object.mapbonestorigplus"
    bl_label = "Map Bones To RigPlus"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # JSON文字列からデータを読み込む
        bone_data = json.loads(RigPlus_Data.bone_data_str)

        # 初期のbone_mappingを作成（すべてのRigPlus名に対して空のTargetを設定）
        bone_mapping = {item['RigPlus']: "" for item in bone_data}

        # 選択中のアーマチュアを取得
        armature = context.active_object

        # MMDのボーン名一覧を検索
        for item in bone_data:
            if item['MMD'] in armature.data.bones:
                bone_mapping[item['RigPlus']] = item['MMD']

        # Vroidのボーン名一覧を検索
        for item in bone_data:
            if item['Vroid'] in armature.data.bones:
                bone_mapping[item['RigPlus']] = item['Vroid']

        # Valueが空白のKey名を取得
        missing_targets = [key for key, value in bone_mapping.items() if not value]

        # 結果をIKToolSettingsのプロパティとして保存
        ik_tool_settings = context.scene.ik_tool_settings
        ik_tool_settings.bone_mapping = json.dumps(bone_mapping)
        ik_tool_settings.missing_targets = json.dumps(missing_targets)
        # ボーンの名前リスト
        bone_names = [
            'J_Bip_C_Spine', '上半身0',  # Spine
            'J_Bip_C_Chest', '上半身',    # Chest
            'J_Bip_C_UpperChest', '上半身2',  # Upper Chest
            'J_Bip_C_Neck', '首',         # Neck
            'J_Bip_C_Head', '頭',         # Head
            'J_Bip_C_Hips', '下半身'       # Hips
        ]
        bpy.ops.object.mode_set(mode='EDIT')
        armature_obj = bpy.context.active_object.data
        # 指定されたボーンに対してuse_connectをFalseに設定
        for bone_name in bone_names:
            if bone_name in armature_obj.edit_bones:
                armature_obj.edit_bones[bone_name].use_connect = False
        # オブジェクトモードに戻る
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
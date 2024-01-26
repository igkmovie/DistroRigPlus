import sys
import os
import bpy
import json
from . import RigPlus_Data


# アーマチュア内のボーン名をチェックしてリストを作成するクラス
class MapBonesToRigPlus(bpy.types.Operator):
    bl_idname = "object.mapbonestorigplus"
    bl_label = "Map Bones To RigPlus"
    bl_options = {'REGISTER', 'UNDO'}

    def vrm(context):
        # JSON文字列からデータを読み込む
        bone_data = json.loads(RigPlus_Data.bone_data_str)
        # print(bone_data)
        # 選択中のアーマチュアを取得
        armature = context.active_object
        bones = bpy.data.armatures["Armature"].vrm_addon_extension.vrm0.humanoid.human_bones
       # bone_mappingディクショナリを初期化
        bone_mapping = {}
        # bone_dataをループ
        armature = bpy.data.armatures["Armature"]
        for item in bone_data:
            # vrmの値を整数として取得
            vrm_index = int(item['vrm'])
            # vrmの値をインデックスとして使用してボーン名を取得
            if 0 <= vrm_index < len(armature.vrm_addon_extension.vrm0.humanoid.human_bones):
                bone_name = armature.vrm_addon_extension.vrm0.humanoid.human_bones[vrm_index].node.bone_name
                bone_mapping[item['RigPlus']] = bone_name
        armature_obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        # 名前が「root」で親がないボーンを探す
        root_bones = [bone.name for bone in armature_obj.pose.bones if "root" in bone.name.lower()]
        bone_mapping["Root"] = root_bones[0]
        bpy.ops.object.mode_set(mode='OBJECT')
        return bone_mapping

    
    def other(context,bone_mapping):
        # JSON文字列からデータを読み込む
        bone_data = json.loads(RigPlus_Data.bone_data_str)
        # 選択中のアーマチュアを取得
        armature = context.active_object
        settings = context.scene.rigplus_settings
        # MMDのボーン名一覧を検索
        if(settings.prop_vrm0 == True):
            for item in bone_data:
                if item['MMD'] in armature.data.bones:
                    bone_mapping[item['RigPlus']] = item['MMD']

        return bone_mapping
    
    def execute(self, context):
        # JSON文字列からデータを読み込む
        bone_data = json.loads(RigPlus_Data.bone_data_str)

        # 初期のbone_mappingを作成（すべてのRigPlus名に対して空のTargetを設定）
        bone_mapping = {item['RigPlus']: "" for item in bone_data}
        armature = context.active_object
        settings = context.scene.rigplus_settings
        if(settings.prop_vrm0 == True):
            bone_mapping = MapBonesToRigPlus.vrm(context)        
        else :
            bone_mapping = MapBonesToRigPlus.other(context,bone_mapping)
        # bone_mapping = MapBonesToRigPlus.vrm(context)
        # Valueが空白のKey名を取得
        missing_targets = [key for key, value in bone_mapping.items() if not value]

        # 結果をRigPlusSettingsのプロパティとして保存
        rigplus_settings = context.scene.rigplus_settings
        rigplus_settings.bone_mapping = json.dumps(bone_mapping)
        rigplus_settings.missing_targets = json.dumps(missing_targets)


        # ボーンの名前リスト
        target_rigplus_bones = ["spine", "chest", "upper_chest", "neck", "head", "hips"]

        bpy.ops.object.mode_set(mode='EDIT')
        armature_obj = bpy.context.active_object.data
        # bone_mappingを使用して対象のボーンを探し、use_connectをFalseに設定
        for rigplus_name in target_rigplus_bones:
            target_bone_name = bone_mapping.get(rigplus_name)
            if target_bone_name and target_bone_name in armature.data.edit_bones:
                armature_obj.edit_bones[target_bone_name].use_connect = False
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    
class MapBonesToRigPlusTest(bpy.types.Operator):
    bl_idname = "object.mapbonestorigplustest"
    bl_label = "Map Bones To RigPlus test"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bones = bpy.data.armatures["Armature"].vrm_addon_extension.vrm0.humanoid.human_bones
        for index, bone in enumerate(bones):
            print(index, bone.node.bone_name)
        # bone_name = "test"
        return {'FINISHED'}
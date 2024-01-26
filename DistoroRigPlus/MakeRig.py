import bpy
from . import RigPlus_Defs
from . import RigPlus_Data
from . import Property_Panel
import json

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
#rigplus用のボーン名に変更する
def rename_bones_to_rigplus(armature, context):
    # RigPlusSettingsからbone_mappingを取得
    rigplus_settings = context.scene.rigplus_settings  # 仮定されたプロパティ名
    bone_mapping = json.loads(rigplus_settings.bone_mapping)
    # エディットモードに移行
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # bone_mappingのValueをキーとして、対応するRigPlus名にボーン名を変更
    for rigplus_name, armature_bone_name in bone_mapping.items():
        print(rigplus_name+"/"+armature_bone_name)
        if armature_bone_name and armature_bone_name in armature.data.edit_bones:
            armature.data.edit_bones[armature_bone_name].name = rigplus_name

    # オブジェクトモードに戻る
    bpy.ops.object.mode_set(mode='OBJECT')
class MakeRigOperator(bpy.types.Operator):
    bl_idname = "object.make_rig"
    bl_label = "Make Rig"
    def is_name_in_bone_mapping(self, name):
        rigplus_settings = bpy.context.scene.rigplus_settings  # RigPlusSettingsのインスタンスを取得
        bone_mapping_str = rigplus_settings.bone_mapping
        
        # bone_mappingが初期値の場合はFalseを返す
        if bone_mapping_str == "none":
            return False
        try:
            bone_mapping = json.loads(bone_mapping_str)
            # nameがキーまたは値に含まれているかチェック
            return name in bone_mapping or name in bone_mapping.values()
        except json.JSONDecodeError:
            print("JSONの解析に失敗しました。")
            return False
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
                flg = self.is_name_in_bone_mapping(bone.name)
                if(not flg):
                    continue
                constraint = bone.constraints.new(type='COPY_TRANSFORMS')
                constraint.target = rig  # rigアーマチュアをターゲットにする
                constraint.subtarget = bone.name
                # ターゲットのボーンも設定
                constraint.target_space = 'POSE'
                constraint.owner_space = 'POSE'
                # コンストレイントの名前に[_rig]を追加
                constraint.name = constraint.name + "_rig"
            hide_constraints_of_armature(selected_obj.name,"_rig")
            # ポーズモードからオブジェクトモードに切り替え
            bpy.ops.object.mode_set(mode='OBJECT')
            # ボーングループの作成
            RigPlus_Defs.create_colored_bone_groups(rig)
            bpy.ops.object.mode_set(mode='EDIT')

            #Rigに使うボーン以外は削除
            for bone in rig.data.edit_bones:
                flg = self.is_name_in_bone_mapping(bone.name)
                if(not flg):
                    rig.data.edit_bones.remove(bone)
            #VroidのBoneだったら
            bpy.ops.object.mode_set(mode='EDIT')
            # flg1 = self.is_name_in_bone_mapping("J_Bip_C_Hips")
            settings = context.scene.rigplus_settings
            # flg1 = True
            # if(flg1):
            #     vroid_bone = rig.data.edit_bones.new('VROID')
            #     vroid_bone.head = (0, 0.1, 0)
            #     vroid_bone.tail = (0, 0.2, 0)
            #     RigPlus_Defs.move_bone_to_last_layer_and_hide(rig,"VROID")
            # #MMDのBoneだったら
            # flg2 = self.is_name_in_bone_mapping("下半身")
            # if(flg2):
            #     mmd_bone = rig.data.edit_bones.new('MMD')
            #     mmd_bone.head = (0, 0.1, 0)
            #     mmd_bone.tail = (0, 0.2, 0)
            #     RigPlus_Defs.move_bone_to_last_layer_and_hide(rig,"MMD")
            rename_bones_to_rigplus(rig,context)
            bpy.ops.object.mode_set(mode='EDIT')
            new_bone = rig.data.edit_bones.new('RigPlus')      
            # ボーンの位置を設定（例として、根元と先端の位置を設定）
            new_bone.head = (0, 0, 0)
            new_bone.tail = (0, 0.1, 0)
            RigPlus_Defs.move_bone_to_last_layer_and_hide(rig,"RigPlus")


            # "center" ボーンが存在するか確認
            bpy.ops.object.mode_set(mode='EDIT')
            edit_bones = rig.data.edit_bones
            edit_bones1 = selected_obj.data.edit_bones
            if "center" not in edit_bones:
                # "center" ボーンを作成
                center_bone = edit_bones.new("center")
                center_bone.head = (0, 0, 0)
                center_bone.tail = (0, 0, 0)  # 仮の高さ

                # "hips" ボーンの高さを取得し、"center" の位置を設定
                if "hips" in edit_bones:
                    hips_height = edit_bones["hips"].head.z
                    center_bone.head.z = hips_height
                    center_bone.tail.z = hips_height
                    center_bone.tail.y += 0.15

                # "Root" ボーンを親に設定
                if "Root" in edit_bones:
                    center_bone.parent = edit_bones["Root"]

            # "hips" の親を "center" に設定
            if "hips" in edit_bones and "center" in edit_bones:
                edit_bones["hips"].use_connect = False;
                edit_bones["hips"].parent = edit_bones["center"]
            if "hips" in edit_bones1:
                edit_bones1["hips"].use_connect = False;
            
            # JSON文字列をPythonの辞書リストに変換
            bone_data = json.loads(RigPlus_Data.bone_data_str)
            # RigPlusのボーン名を格納するリスト
            rigplus_bone_names = [bone['RigPlus'] for bone in bone_data]
            bpy.ops.object.mode_set(mode='POSE')

            for bone_name in rigplus_bone_names:
                # ボーンが存在するかどうかをチェック
                if bone_name in rig.pose.bones:
                    # ボーンが存在する場合はカスタムシェイプを設定
                    custom_shape = RigPlus_Defs.create_custom_shape("circle", 0.5, "Y")
                    RigPlus_Defs.assign_bone_to_group(bone_name, Property_Panel.BoneGroups.BODY_HANDLE)
                    rig.pose.bones[bone_name].custom_shape = custom_shape
            bpy.ops.object.mode_set(mode='OBJECT')

            self.report({'INFO'}, "Rig created and constraints added.")
        else:
            self.report({'ERROR'}, "Please select an armature in Object Mode.")
        
        return {'FINISHED'}
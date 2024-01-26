import bpy
from bpy.types import Operator, Panel
from enum import Enum
from . import RigPlus_Defs

class BoneGroups(Enum):
    IK_HANDLE = "IK_handle"
    POLE_HANDLE = "Pole_handle"
    BODY_HANDLE = "body_handle"
    CENTER_HANDLE = "center_handle"
    CONTROLLER_HANDLE = "controller_handle"

# つま先とかかとのリグのInfluence更新関数の定義
def update_foot_bones_influence(self, context, side):
    armature = context.object
    if armature and armature.type == 'ARMATURE':
        bone_names = [f"{side}_footRot", f"{side}_toeBaseRot"]
        for bone_name in bone_names:
            bone = armature.pose.bones.get(bone_name)
            if bone:
                for constraint in bone.constraints:
                    if constraint.type == 'DAMPED_TRACK':
                        constraint.influence = getattr(self, f"{side.lower()}_foot_influence")

def update_l_foot_bones_influence(self, context):
    update_foot_bones_influence(self, context, 'L')

def update_r_foot_bones_influence(self, context):
    update_foot_bones_influence(self, context, 'R')       
# パネル設定用
class RigPlusSettings(bpy.types.PropertyGroup):
    ik_setting: bpy.props.StringProperty(
        name="ik_setting List JSON",
        default="",
        description="JSON representation of the multi list"
    )
    show_arm_ik: bpy.props.BoolProperty(
        name="OnHandIKSetting",
        description="Toggle visibility of HandIKSetting section",
        default=False
    )
    show_leg_ik: bpy.props.BoolProperty(
        name="OnFootIKSetting",
        description="Toggle visibility of OnFootIKSetting section",
        default=False
    )
    show_toe_rig: bpy.props.BoolProperty(
        name="OnToe&HeelSetting",
        description="Toggle visibility of Toe&HeelSetting section",
        default=False
    )
    show_Troso_rig: bpy.props.BoolProperty(
        name="OnTrosoSetting",
        description="Toggle visibility of TrosoSetting section",
        default=False
    )
    l_foot_influence: bpy.props.FloatProperty(
        name="L Foot Influence",
        default=1.0,
        min=0.0,
        max=1.0,
        update=update_l_foot_bones_influence
    )
    r_foot_influence: bpy.props.FloatProperty(
        name="R Foot Influence",
        default=1.0,
        min=0.0,
        max=1.0,
        update=update_r_foot_bones_influence
    )
    bone_mapping: bpy.props.StringProperty(
        name="bone_mapping JSON",
        default="none",
        description="JSON representation of the multi list"
    )
    missing_targets: bpy.props.StringProperty(
        name="missing_targets List JSON",
        default="",
        description="JSON representation of the multi list"
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
#足切IKのパネル操作
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
                        row.prop(constraint, "influence", slider=True,text=displayName)
        bone_names = ["R_foot", "L_foot"]
        row = layout.row()
        bone_name1 = "L_foot_IK_P"
        bone_exists = bone_name1 in [bone.name for bone in armature_obj.data.bones]
        if not bone_exists:
            row.label(text="Ground IK_ON/OFF",icon='CONSTRAINT_BONE')
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
                            row.prop(constraint, "influence", slider=True,text=displayName)
#腕切IKパネル用
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
                        row.prop(constraint, "influence", slider=True,text=displayName)
        bone_names = ["R_hand", "L_hand"]
        row = layout.row()
        row.label(text="Ground IK_ON/OFF",icon='CONSTRAINT_BONE')
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
                        row.prop(constraint, "influence", slider=True,text=displayName)
#IKのチャイルドコンストレイントのパネル設定
def draw_IK_bone_constraints(context, layout):
    armature_obj = context.active_object
    if armature_obj and armature_obj.type == 'ARMATURE':
        ik_bone_names = ["R_hand_IK", "L_hand_IK"]
        layout.label(text="hand_IK Parent:", icon='CONSTRAINT_BONE')

        # 'R_hand_IK' と 'L_hand_IK' のコンストレイント設定
        for ik_bone_name in ik_bone_names:
            bone = armature_obj.pose.bones.get(ik_bone_name)
            if bone:
                child_of_constraint = next((c for c in bone.constraints if c.type == 'CHILD_OF'), None)
                if child_of_constraint:
                    # ターゲットボーン選択メニュー
                    
                    row = layout.row()
                    row.label(text=f"{ik_bone_name} Parent Bone:")
                    row.prop_search(child_of_constraint, "subtarget", armature_obj.pose, "bones", text="")

                    # インフルエンススライダー
                    row = layout.row()
                    row.prop(child_of_constraint, "influence", slider=True)
class BoneGroups(Enum):
    IK_HANDLE = "IK_handle"
    POLE_HANDLE = "Pole_handle"
    BODY_HANDLE = "body_handle"
    CENTER_HANDLE = "center_handle"
    CONTROLLER_HANDLE = "controller_handle"
def update_prop(self, context):
    selected = context.scene.my_tool

    # 他のプロパティをFalseに設定する条件を変更
    if self.prop_a and (self.prop_b or self.prop_c):
        selected.prop_b = selected.prop_c = False
    elif self.prop_b and (self.prop_a or self.prop_c):
        selected.prop_a = selected.prop_c = False
    elif self.prop_c and (self.prop_a or self.prop_b):
        selected.prop_a = selected.prop_b = False
# パネル設定用
class RigPlusSettings(bpy.types.PropertyGroup):
    ik_setting: bpy.props.StringProperty(
        name="ik_setting List JSON",
        default="",
        description="JSON representation of the multi list"
    )
    show_arm_ik: bpy.props.BoolProperty(
        name="OnHandIKSetting",
        description="Toggle visibility of HandIKSetting section",
        default=False
    )
    show_leg_ik: bpy.props.BoolProperty(
        name="OnFootIKSetting",
        description="Toggle visibility of OnFootIKSetting section",
        default=False
    )
    show_toe_rig: bpy.props.BoolProperty(
        name="OnToe&HeelSetting",
        description="Toggle visibility of Toe&HeelSetting section",
        default=False
    )
    show_Troso_rig: bpy.props.BoolProperty(
        name="OnTrosoSetting",
        description="Toggle visibility of TrosoSetting section",
        default=False
    )

    l_foot_influence: bpy.props.FloatProperty(
        name="L Foot Influence",
        default=1.0,
        min=0.0,
        max=1.0,
        update=update_l_foot_bones_influence
    )
    r_foot_influence: bpy.props.FloatProperty(
        name="R Foot Influence",
        default=1.0,
        min=0.0,
        max=1.0,
        update=update_r_foot_bones_influence
    )
    bone_mapping: bpy.props.StringProperty(
        name="bone_mapping JSON",
        default="none",
        description="JSON representation of the multi list"
    )
    missing_targets: bpy.props.StringProperty(
        name="missing_targets List JSON",
        default="",
        description="JSON representation of the multi list"
    )
    prop_vrm0: bpy.props.BoolProperty(name="VRM0.x",default=True, update=update_prop)
    prop_vrm1: bpy.props.BoolProperty(name="VRM1.x", update=update_prop)
    prop_pmx: bpy.props.BoolProperty(name="pmx", update=update_prop)

#パネル設定用
class IKToolPanel(bpy.types.Panel):
    bl_label = "DistroRigPlus"
    bl_idname = "OBJECT_PT_ik_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DistroRigPlus'
    
    def draw_foot_influence_sliders(self, context, box, settings):
        armature_obj = bpy.context.view_layer.objects.active
        bone_name = "L_footRot"
        bone_exists = bone_name in [bone.name for bone in armature_obj.data.bones]

        if bone_exists:
            box.prop(settings, "l_foot_influence", slider=True, text="L Toe Influence")
            box.prop(settings, "r_foot_influence", slider=True, text="R Toe Influence")    

    def draw(self, context):
        layout = self.layout
        settings = context.scene.rigplus_settings
        flg = True;
        typebox = layout.box()
        typebox.prop(settings, "prop_vrm0")
        # Rigを作成のみのボックス
        box0 = layout.box()
        box0.label(text="Rig Tools:", icon='ARMATURE_DATA')
        box0.operator("object.mapbonestorigplus", text="RigSetUp")

        if(settings.bone_mapping == "none"):
            return
        # Rigを作成のみのボックス
        box = layout.box()
        box.label(text="Rig Tools:", icon='ARMATURE_DATA')
        box.operator("object.make_rig", text="Make Rig")

        flg1 = RigPlus_Defs.bone_exist("RigPlus")
        flg2 = RigPlus_Defs.bone_exist("head_rot")
        flg3 = RigPlus_Defs.bone_exist("L_hand_pole")
        flg4 = RigPlus_Defs.bone_exist("L_foot_pole")
        flg5 = RigPlus_Defs.bone_exist("L_foot_IK_P")
        flg6 = RigPlus_Defs.bone_exist("MMD")
        # flg6 = False

        if(not flg1):
            return
        # 別のボックスに「体幹のRigを作成」を配置
        box = layout.box()
        box.label(text="Rig Make", icon='ARMATURE_DATA')
        if(not flg2):
            box.operator("object.createtorso_rig", text="Torso Rig Creation")
        if(not flg3):
            box.operator("object.create_wrist_ik",text="Arm IK Creation")
        if(not flg4):
            box.operator("object.create_leg_ik", text="Foot IK Creation")
        if(not flg6):
            if(not flg5):
                box.operator("object.create_toe_heel_rig", text="Toes & Heels Rig")      
        if(flg2):
            layout.prop(settings,"show_Troso_rig")
            if settings.show_Troso_rig:
                box = layout.box()
                box.label(text="Troso Rig Setting:", icon='CONSTRAINT_BONE')
                draw_head_constraint(context, box)  # ここで関数を呼び出す
        if(flg3):
            # 腕IKの表示設定
            layout.prop(settings, "show_arm_ik")
            if settings.show_arm_ik:
                box = layout.box()
                box.label(text="腕IK作成:", icon='CONSTRAINT_BONE')
                # box.operator("object.create_wrist_ik", text="腕IK作成")
                draw_bone_constraints(context, box)
                box.label(text="Right Arm IK2FK/FK2IK:", icon='CONSTRAINT_BONE')
                box.operator("pose.ik_to_fk_right", text="IK to FK βver")
                box.operator("pose.copy_ik_to_fk_right", text="FK to IK")
                box.label(text="Left Arm IK2FK/FK2IK:", icon='CONSTRAINT_BONE')
                box.operator("pose.ik_to_fk_left", text="IK to FK βver")
                box.operator("pose.copy_ik_to_fk_left", text="FK to IK")
                draw_IK_bone_constraints(context, box)
        if(flg4):
            # 足IKの表示設定
            layout.prop(settings, "show_leg_ik")
            if settings.show_leg_ik:
                box = layout.box()
                box.label(text="足IK Tools:", icon='CONSTRAINT_BONE')
                # box.operator("object.create_leg_ik", text="足IK作成")
                draw_leg_constraints(context, box)
                box.label(text="Right leg:", icon='CONSTRAINT_BONE')
                box.operator("pose.ik_to_fk_right_leg", text="IK to FK βver")
                box.operator("pose.copy_right_leg_ik_to_fk", text="FK to IK")
                box.label(text="Left leg:", icon='CONSTRAINT_BONE')
                box.operator("pose.ik_to_fk_left_leg", text="IK to FK βver")
                box.operator("pose.copy_left_leg_ik_to_fk", text="FK to IK ")
        if(flg5):
            # 足IKの表示設定
            layout.prop(settings, "show_toe_rig")
            if settings.show_toe_rig:
                box = layout.box()
                box.label(text="Toe&HeelRig:", icon='CONSTRAINT_BONE')
                # box.operator("object.create_toe_heel_rig", text="Toes & Heels Rig")
                self.draw_foot_influence_sliders(context, box, settings)
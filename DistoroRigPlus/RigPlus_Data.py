import bpy
import json

# CSVデータをJSON文字列として保存
bone_data_str = """
[
  {
    "RigPlus": "Root",
    "MMD": "全ての親",
    "Vroid": "root",
    "vrm":-1
  },
  {
    "RigPlus": "center",
    "MMD": "センター",
    "Vroid": "center",
    "vrm":-1
  },
  {
    "RigPlus": "spine",
    "MMD": "上半身0",
    "Vroid": "J_Bip_C_Spine",
    "vrm":7
  },
  {
    "RigPlus": "chest",
    "MMD": "上半身",
    "Vroid": "J_Bip_C_Chest",
    "vrm":8
  },
  {
    "RigPlus": "upper_chest",
    "MMD": "上半身2",
    "Vroid": "J_Bip_C_UpperChest",
    "vrm":53
  },
  {
    "RigPlus": "neck",
    "MMD": "首",
    "Vroid": "J_Bip_C_Neck",
    "vrm":9
  },
  {
    "RigPlus": "head",
    "MMD": "頭",
    "Vroid": "J_Bip_C_Head",
    "vrm":10
  },
  {
    "RigPlus": "L_eye",
    "MMD": "目.L",
    "Vroid": "J_Adj_L_FaceEye",
    "vrm":21
  },
  {
    "RigPlus": "R_eye",
    "MMD": "目.R",
    "Vroid": "J_Adj_R_FaceEye",
    "vrm":22
  },
    {
    "RigPlus": "hips",
    "MMD": "下半身",
    "Vroid": "J_Bip_C_Hips",
    "vrm":0
  },
  {
    "RigPlus": "L_shoulder",
    "MMD": "肩.L",
    "Vroid": "J_Bip_L_Shoulder",
    "vrm":11
  },
  {
    "RigPlus": "L_upper_arm",
    "MMD": "腕.L",
    "Vroid": "J_Bip_L_UpperArm",
    "vrm":13
  },
  {
    "RigPlus": "L_lower_arm",
    "MMD": "ひじ.L",
    "Vroid": "J_Bip_L_LowerArm",
    "vrm":15
  },
  {
    "RigPlus": "L_hand",
    "MMD": "手首.L",
    "Vroid": "J_Bip_L_Hand",
    "vrm":17
  },
  {
    "RigPlus": "L_thumb_1",
    "MMD": "親指０.L",
    "Vroid": "J_Bip_L_Thumb1",
    "vrm":23
  },
  {
    "RigPlus": "L_thumb_2",
    "MMD": "親指１.L",
    "Vroid": "J_Bip_L_Thumb2",
    "vrm":24
  },  {
    "RigPlus": "L_thumb_3",
    "MMD": "親指２.L",
    "Vroid": "J_Bip_L_Thumb3",
    "vrm":25
  },
  {
    "RigPlus": "L_index_1",
    "MMD": "人指１.L",
    "Vroid": "J_Bip_L_Index1",
    "vrm":26
  },
  {
    "RigPlus": "L_index_2",
    "MMD": "人指２.L",
    "Vroid": "J_Bip_L_Index2",
    "vrm":27
  },
  {
    "RigPlus": "L_index_3",
    "MMD": "人指３.L",
    "Vroid": "J_Bip_L_Index3",
    "vrm":28
  },
  {
    "RigPlus": "L_middle_1",
    "MMD": "中指１.L",
    "Vroid": "J_Bip_L_Middle1",
    "vrm":29
  },
  {
    "RigPlus": "L_middle_2",
    "MMD": "中指２.L",
    "Vroid": "J_Bip_L_Middle2",
    "vrm":30
  },
  {
    "RigPlus": "L_middle_3",
    "MMD": "中指３.L",
    "Vroid": "J_Bip_L_Middle3",
    "vrm":31
  },
  {
    "RigPlus": "L_ring_1",
    "MMD": "薬指１.L",
    "Vroid": "J_Bip_L_Ring1",
    "vrm":32
  },
  {
    "RigPlus": "L_ring_2",
    "MMD": "薬指２.L",
    "Vroid": "J_Bip_L_Ring2",
    "vrm":33
  },
  {
    "RigPlus": "L_ring_3",
    "MMD": "薬指３.L",
    "Vroid": "J_Bip_L_Ring3",
    "vrm":34
  },
    {
    "RigPlus": "L_pinky_1",
    "MMD": "小指１.L",
    "Vroid": "J_Bip_L_Little1",
    "vrm":35
  },
  {
    "RigPlus": "L_pinky_2",
    "MMD": "小指２.L",
    "Vroid": "J_Bip_L_Little2",
    "vrm":36
  },
  {
    "RigPlus": "L_pinky_3",
    "MMD": "小指３.L",
    "Vroid": "J_Bip_L_Little3",
    "vrm":37
  },
  {
    "RigPlus": "L_upper_leg",
    "MMD": "足.L",
    "Vroid": "J_Bip_L_UpperLeg",
    "vrm":1
  },
  {
    "RigPlus": "L_lower_leg",
    "MMD": "ひざ.L",
    "Vroid": "J_Bip_L_LowerLeg",
    "vrm":3
  },
  {
    "RigPlus": "L_foot",
    "MMD": "足首.L",
    "Vroid": "J_Bip_L_Foot",
    "vrm":5
  },
  {
    "RigPlus": "L_toeBase",
    "MMD": "つま先.L",
    "Vroid": "J_Bip_L_ToeBase",
    "vrm":19
  },
  {
    "RigPlus": "R_shoulder",
    "MMD": "肩.R",
    "Vroid": "J_Bip_R_Shoulder",
    "vrm":12
  },
  {
    "RigPlus": "R_upper_arm",
    "MMD": "腕.R",
    "Vroid": "J_Bip_R_UpperArm",
    "vrm":14
  },
  {
    "RigPlus": "R_lower_arm",
    "MMD": "ひじ.R",
    "Vroid": "J_Bip_R_LowerArm",
    "vrm":16
  },
    {
    "RigPlus": "R_hand",
    "MMD": "手首.R",
    "Vroid": "J_Bip_R_Hand",
    "vrm":18
  },
  {
    "RigPlus": "R_thumb_1",
    "MMD": "親指０.R",
    "Vroid": "J_Bip_R_Thumb1",
    "vrm":38
  },
  {
    "RigPlus": "R_thumb_2",
    "MMD": "親指１.R",
    "Vroid": "J_Bip_R_Thumb2",
    "vrm":39
  },
  {
    "RigPlus": "R_thumb_3",
    "MMD": "親指２.R",
    "Vroid": "J_Bip_R_Thumb3",
    "vrm":40
  },
  {
    "RigPlus": "R_index_1",
    "MMD": "人指１.R",
    "Vroid": "J_Bip_R_Index1",
    "vrm":41
  },
  {
    "RigPlus": "R_index_2",
    "MMD": "人指２.R",
    "Vroid": "J_Bip_R_Index2",
    "vrm":42
  },
  {
    "RigPlus": "R_index_3",
    "MMD": "人指３.R",
    "Vroid": "J_Bip_R_Index3",
    "vrm":43
  },
  {
    "RigPlus": "R_middle_1",
    "MMD": "中指１.R",
    "Vroid": "J_Bip_R_Middle1",
    "vrm":44
  },
  {
    "RigPlus": "R_middle_2",
    "MMD": "中指２.R",
    "Vroid": "J_Bip_R_Middle2",
    "vrm":45
  },
  {
    "RigPlus": "R_middle_3",
    "MMD": "中指３.R",
    "Vroid": "J_Bip_R_Middle3",
    "vrm":46
  },
  {
    "RigPlus": "R_ring_1",
    "MMD": "薬指１.R",
    "Vroid": "J_Bip_R_Ring1",
    "vrm":47
  },
  {
    "RigPlus": "R_ring_2",
    "MMD": "薬指２.R",
    "Vroid": "J_Bip_R_Ring2",
    "vrm":48
  },
  {
    "RigPlus": "R_ring_3",
    "MMD": "薬指３.R",
    "Vroid": "J_Bip_R_Ring3",
    "vrm":49
  },
  {
    "RigPlus": "R_pinky_1",
    "MMD": "小指１.R",
    "Vroid": "J_Bip_R_Little1",
    "vrm":50
  },
  {
    "RigPlus": "R_pinky_2",
    "MMD": "小指２.R",
    "Vroid": "J_Bip_R_Little2",
    "vrm": 51
  },
  {
    "RigPlus": "R_pinky_3",
    "MMD": "小指３.R",
    "Vroid": "J_Bip_R_Little3",
    "vrm": 52
  },
  {
    "RigPlus": "R_upper_leg",
    "MMD": "足.R",
    "Vroid": "J_Bip_R_UpperLeg",
    "vrm": 2
  },
  {
    "RigPlus": "R_lower_leg",
    "MMD": "ひざ.R",
    "Vroid": "J_Bip_R_LowerLeg",
    "vrm": 4
  },
  {
    "RigPlus": "R_foot",
    "MMD": "足首.R",
    "Vroid": "J_Bip_R_Foot",
    "vrm": 6
  },
  {
    "RigPlus": "R_toeBase",
    "MMD": "つま先.R",
    "Vroid": "J_Bip_R_ToeBase",
    "vrm": 20
  }
]
"""
ik_setting_str = """
[
  {
    "name": "VROID",
    "L_Hand_Pole_angle": 180,
    "L_Hand_Limt_x_min": 0,
    "L_Hand_Limt_x_Max": 0,
    "L_Hand_Limt_z_min": -180,
    "L_Hand_Limt_z_Max": 0,
    "R_Hand_Pole_angle": 0,
    "R_Hand_Limt_x_min": 0,
    "R_Hand_Limt_x_Max": 0,
    "R_Hand_Limt_z_min": 0,
    "R_Hand_Limt_z_Max": 180,
    "L_Foot_Pole_angle": -90,
    "L_Foot_Limt_x_min": 0,
    "L_Foot_Limt_x_Max": 180,
    "L_Foot_Limt_z_min": 0,
    "L_Foot_Limt_z_Max": 0,
    "R_Foot_Pole_angle": -90,
    "R_Foot_Limt_x_min": 0,
    "R_Foot_Limt_x_Max": 180,
    "R_Foot_Limt_z_min": 0,
    "R_Foot_Limt_z_Max": 0
  },
    {
    "name": "MMD",
    "L_Hand_Pole_angle": 45,
    "L_Hand_Limt_x_min": 0,
    "L_Hand_Limt_x_Max": 0,
    "L_Hand_Limt_z_min": 0,
    "L_Hand_Limt_z_Max": 180,
    "R_Hand_Pole_angle": -45,
    "R_Hand_Limt_x_min": 0,
    "R_Hand_Limt_x_Max": 0,
    "R_Hand_Limt_z_min": 0,
    "R_Hand_Limt_z_Max": 180,
    "L_Foot_Pole_angle": -90,
    "L_Foot_Limt_x_min": 0,
    "L_Foot_Limt_x_Max": 180,
    "L_Foot_Limt_z_min": 0,
    "L_Foot_Limt_z_Max": 0,
    "R_Foot_Pole_angle": -90,
    "R_Foot_Limt_x_min": 0,
    "R_Foot_Limt_x_Max": 180,
    "R_Foot_Limt_z_min": 0,
    "R_Foot_Limt_z_Max": 0
  }
]

"""
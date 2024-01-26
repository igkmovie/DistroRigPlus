bl_info = {
    "name": "DistroRigPlus",
     "author": "ig_k",
    "version": (0, 0, 3),  # バージョン番号
    "blender": (2, 80, 0),
    "category": "Object",
}
if "bpy" in locals():
    import imp
    imp.reload(ArmIKCreation)
    imp.reload(RigPlus_Defs)
    imp.reload(FootIKCreation)
    imp.reload(MakeRig)
    imp.reload(Property_Panel)
    imp.reload(RigSetUp)
    imp.reload(ToesHeelsRig)
    imp.reload(TorsoRigCreation)
    imp.reload(IK2FK_FK2IK)
else:
    from . import RigPlus_Defs
    from . import RigSetUp
    from . import MakeRig
    from . import Property_Panel
    from . import TorsoRigCreation
    from . import ArmIKCreation
    from . import FootIKCreation
    from . import ToesHeelsRig
    from . import IK2FK_FK2IK

import bpy
from enum import Enum



def register():
    bpy.utils.register_class(RigSetUp.MapBonesToRigPlus)
    bpy.utils.register_class(RigSetUp.MapBonesToRigPlusTest)
    bpy.utils.register_class(RigPlus_Defs.MessagePopupOperator)
    bpy.utils.register_class(FootIKCreation.CreateLegIKOperator)
    bpy.utils.register_class(ArmIKCreation.CreateWristIKOperator)
    bpy.utils.register_class(MakeRig.MakeRigOperator)
    bpy.utils.register_class(IK2FK_FK2IK.IK2FKRightOperator)
    bpy.utils.register_class(IK2FK_FK2IK.IK2FKLeftOperator)
    bpy.utils.register_class(IK2FK_FK2IK.CopyIKtoFKLeftOperator)
    bpy.utils.register_class(IK2FK_FK2IK.CopyIKtoFKRightOperator)
    bpy.utils.register_class(TorsoRigCreation.CreateTorsoRig)
    bpy.utils.register_class(IK2FK_FK2IK.CopyLeftLegIKtoFKOperator)
    bpy.utils.register_class(IK2FK_FK2IK.CopyRightLegIKtoFKOperator)
    bpy.utils.register_class(IK2FK_FK2IK.IK2FKLeftLegOperator)
    bpy.utils.register_class(IK2FK_FK2IK.IK2FKRightLegOperator)
    bpy.utils.register_class(ToesHeelsRig.OBJECT_OT_CreateToeHeelRig)
    bpy.utils.register_class(Property_Panel.RigPlusSettings)
    bpy.utils.register_class(Property_Panel.IKToolPanel)
    bpy.types.Scene.rigplus_settings = bpy.props.PointerProperty(type=Property_Panel.RigPlusSettings)

def unregister():
    bpy.utils.unregister_class(RigSetUp.MapBonesToRigPlus)
    bpy.utils.unregister_class(RigSetUp.MapBonesToRigPlusTest)
    bpy.utils.unregister_class(RigPlus_Defs.MessagePopupOperator)
    bpy.utils.unregister_class(FootIKCreation.CreateLegIKOperator)
    bpy.utils.unregister_class(MakeRig.MakeRigOperator)
    bpy.utils.unregister_class(ArmIKCreation.CreateWristIKOperator)
    bpy.utils.unregister_class(IK2FK_FK2IK.IK2FKRightOperator)
    bpy.utils.unregister_class(IK2FK_FK2IK.IK2FKLeftOperator)
    bpy.utils.unregister_class(IK2FK_FK2IK.CopyIKtoFKLeftOperator)
    bpy.utils.unregister_class(IK2FK_FK2IK.CopyIKtoFKRightOperator)
    bpy.utils.unregister_class(TorsoRigCreation.CreateTorsoRig)
    bpy.utils.unregister_class(IK2FK_FK2IK.CopyLeftLegIKtoFKOperator)
    bpy.utils.unregister_class(IK2FK_FK2IK.CopyRightLegIKtoFKOperator)
    bpy.utils.unregister_class(IK2FK_FK2IK.IK2FKLeftLegOperator)
    bpy.utils.unregister_class(IK2FK_FK2IK.IK2FKRightLegOperator)
    bpy.utils.unregister_class(ToesHeelsRig.OBJECT_OT_CreateToeHeelRig)
    del bpy.types.Scene.rigplus_settings
    bpy.utils.unregister_class(Property_Panel.IKToolPanel)
    bpy.utils.unregister_class(Property_Panel.RigPlusSettings)

if __name__ == "__main__":
    register()
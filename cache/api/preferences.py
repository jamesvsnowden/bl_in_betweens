
from bpy.types import AddonPreferences
from bpy.props import BoolProperty
from ..lib.update import AddonUpdatePreferences

class InBetweenPreferences(AddonUpdatePreferences, AddonPreferences):
    bl_idname = "in_betweens"

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "In-Betweens",
    "description": "In-between shape keys.",
    "author": "James Snowden",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Properties > data",
    "doc_url": "https://jamesvsnowden.github.io/bl_in_betweens/",
    "tracker_url": "https://github.com/jamesvsnowden/bl_in_betweens/issues",
    "category": "Animation",
}

UPDATE_URL = ""

from .lib.curve_mapping import (BLCMAP_CurvePointProperties,
                                BLCMAP_CurveProperties,
                                BLCMAP_CurvePoint,
                                BLCMAP_CurvePoints,
                                BLCMAP_Curve,
                                BLCMAP_OT_curve_copy,
                                BLCMAP_OT_curve_paste,
                                BLCMAP_OT_node_ensure,
                                BCLMAP_OT_curve_point_remove,
                                BLCMAP_OT_handle_type_set)
from .api.activation_curve import ActivationCurve
from .api.in_between import InBetween
from .api.in_betweens import InBetweens
from .api.target import Target
from .api.preferences import InBetweenPreferences
from .ops.new import INBETWEEN_OT_new
from .ops.select import INBETWEEN_OT_select
from .ops.add import INBETWEEN_OT_add
from .ops.remove import INBETWEEN_OT_remove
from .ops.activate import INBETWEEN_OT_activate
from .gui.hero import INBETWEENS_PT_hero
from .gui.inbetween import INBETWEENS_PT_inbetween
from .gui.inbetweens import INBETWEENS_UL_inbetweens
from .gui.menu import draw_menu_items
from .app.bus import enable_message_broker, MESSAGE_BROKER

def classes():
    return [
        # lib
        BLCMAP_CurvePointProperties,
        BLCMAP_CurveProperties,
        BLCMAP_CurvePoint,
        BLCMAP_CurvePoints,
        BLCMAP_Curve,
        BLCMAP_OT_curve_copy,
        BLCMAP_OT_curve_paste,
        BLCMAP_OT_node_ensure,
        BCLMAP_OT_curve_point_remove,
        BLCMAP_OT_handle_type_set,
        # api
        ActivationCurve,
        InBetween,
        InBetweens,
        InBetweenPreferences,
        Target,
        # ops
        INBETWEEN_OT_new,
        INBETWEEN_OT_select,
        INBETWEEN_OT_add,
        INBETWEEN_OT_remove,
        INBETWEEN_OT_activate,
        # gui
        INBETWEENS_PT_inbetween,
        INBETWEENS_UL_inbetweens,
        INBETWEENS_PT_hero,
        ]

def register():
    import bpy

    BLCMAP_OT_curve_copy.bl_idname = "in_betweens.curve_copy"
    BLCMAP_OT_curve_paste.bl_idname = "in_betweens.curve_paste"
    BLCMAP_OT_node_ensure.bl_idname = "in_betweens.node_ensure"
    BCLMAP_OT_curve_point_remove.bl_idname = "in_betweens.curve_point_remove"
    BLCMAP_OT_handle_type_set.bl_idname = "in_betweens.handle_type_set"

    from .lib import update
    update.register("in_betweens", UPDATE_URL)

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Key.in_betweens = bpy.props.CollectionProperty(
        name="In-Betweens",
        type=InBetweens,
        options=set()
        )

    bpy.types.MESH_MT_shape_key_context_menu.append(draw_menu_items)
    bpy.app.handlers.load_post.append(enable_message_broker)
    enable_message_broker()

def unregister():
    import bpy
    import sys
    import operator

    bpy.msgbus.clear_by_owner(MESSAGE_BROKER)
    bpy.app.handlers.load_post.remove(enable_message_broker)
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_menu_items)

    from .lib import update
    update.unregister()

    try:
        del bpy.types.Key.in_betweens
    except: pass

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)

    modules_ = sys.modules 
    modules_ = dict(sorted(modules_.items(), key=operator.itemgetter(0)))
   
    for name in modules_.keys():
        if name.startswith(__name__):
            del sys.modules[name]
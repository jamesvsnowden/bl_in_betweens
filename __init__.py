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
    "blender": (2, 90, 0),
    "location": "View3D",
    "warning": "",
    "doc_url": "https://in_betweens.github.io",
    "tracker_url": "https://github.com/jamesvsnowden/bl_in_betweens/issues",
    "category": "Animation",
}

import typing
import uuid
import bpy
from .lib import curve_mapping
from .lib.curve_mapping import to_bezier, keyframe_points_assign, draw_curve_manager_ui
from .lib.driver_utils import driver_ensure, driver_find, driver_remove
from .lib.symmetry import symmetrical_split

curve_mapping.BLCMAP_OT_curve_copy.bl_idname = "in_between.curve_copy"
curve_mapping.BLCMAP_OT_curve_paste.bl_idname = "in_between.curve_paste"
curve_mapping.BLCMAP_OT_curve_edit.bl_idname = "in_between.curve_edit"

COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
COMPAT_OBJECTS = {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}

class InBetweenCurveMap(curve_mapping.BCLMAP_CurveManager, bpy.types.PropertyGroup):

    def update(self, context: typing.Optional[bpy.types.Context] = None) -> None:
        super().update(context)
        self.id_data.path_resolve(self.path_from_id().rpartition(".")[0]).update()

class InBetween(bpy.types.PropertyGroup):
    """Manages and stores settings for an in-between shape key"""

    def update(self, context: typing.Optional[bpy.types.Context]=None) -> None:
        fcurve = driver_ensure(self.id_data, f'key_blocks["{self.name}"].value')
        fcurve.mute = self.mute
        points = self.activation_curve.curve.points
        xrange = (self.get_activation_range_min(), self.get_activation_range_max())
        yrange = (0.0, self.value)
        points = to_bezier(points, xrange, yrange, extrapolate=False)
        keyframe_points_assign(fcurve.keyframe_points, points)

    def get_activation_value(self) -> float:
        amin = self.get_activation_range_min()
        amax = self.get_activation_range_max()
        adif = amax - amin
        return self.get("activation_value", amin + adif * 0.5)

    def set_activation_value(self, value: float) -> None:
        amin = self.get_activation_range_min()
        amax = self.get_activation_range_max()
        value = min(max(amin, value), amax)
        if value != self.get_activation_value():
            self["activation_value"] = value
            self.activation_curve.offset = (((value - amin) * 2.0) / (amax - amin)) + -1.0
            key = self.id_data
            hero = key.key_blocks.get(next((x.name for x in key.in_betweens if any((i == self for i in x.data))), ""))
            if hero is not None:
                pfix, base, sfix = symmetrical_split(hero.name)
                target = key.key_blocks.get(self.name)
                if target is not None:
                    target.name = f'{pfix}{base}_{value:.3f}{sfix}'

    activation_value: bpy.props.FloatProperty(
        name="Activation Value",
        description="The value of the shape key around which the in-between is activated",
        min=-10.0,
        max=10.0,
        soft_min=0.0,
        soft_max=1.0,
        get=get_activation_value,
        set=set_activation_value,
        precision=3,
        options=set(),
        )

    activation_curve: bpy.props.PointerProperty(
        name="Curve",
        description="In-Between interpolation curve",
        type=InBetweenCurveMap,
        options=set(),
        update=update
        )

    value: bpy.props.FloatProperty(
        name="Value",
        description="The value of the in-between when fully activated",
        min=0.0,
        max=10.0,
        soft_min=0.1,
        soft_max=1.0,
        default=1.0,
        precision=3,
        options=set(),
        update=update
        )

    identifier: bpy.props.StringProperty(
        name="Shape",
        description="Unique identifier used to hold a reference to the in-between shape key.",
        get=lambda self: self.get("identifier", ""),
        options={'HIDDEN'}
        )

    @property
    def is_valid(self) -> bool:
        """Whether or not a in-between shape key exists"""
        return self.name in self.id_data.key_blocks

    mute: bpy.props.BoolProperty(
        name="Mute",
        description=("Whether or not the in-between shape key's driver is enabled. Disabling "
                     "the driver allows (temporary) editing of the shape key's value in the UI"),
        default=False,
        options=set(),
        update=update
        )

    def get_activation_range_min(self) -> float:
        return self.get("range_min", 0.0)

    def set_activation_range_min(self, value: float) -> None:
        value = min(max(-10.0, min(value, self.activation_value)), 9.999)
        if value != self.get_activation_range_min():
            self["activation_range_min"] = value
            if self.get_activation_range_max() <= value:
                self["activation_range_max"] = value + 0.001
            self.update()

    def get_activation_range_max(self) -> float:
        return self.get("activation_range_max", 1.0)

    def set_activation_range_max(self, value: float) -> None:
        value = min(max(-9.999, max(value, self.activation_value)), 10.0)
        if value != self.get_activation_range_max():
            self["activation_range_max"] = value
            if self.get_activation_range_min() >= value:
                self["activation_range_min"] = value - 0.001
            self.update()

    activation_range_min: bpy.props.FloatProperty(
        name="Activation Min",
        min=-10.0,
        max=9.999,
        get=get_activation_range_min,
        set=set_activation_range_min,
        options=set(),
        )

    activation_range_max: bpy.props.FloatProperty(
        name="Activation Max",
        min=-9.999,
        max=10.0,
        get=get_activation_range_max,
        set=set_activation_range_max,
        options=set(),
        )

class InBetweens(bpy.types.PropertyGroup):

    active_index: bpy.props.IntProperty(
        name="In-Between",
        description="In-Between shape key",
        min=0,
        default=0,
        options=set()
        )

    @property
    def active(self) -> typing.Optional[InBetween]:
        index = self.active_index
        return self[index] if index < len(self) else None

    data: bpy.props.CollectionProperty(
        name="In-Betweens",
        type=InBetween,
        options=set()
        )

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> typing.Iterator[InBetween]:
        return iter(self.data)

    def __getitem__(self, key: typing.Union[int, str, slice]) -> typing.Union[InBetween, typing.List[InBetween]]:
        return self.data[key]

    def get(self, name: str, default: typing.Any) -> typing.Any:
        return self.data.get(name, default)

class InBetweenTarget(bpy.types.PropertyGroup):
    pass

class INBETWEEN_OT_new(bpy.types.Operator):
    
    bl_idname = 'in_between.new'
    bl_label = "New In-Between"
    bl_description = "Add a new in-between shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            return (object is not None
                    and object.type in COMPAT_OBJECTS
                    and object.active_shape_key is not None
                    and object.active_shape_key != object.active_shape_key.id_data.reference_key)
        return False

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data

        inbetweens = key.in_betweens.get(hero.name)

        if inbetweens is None:
            inbetweens = key.in_betweens.add()
            inbetweens["name"] = hero.name

        amin = hero.slider_min
        amax = hero.slider_max
        aval = hero.value

        p, k, s = symmetrical_split(hero.name)
        target = object.shape_key_add(name=f'{p}{k}_{aval:.3f}{s}', from_mix=False)

        inbtwn: InBetween = inbetweens.data.add()
        inbtwn["name"] = target.name
        inbtwn["identifier"] = f'inbetween_{uuid.uuid4().hex}'
        inbtwn["value"] = 1.0
        inbtwn["activation_value"] = aval
        inbtwn["activation_range_min"] = amin
        inbtwn["activation_range_max"] = amax
        inbtwn.activation_curve.__init__(type='BELL',
                                         ramp='HEAD',
                                         interpolation='QUAD',
                                         easing='EASE_IN_OUT',
                                         offset=(((aval - amin) * 2.0) / (amax - amin)) + -1.0)

        fcurve = driver_ensure(key, f'key_blocks["{target.name}"].value')
        driver = fcurve.driver
        driver.type = 'SCRIPTED'
        driver.expression = "var"

        var = driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.name = inbtwn.identifier
        var.targets[0].id_type = 'KEY'
        var.targets[0].id = key
        var.targets[0].data_path = 'reference_key.value'

        var = driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.name = "var"
        var.targets[0].id_type = 'KEY'
        var.targets[0].id = key
        var.targets[0].data_path = f'key_blocks["{hero.name}"].value'

        inbtwn.update()
        inbetweens.active_index = len(inbetweens)-1

        return {'FINISHED'}

class INBETWEEN_OT_select(bpy.types.Operator):
    
    bl_idname = 'in_between.select'
    bl_label = "Select In-Between"
    bl_description = "Select a shape key to add as an in-between"
    bl_options = {'INTERNAL', 'UNDO'}

    targets: bpy.props.CollectionProperty(
        name="Targets",
        type=InBetweenTarget,
        options=set()
        )

    target: bpy.props.StringProperty(
        name="Target",
        default="",
        options=set()
        )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            return (object is not None
                    and object.type in COMPAT_OBJECTS
                    and object.active_shape_key is not None
                    and object.active_shape_key != object.active_shape_key.id_data.reference_key)
        return False

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> typing.Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data
        ref = object.reference_key
        targets = self.targets
        targets.clear()
        for shape in key.key_blocks:
            if (shape != hero
                and shape != ref
                and not driver_find(key, f'key_blocks["{shape.name}"].value')
                ):
                targets.add().name = shape.name
        self.target = ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: bpy.types.Context) -> None:
        self.layout.prop_search(self, "target", self, "targets", icon='SHAPEKEY_DATA', text="")

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data
        target = key.key_blocks.get(self.target)
        if target:

            inbetweens = key.in_betweens.get(hero.name)

            if inbetweens is None:
                inbetweens = key.in_betweens.add()
                inbetweens["name"] = hero.name

            inbtwn: InBetween = inbetweens.data.add()
            inbtwn["name"] = target.name
            inbtwn["identifier"] = f'inbetween_{uuid.uuid4().hex}'
            inbtwn["activation_value"] = hero.value
            inbtwn["activation_radius"] = 1.0-hero.value
            inbtwn.activation_curve.__init__(type='BELL', ramp='HEAD', interpolation='QUAD', easing='EASE_IN_OUT')

            fcurve = driver_ensure(key, f'key_blocks["{target.name}"].value')
            driver = fcurve.driver
            driver.type = 'SCRIPTED'
            driver.expression = "var"

            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = inbtwn.identifier
            var.targets[0].id_type = 'KEY'
            var.targets[0].id = key
            var.targets[0].data_path = 'reference_key.value'

            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            var.targets[0].id_type = 'KEY'
            var.targets[0].id = key
            var.targets[0].data_path = f'key_blocks["{hero.name}"].value'

            inbtwn.update()
            inbetweens.active_index = len(inbetweens)-1

        return {'FINISHED'}

class INBETWEEN_OT_add(bpy.types.Operator):
    
    bl_idname = 'in_between.add'
    bl_label = "Add In-Between"
    bl_description = "Add an in-between"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            return (object is not None
                    and object.type in COMPAT_OBJECTS
                    and object.active_shape_key is not None
                    and object.active_shape_key != object.active_shape_key.id_data.reference_key)
        return False

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.operator(INBETWEEN_OT_new.bl_idname, icon='ADD', text="New In-Between")
        layout.operator(INBETWEEN_OT_select.bl_idname, icon='ANIM', text="Select In-Between")

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        context.window_manager.popup_menu(INBETWEEN_OT_add.draw)
        return {'FINISHED'}

class INBETWEEN_OT_remove(bpy.types.Operator):
    bl_idname = 'in_between.remove'
    bl_label = "Remove In-Between"
    bl_description = "Remove the selected in-between"
    bl_options = {'INTERNAL', 'UNDO'}

    action: bpy.props.EnumProperty(
        name="Action",
        items=[
            ('REMOVE', "Remove", "Remove the in-between but leave the shape key in the list"),
            ('DELETE', "Delete", "Remove and delete the in-between shape key"),
            ],
        default='DELETE',
        options=set()
        )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.use_relative and key.is_property_set("in_betweens"):
                        data = key.in_betweens.get(shape.name)
                        return data is not None and data.active is not None
        return False

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.operator("INBETWEEN_OT_remove", text="Remove In-Between", icon='REMOVE').action='REMOVE'
        layout.operator("INBETWEEN_OT_remove", text="Delete In-Between Shape Key", icon='X').action='DELETE'

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> typing.Set[str]:
        context.window_manager.popup_menu(INBETWEEN_OT_remove.draw)
        return {'FINISHED'}

    def execute(self, context: bpy.types.Context) -> typing.Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data
        inbetweens = key.in_betweens[hero.name]
        data = inbetweens.data
        name = inbetweens.active.name
        driver_remove(key, f'key_blocks["{name}"].value')
        data.remove(data.find(name))
        if self.action == 'DELETE':
            object.shape_key_remove(hero)
        return {'FINISHED'}

class INBETWEENS_UL_inbetweens(bpy.types.UIList):

    def draw_item(self,
                  context: bpy.types.Context,
                  layout: bpy.types.UILayout,
                  data: bpy.types.bpy_prop_collection,
                  item: InBetween,
                  icon, active_data, active_property, index, fltflag) -> None:

        shape = item.id_data.key_blocks.get(item.name)

        row = layout.row()
        row.alert = shape is None
        row.label(icon='SHAPEKEY_DATA', text=item.name)

        if shape:
            row = row.row()
            row.emboss = 'NONE_OR_STATUS'
            row.alignment = 'RIGHT'
            row.prop(shape, "value", text="")

UI_SPLIT = 0.385

def layout_split(layout: bpy.types.UILayout,
                 label: typing.Optional[str]="",
                 align: typing.Optional[bool]=False,
                 factor: typing.Optional[float]=0.385,
                 decorate: typing.Optional[bool]=True,
                 decorate_fill: typing.Optional[bool]=True
                 ) -> typing.Union[bpy.types.UILayout, typing.Tuple[bpy.types.UILayout, ...]]:
    split = layout.row().split(factor=factor)
    col_a = split.column(align=align)
    col_a.alignment = 'RIGHT'
    if label:
        col_a.label(text=label)
    row = split.row()
    col_b = row.column(align=align)
    if decorate:
        col_c = row.column(align=align)
        if decorate_fill:
            col_c.label(icon='BLANK1')
        else:
            return col_a, col_b, col_c
    return col_b if label else (col_a, col_b)

def draw_inbetween_settings(layout: bpy.types.UILayout, settings: InBetween) -> None:

    labels, values = layout_split(layout)
    labels.label(text="Activation  Value")
    values.prop(settings, "activation_value", text="")

    labels, values = layout_split(layout, align=True)
    labels.label(text="Activation Range Min")
    labels.label(text="Max")
    values.prop(settings, "activation_range_min", text="")
    values.prop(settings, "activation_range_max", text="")

    labels, values = layout_split(layout, decorate=False)
    labels.label(text="Activation Curve")
    draw_curve_manager_ui(values, settings.activation_curve)
    layout_split(layout, label="Target Value").prop(settings, "value", text="")

class INBETWEENS_PT_inbetween(bpy.types.Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_label = "In-Between Settings"
    bl_description = "In-Between shape key settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        object = context.object
        if object is not None:
            shape = object.active_shape_key
            if shape is not None:
                key = shape.id_data
                if key.is_property_set("in_betweens"):
                    name = shape.name
                    for inbetweens in key.in_betweens:
                        if name in inbetweens.data:
                            return True
        return False

    def draw(self, context: bpy.types.Context) -> None:
        object = context.object
        target = object.active_shape_key
        name = target.name
        key = target.id_data
        for inbetweens in key.in_betweens:
            inbetween = inbetweens.data.get(name)
            if inbetween:
                layout = self.layout
                region = layout_split(layout, "Hero Shape Key")
                region.enabled = False
                region.alert = inbetweens.name not in key.key_blocks
                region.prop(inbetween, "name", icon='SHAPEKEY_DATA', text="")
                draw_inbetween_settings(layout, inbetween)
                return

class INBETWEENS_PT_hero(bpy.types.Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_label = "In-Betweens"
    bl_description = "In-Between shape key settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        object = context.object
        if object is not None:
            shape = object.active_shape_key
            if shape is not None:
                key = shape.id_data
                return (key.is_property_set("in_betweens")
                        and shape.name in key.in_betweens
                        and len(key.in_betweens[shape.name]) > 0)
        return False

    def draw(self, context: bpy.types.Context) -> None:
        obj = context.object
        key = obj.data.shape_keys
        inbetweens = key.in_betweens[obj.active_shape_key.name]
        layout = self.layout

        row = layout.row()
        row.column().template_list("INBETWEENS_UL_inbetweens", "",
                                   inbetweens, "data",
                                   inbetweens, "active_index")

        column = row.column(align=True)
        column.operator_context = 'INVOKE_DEFAULT'
        column.operator(INBETWEEN_OT_add.bl_idname, text="", icon='ADD')
        column.operator(INBETWEEN_OT_remove.bl_idname, text="", icon='REMOVE')

        active = inbetweens.active
        if active:
            draw_inbetween_settings(layout, active)

def draw_menu_items(menu: bpy.types.Menu, context: bpy.types.Context) -> None:
    object = context.object
    if object is not None:
        shape = object.active_shape_key
        if shape is not None:
            key = shape.id_data
            if shape != key.reference_key:
                layout = menu.layout
                layout.separator()
                layout.operator(INBETWEEN_OT_new.bl_idname,
                                icon='ADD',
                                text="New In-Between")
                layout.operator(INBETWEEN_OT_select.bl_idname,
                                icon='ANIM',
                                text="Select In-Between")

MESSAGE_BROKER = object()

def shape_key_name_callback():
    for key in bpy.data.shape_keys:
        if key.is_property_set("in_betweens"):
            animdata = key.animation_data
            if animdata:
                data = {}
                for hero in key.in_betweens:
                    for item in hero:
                        data[item.identifier] = (item, hero)
                if data:
                    umap = {}
                    for fc in animdata.drivers:
                        vars = fc.driver.variables
                        if len(vars) == 2:
                            k = vars[0].name
                            if k.startswith("inbetween_") and k in data:
                                item, hero = data[k]
                                item_name = item["name"] = fc.data_path[12:-8]
                                hero_name = hero["name"] = vars[1].targets[0].data_path[12:-8]
                                if not item_name.startswith(hero_name):
                                    umap.setdefault(hero, []).append(item)
                    if umap:
                        kbs = key.key_blocks
                        for hero, items in umap.items():
                            pfix, base, sfix = symmetrical_split(hero.name)
                            for item in items:
                                kb = kbs.get(item.name)
                                if kb is not None:
                                    kb.name = item["name"] = f'{pfix}{base}_{item.activation_value:.3f}{sfix}'


@bpy.app.handlers.persistent
def enable_message_broker(_=None) -> None:
    bpy.msgbus.clear_by_owner(MESSAGE_BROKER)
    bpy.msgbus.subscribe_rna(key=(bpy.types.ShapeKey, "name"),
                             owner=MESSAGE_BROKER,
                             args=tuple(),
                             notify=shape_key_name_callback)

CLASSES = [
    curve_mapping.BLCMAP_CurvePointProperties,
    curve_mapping.BLCMAP_CurveProperties,
    curve_mapping.BLCMAP_CurvePoint,
    curve_mapping.BLCMAP_CurvePoints,
    curve_mapping.BLCMAP_Curve,
    curve_mapping.BLCMAP_OT_curve_copy,
    curve_mapping.BLCMAP_OT_curve_paste,
    curve_mapping.BLCMAP_OT_curve_edit,
    InBetweenCurveMap,
    InBetween,
    InBetweens,
    InBetweenTarget,
    INBETWEEN_OT_new,
    INBETWEEN_OT_select,
    INBETWEEN_OT_add,
    INBETWEEN_OT_remove,
    INBETWEENS_UL_inbetweens,
    INBETWEENS_PT_inbetween,
    INBETWEENS_PT_hero,
    ]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Key.in_betweens = bpy.props.CollectionProperty(
        name="In-Betweens",
        type=InBetweens,
        options=set()
        )

    bpy.types.MESH_MT_shape_key_context_menu.append(draw_menu_items)
    bpy.app.handlers.load_post.append(enable_message_broker)
    enable_message_broker() # Ensure messages are subscribed to on first install

def unregister():
    bpy.msgbus.clear_by_owner(MESSAGE_BROKER)
    bpy.app.handlers.load_post.remove(enable_message_broker)
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_menu_items)

    try:
        del bpy.types.Key.in_betweens
    except: pass

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

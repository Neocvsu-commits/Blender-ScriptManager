"""Blender 脚本管理器 — 浏览、搜索、一键执行自定义 Python 脚本。"""

bl_info = {
    "name": "脚本管理器",
    "author": "高迪",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D View > Sidebar > Scripts",
    "description": "集中管理自定义 Python 脚本：浏览、搜索、一键执行",
    "category": "3D View",
}

import ast
import os
import traceback

import bpy


# ============================================================
# Constants
# ============================================================

ADDON_ID = "blender_script_manager"

# ============================================================
# Script scanning
# ============================================================

_script_cache = []


def _extract_description(filepath):
    """Extract the first meaningful line of a Python file's docstring."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree)
        if docstring:
            line = docstring.strip().split('\n')[0].rstrip('。.；;')
            if line and not line.startswith('Blender'):
                return line
            # If first line is just "Blender x.x：...", try second line
            lines = [l.strip() for l in docstring.split('\n') if l.strip()]
            for l in lines:
                if l and not l.startswith('Blender'):
                    return l.rstrip('。.；;')
            return lines[0].rstrip('。.；;') if lines else ""
    except Exception:
        pass
    return ""


def scan_scripts(directory):
    """Populate _script_cache from .py files in *directory*."""
    global _script_cache
    _script_cache.clear()

    if not directory or not os.path.isdir(directory):
        return

    for fname in sorted(os.listdir(directory)):
        if not fname.endswith('.py') or fname.startswith('_'):
            continue
        fpath = os.path.join(directory, fname)
        if not os.path.isfile(fpath):
            continue
        _script_cache.append({
            'name': fname[:-3],                  # strip .py
            'path': fpath,
            'description': _extract_description(fpath),
        })


# ============================================================
# UI state
# ============================================================

class SCRIPTMANAGER_PG_settings(bpy.types.PropertyGroup):
    search: bpy.props.StringProperty(           # type: ignore[valid-type]
        name="Search",
        description="Filter scripts by name or description",
        default="",
        options={'TEXTEDIT_UPDATE'},
    )


# ============================================================
# Operators
# ============================================================

class SCRIPTMANAGER_OT_refresh(bpy.types.Operator):
    """Re-scan the script directory for .py files."""
    bl_idname = "scriptmanager.refresh"
    bl_label = "Refresh Script List"

    def execute(self, context):
        addon = context.preferences.addons.get(ADDON_ID)
        if addon:
            scan_scripts(addon.preferences.script_directory)
        count = len(_script_cache)
        self.report({'INFO'}, f"Found {count} script{'s' if count != 1 else ''}")
        return {'FINISHED'}


class SCRIPTMANAGER_OT_execute(bpy.types.Operator):
    """Execute this script and report any errors to the console."""
    bl_idname = "scriptmanager.execute"
    bl_label = "Execute Script"

    script_path: bpy.props.StringProperty()     # type: ignore[valid-type]
    script_name: bpy.props.StringProperty()     # type: ignore[valid-type]

    def execute(self, context):
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                source = f.read()
            code = compile(source, self.script_path, 'exec')
            namespace = {"__name__": "__main__", "__file__": self.script_path}
            exec(code, namespace)
            self.report({'INFO'}, f"'{self.script_name}' — done")
        except Exception:
            traceback.print_exc()
            self.report({'ERROR'}, f"'{self.script_name}' failed — see console")
        return {'FINISHED'}


class SCRIPTMANAGER_OT_edit(bpy.types.Operator):
    """Open this script in the system default editor for .py files."""
    bl_idname = "scriptmanager.edit"
    bl_label = "Edit Script"

    script_path: bpy.props.StringProperty()     # type: ignore[valid-type]
    script_name: bpy.props.StringProperty()     # type: ignore[valid-type]

    def execute(self, context):
        if not os.path.isfile(self.script_path):
            self.report({'ERROR'}, f"File not found: {self.script_path}")
            return {'CANCELLED'}
        os.startfile(self.script_path)
        self.report({'INFO'}, f"Editing '{self.script_name}' — save then Refresh + Run")
        return {'FINISHED'}


class SCRIPTMANAGER_OT_open_folder(bpy.types.Operator):
    """Open the script directory in the system file manager."""
    bl_idname = "scriptmanager.open_folder"
    bl_label = "Open Script Folder"

    def execute(self, context):
        addon = context.preferences.addons.get(ADDON_ID)
        if not addon:
            return {'CANCELLED'}
        directory = addon.preferences.script_directory
        if directory and os.path.isdir(directory):
            os.startfile(directory)             # Windows
        else:
            self.report({'ERROR'}, "Directory does not exist")
        return {'FINISHED'}


# ============================================================
# Panel
# ============================================================

class SCRIPTMANAGER_PT_panel(bpy.types.Panel):
    bl_label = "Script Manager"
    bl_idname = "SCRIPTMANAGER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Scripts"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.scriptmanager_settings
        addon = context.preferences.addons.get(ADDON_ID)
        if not addon:
            layout.label(text="Addon not found", icon='ERROR')
            return
        prefs = addon.preferences

        # ── search ──
        layout.prop(settings, "search", text="", icon='VIEWZOOM')

        # ── toolbar row ──
        row = layout.row(align=True)
        row.operator("scriptmanager.open_folder", text="Folder", icon='FILEBROWSER')
        row.operator("scriptmanager.refresh", text="Refresh", icon='FILE_REFRESH')

        # ── directory guard ──
        directory = prefs.script_directory
        if not directory:
            layout.label(text="Set script directory in Preferences", icon='ERROR')
            return
        if not os.path.isdir(directory):
            layout.label(text=f"Not found: {directory}", icon='ERROR')
            return

        layout.separator()

        # ── filter ──
        search_term = settings.search.lower().strip()
        if search_term:
            scripts = [
                s for s in _script_cache
                if search_term in s['name'].lower() or search_term in s['description'].lower()
            ]
        else:
            scripts = _script_cache

        layout.label(text=f"{len(scripts)} of {len(_script_cache)} scripts")

        # ── list ──
        if not scripts:
            layout.separator()
            msg = "No matching scripts" if search_term else "No .py files in directory"
            layout.label(text=msg, icon='INFO')
            return

        layout.separator()
        for script in scripts:
            row = layout.row(align=True)
            # ── run ──
            SCRIPTMANAGER_OT_execute.__doc__ = script['description'] or "Execute script"
            op_run = row.operator(
                "scriptmanager.execute",
                text=script['name'],
                icon='FILE_SCRIPT',
            )
            op_run.script_path = script['path']
            op_run.script_name = script['name']
            # ── edit ──
            op_edit = row.operator(
                "scriptmanager.edit",
                text="",
                icon='TEXT',
            )
            op_edit.script_path = script['path']
            op_edit.script_name = script['name']


# ============================================================
# Preferences
# ============================================================

class SCRIPTMANAGER_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID

    script_directory: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="Script Directory",
        description="Folder containing .py scripts to manage",
        subtype='DIR_PATH',
        default=r"E:\Users\Administrator\Desktop\Blender脚本整理",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "script_directory")
        layout.separator()
        row = layout.row(align=True)
        row.label(text=f"Scripts found: {len(_script_cache)}")
        row.operator("scriptmanager.refresh", text="Scan Now", icon='FILE_REFRESH')


# ============================================================
# Registration
# ============================================================

_classes = [
    SCRIPTMANAGER_PG_settings,
    SCRIPTMANAGER_OT_refresh,
    SCRIPTMANAGER_OT_execute,
    SCRIPTMANAGER_OT_edit,
    SCRIPTMANAGER_OT_open_folder,
    SCRIPTMANAGER_PT_panel,
    SCRIPTMANAGER_AddonPreferences,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.scriptmanager_settings = bpy.props.PointerProperty(
        type=SCRIPTMANAGER_PG_settings
    )

    # Initial scan
    try:
        addon = bpy.context.preferences.addons.get(ADDON_ID)
        if addon:
            scan_scripts(addon.preferences.script_directory)
    except Exception:
        pass


def unregister():
    if hasattr(bpy.types.Scene, 'scriptmanager_settings'):
        del bpy.types.Scene.scriptmanager_settings

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

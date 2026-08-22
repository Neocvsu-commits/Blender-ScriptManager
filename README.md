# Blender 脚本管理器

Blender 插件的 N 面板标签页，集中管理你积累的 Python 脚本——浏览、搜索、一键执行、直接编辑。

## 功能

| 操作 | 说明 |
|---|---|
| 搜索 | 实时过滤，匹配脚本**文件名**和 **docstring 描述** |
| 执行 | 点击脚本名右侧 ▶ 按钮，通过 `exec()` 在 Blender 上下文中运行 |
| 编辑 | 点击 ✏ 按钮，用系统默认编辑器打开 `.py` 文件 |
| 目录 | `Folder` 按钮在资源管理器中打开脚本目录 |
| 刷新 | `Refresh` 按钮重新扫描目录（新增/删除脚本后使用） |

- 面板顶部显示当前过滤状态：`{N} of {M} scripts`
- 执行结果/错误输出到 Blender 控制台（Window → Toggle System Console）
- 以 `_` 开头的 `.py` 文件自动排除（用于放工具模块、共享函数）

## 界面

3D View 按 `N` → 侧边栏 `Scripts` 标签页：

```
┌─────────────────────────────────┐
│ 🔍 [搜索框]                      │
│ [Folder]  [Refresh]             │
│ ─────────────────────────────── │
│ 3 of 12 scripts                 │
│ ─────────────────────────────── │
│ 📄 export_fbx          ✏       │
│ 📄 batch_rename        ✏       │
│ 📄 clean_mesh          ✏       │
└─────────────────────────────────┘
```

## 安装

1. Blender → Edit → Preferences → Add-ons → Install
2. 选择 `script_manager.py`
3. 勾选启用
4. 在偏好设置中指定**脚本目录**（默认 `E:\Users\Administrator\Desktop\Blender脚本整理`）

## 添加新脚本

1. 把 `.py` 文件放入脚本目录（文件名不以 `_` 开头）
2. 给文件加上 docstring，面板自动提取第一行作为副标题
3. 在 Blender 中点 `Refresh`

```python
"""批量导出选中对象为独立的 FBX 文件。"""

import bpy

# === 配置区 ===
OUTPUT_DIR = "//exports/"
# === 结束 ===

# ... 你的逻辑 ...
```

- docstring 以 `Blender` 开头的行会被跳过，自动取后续有效行
- 脚本执行时注入 `__name__ = "__main__"` 和 `__file__` 指向实际路径
- 可正常使用 `bpy`、`import` 等所有 Blender Python API

## 迭代协议

版本号遵循 `MAJOR.MINOR.PATCH`，对应 `bl_info["version"]` 元组 `(MAJOR, MINOR, PATCH)`。

### 版本号规则

| 段位 | 触发条件 | 示例 |
|---|---|---|
| PATCH | Bug 修复、文案修正、不影响 API 的微调 | `1.0.0` → `1.0.1` |
| MINOR | 新增功能、新增 operator/panel/属性 | `1.0.1` → `1.1.0` |
| MAJOR | 破坏性变更：bl_idname 改名、preferences 键变更、不再兼容旧 Blender 版本 | `1.1.0` → `2.0.0` |

### 发布前检查

- [ ] `bl_info["version"]` 已更新
- [ ] README 功能描述与代码实际行为一致
- [ ] 在目标 Blender 版本上启用/禁用/重新启用无报错
- [ ] Git commit message 以版本号开头（如 `v1.1.0: 新增编辑按钮`）
- [ ] commit 后打 tag：`git tag v1.1.0`，`git push --tags`

### 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-07-24 | 初始发布：脚本浏览、搜索过滤、一键执行、系统编辑器打开、文件夹管理 |

## 兼容性

- Blender 4.x（3.x 应也可用，未测）
- Windows（`os.startfile`）—— 如需 macOS/Linux 支持，替换 `open_folder` 和 `edit` 中的 `os.startfile`

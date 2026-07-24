# Blender 脚本管理器

Blender 插件的 N 面板标签页，集中管理你积累的 Python 脚本——浏览、搜索、一键执行。

## 安装

1. Blender → Edit → Preferences → Add-ons → Install
2. 选择 `blender_script_manager.py`
3. 勾选启用
4. 在偏好设置中指定**脚本目录**（默认 `E:\Users\Administrator\Desktop\Blender脚本整理`）

## 使用

- 按 `N` 打开侧边栏 → `Scripts` 标签页
- 搜索框实时过滤脚本名称和描述
- 点击 ▶ 按钮在 Blender 上下文执行脚本
- 执行结果输出到 Blender 控制台（Window → Toggle System Console）
- `Folder` 按钮在资源管理器中打开脚本目录
- `Refresh` 按钮重新扫描目录（新增/删除脚本后使用）

## 添加新脚本

1. 把 `.py` 文件放入脚本目录
2. 给文件加上 docstring（`"""一行描述"""`），面板会自动提取作为副标题
3. 在 Blender 中点 `Refresh`

脚本格式参考：

```python
"""批量导出选中对象为独立的 FBX 文件。"""

import bpy

# === 配置区 ===
OUTPUT_DIR = "//exports/"
# === 结束 ===

# ... 你的逻辑 ...
```

脚本通过 `exec()` 执行，可以正常使用 `bpy`、`import` 等所有 Blender Python API。

## 兼容性

- Blender 4.x（3.x 应也可用，未测）
- Windows（`os.startfile`）—— 如需 macOS/Linux 支持，替换 `open_folder` 中的 `os.startfile`

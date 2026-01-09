# -*- coding: utf-8 -*-
import os
from pathlib import Path

# ==================== 配置区 ====================
# 要处理的扩展名
TARGET_EXTENSIONS = {'.svelte', '.js'}

# 输出目录结构的文件名
TREE_OUTPUT = "tree.txt"

# 是否要包含文件内容里每一行的行号（可选）
SHOW_LINE_NUMBERS = True
# ===============================================

def get_tree_structure(start_path='.'):
    """生成类似 tree 命令的目录结构"""
    lines = []
    prefix = "📁 "
    
    def walk(directory, prefix=""):
        contents = sorted(os.listdir(directory))
        pointers = ["├── "] * (len(contents) - 1) + ["└── "] if contents else []
        
        for pointer, name in zip(pointers, contents):
            path = os.path.join(directory, name)
            if os.path.isdir(path):
                lines.append(f"{prefix}{pointer}📁 {name}/")
                extension = "│   " if pointer == "├── " else "    "
                walk(path, prefix + extension)
            else:
                icon = "📄 " if name.endswith(('.svelte', '.js', '.ts', '.json', '.css')) else ""
                lines.append(f"{prefix}{pointer}{icon}{name}")
    
    root_name = os.path.basename(os.path.abspath(start_path)) or "."
    lines.append(f"📁 ./{root_name}")
    walk(start_path)
    
    return '\n'.join(lines)


def extract_folder_content():
    """把每个子文件夹中的 .svelte 和 .js 文件内容输出到 对应文件夹名.txt"""
    root = Path('.').resolve()
    
    # 先收集所有要处理的子文件夹
    folders = [p for p in root.iterdir() if p.is_dir()]
    
    for folder in folders:
        output_file = f"{folder.name}.txt"
        contents = []
        
        # 遍历这个文件夹下的所有文件（包括深层子目录）
        for file_path in folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in TARGET_EXTENSIONS:
                try:
                    rel_path = file_path.relative_to(folder)
                    contents.append(f"\n{'='*60}")
                    contents.append(f"文件: {rel_path}")
                    contents.append(f"{'-'*60}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if SHOW_LINE_NUMBERS:
                            for i, line in enumerate(lines, 1):
                                contents.append(f"{i:4d} | {line.rstrip()}")
                        else:
                            contents.append(''.join(lines))
                            
                except Exception as e:
                    contents.append(f"[读取错误] {file_path} : {e}")
        
        # 写出文件
        if contents:  # 只有真的有内容才生成文件
            with open(output_file, 'w', encoding='utf-8') as out:
                out.write(f"文件夹：{folder.name}\n")
                out.write(f"生成时间：当前目录下所有 .svelte / .js 文件内容\n\n")
                out.write('\n'.join(contents))
            print(f"已生成：{output_file} ({len(contents)} 行内容)")
        else:
            print(f"文件夹 {folder.name} 没有找到 .svelte 或 .js 文件，跳过")


def main():
    print("正在生成各文件夹的内容汇总文件...\n")
    
    # 1. 生成各文件夹的 .txt 汇总
    extract_folder_content()
    
    print("\n" + "="*70)
    print("2. 正在生成目录树结构到 tree.txt ...")
    
    # 2. 生成 tree.txt
    tree_content = get_tree_structure()
    with open(TREE_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(tree_content)
    
    print(f"目录结构已保存到：{TREE_OUTPUT}")
    print("完成！")


if __name__ == "__main__":
    main()
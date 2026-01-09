import os

# --- 配置项 ---
target_dir = '.'  # 当前目录
summary_file = 'summary.txt'
tree_file = 'tree.txt'
# 建议排除的无关目录，避免扫描 node_modules 导致卡顿
exclude_dirs = {'.git', 'node_modules', '__pycache__', '.svelte-kit', 'dist'}

def run_task():
    summary_list = []
    tree_list = []

    # 使用 os.walk 递归遍历
    for root, dirs, files in os.walk(target_dir):
        # 实时过滤掉不需要扫描的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # 计算当前目录在 tree 中的缩进层级
        level = root.replace(target_dir, '').count(os.sep)
        indent = '  ' * level
        folder_name = os.path.basename(root) or target_dir
        tree_list.append(f"{indent}📁 {folder_name}/")
        
        sub_indent = '  ' * (level + 1)
        
        for file in files:
            # 记录所有文件到 tree.txt
            tree_list.append(f"{sub_indent}📄 {file}")
            
            # 仅处理 .svelte 文件到 summary.txt
            if file.endswith('.svelte'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 严格按照要求的格式：文件名 + 冒号 + 内容
                        summary_list.append(f"{file}:\n{content}\n")
                except Exception as e:
                    summary_list.append(f"{file}:\n[读取文件时出错: {e}]\n")

    # 写入 tree.txt (所有文件结构)
    with open(tree_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tree_list))

    # 写入 summary.txt (.svelte 内容)
    # 使用 "\n" 分隔每个文件的区块
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_list))

    print(f"✅ 执行成功！")
    print(f"📂 目录树已生成: {tree_file}")
    print(f"📝 汇总内容已生成: {summary_file}")

if __name__ == "__main__":
    run_task()
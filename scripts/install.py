#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

def copy_skills(source_dir: Path, target_dir: Path):
    """
    将 source_dir 下的所有 skill 复制到 target_dir。
    """
    # 确保源目录存在
    if not source_dir.exists():
        print(f"错误: 源目录不存在: {source_dir}")
        return

    # 展开用户路径 (处理 ~)
    target_dir = target_dir.expanduser().resolve()

    try:
        # 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n正在安装 Skills 到: {target_dir}")
    except Exception as e:
        print(f"错误: 无法创建目标目录 {target_dir}: {e}")
        return

    # 获取源目录下的所有项目
    items = sorted([item for item in source_dir.iterdir() if item.is_dir()])

    if not items:
        print("源目录中没有找到任何 Skill 目录。")
        return

    success_count = 0
    fail_count = 0

    for item in items:
        skill_name = item.name
        # 忽略隐藏目录
        if skill_name.startswith('.'):
            continue

        dest_path = target_dir / skill_name

        try:
            # 使用 dirs_exist_ok=True 允许覆盖/合并现有目录 (需 Python 3.8+)
            if sys.version_info >= (3, 8):
                shutil.copytree(item, dest_path, dirs_exist_ok=True)
            else:
                # 兼容旧版本 Python: 如果存在则先删除
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(item, dest_path)

            print(f"  [✓] 已安装: {skill_name}")
            success_count += 1
        except Exception as e:
            print(f"  [✗] 安装 {skill_name} 失败: {e}")
            fail_count += 1

    print(f"完成! 成功: {success_count}, 失败: {fail_count}")

def main():
    # 获取脚本所在目录的上一级目录 (项目根目录)
    current_script_path = Path(__file__).resolve()
    project_root = current_script_path.parent.parent
    source_skills_dir = project_root / 'skills'

    print(f"源 Skill 目录: {source_skills_dir}")

    # 1. 安装到默认目录 ~/.agents/skills
    default_target_dir = Path("~/.agents/skills")
    copy_skills(source_skills_dir, default_target_dir)

    # 2. 交互式询问是否安装到其他目录
    while True:
        try:
            print("\n" + "-"*50)
            user_input = input("是否需要安装到其他目录？\n请输入目录路径 (直接回车跳过/退出): ").strip()

            if not user_input:
                break

            custom_target_dir = Path(user_input)
            copy_skills(source_skills_dir, custom_target_dir)

        except KeyboardInterrupt:
            print("\n操作已取消。")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()

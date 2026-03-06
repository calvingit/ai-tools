#!/usr/bin/env bash

# 设置错误退出和变量展开检查
set -e

# 获取脚本所在目录的上一级目录作为项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 默认安装目录
DEFAULT_INSTALL_DIR="$HOME/.agents/skills"
DEFAULT_LINK_DIR="$HOME/.claude/skills"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 辅助函数：将单个源目录安装到目标目录
install_source_dir() {
    local source_dir="$1"
    local target_dir="$2"

    if [ ! -d "$source_dir" ]; then
        log_error "源目录不存在: $source_dir"
        return 1
    fi

    log_info "正在从 [$(basename "$source_dir")] 安装 Skills 到: $target_dir"
    mkdir -p "$target_dir"

    local success_count=0
    local fail_count=0

    # 遍历源目录下的子目录
    for skill_path in "$source_dir"/*; do
        if [ -d "$skill_path" ]; then
            skill_name=$(basename "$skill_path")

            # 忽略隐藏目录
            if [[ "$skill_name" == .* ]]; then
                continue
            fi

            target_path="$target_dir/$skill_name"

            # 删除旧版本并复制新版本
            rm -rf "$target_path"
            if cp -R "$skill_path" "$target_path"; then
                echo "  [✓] 已安装: $skill_name"
                ((success_count++))
            else
                echo "  [✗] 安装 $skill_name 失败"
                ((fail_count++))
            fi
        fi
    done

    echo "  -> 结果: 成功 $success_count, 失败 $fail_count"
}

# 辅助函数：将目标目录的 skills 链接到其他位置
link_skills() {
    local source_base="$1"
    local target_base="$2"

    if [ ! -d "$source_base" ]; then
        log_error "源基准目录不存在，无法创建链接: $source_base"
        return 1
    fi

    log_info "正在更新软链接: $target_base"
    mkdir -p "$target_base"

    local link_count=0

    # 遍历已安装的 skills 目录
    for skill_path in "$source_base"/*; do
        if [ -d "$skill_path" ]; then
            skill_name=$(basename "$skill_path")
            target_link="$target_base/$skill_name"

            # 创建软链接 (强制覆盖)
            if ln -sf "$skill_path" "$target_link"; then
                # echo "  [🔗] 已链接: $skill_name" # 减少输出噪音
                ((link_count++))
            else
                echo "  [✗] 链接 $skill_name 失败"
            fi
        fi
    done

    echo "  -> 已更新链接数: $link_count"
}

main() {
    local target_arg="${1:-skills}" # 默认为 skills
    local skills_dirs=()

    # 解析参数
    if [[ "$target_arg" == "all" ]]; then
        # 查找 skills 目录
        if [ -d "$PROJECT_ROOT/skills" ]; then
            skills_dirs+=("$PROJECT_ROOT/skills")
        fi
        # 查找所有以 -skills 结尾的目录
        while IFS= read -r dir; do
            skills_dirs+=("$dir")
        done < <(find "$PROJECT_ROOT" -maxdepth 1 -type d -name "*-skills")
    else
        # 指定目录
        local specified_dir="$PROJECT_ROOT/$target_arg"
        if [ -d "$specified_dir" ]; then
            skills_dirs+=("$specified_dir")
        else
            log_error "指定的目录不存在: $specified_dir"
            exit 1
        fi
    fi

    if [ ${#skills_dirs[@]} -eq 0 ]; then
        log_error "未找到任何可安装的 Skills 目录"
        exit 1
    fi

    # 1. 执行安装
    for src_dir in "${skills_dirs[@]}"; do
        install_source_dir "$src_dir" "$DEFAULT_INSTALL_DIR"
    done

    # 2. 默认创建软链接到 ~/.claude/skills
    link_skills "$DEFAULT_INSTALL_DIR" "$DEFAULT_LINK_DIR"

    # 3. 交互式询问
    while true; do
        echo ""
        echo "--------------------------------------------------"
        read -r -p "是否需要将 Skills 链接到其他目录？(请输入目录路径，直接回车跳过/退出): " user_input

        user_input=$(echo "$user_input" | xargs)

        if [ -z "$user_input" ]; then
            break
        fi

        # 处理用户输入的路径 (支持 ~)
        target_link_dir="${user_input/#\~/$HOME}"
        link_skills "$DEFAULT_INSTALL_DIR" "$target_link_dir"
    done

    echo -e "${GREEN}所有操作已完成。${NC}"
}

main "$@"

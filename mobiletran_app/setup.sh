#!/data/data/com.termux/files/usr/bin/bash
# ============================================
# MobileTran - Termux 安装脚本
# 用于安装 Termux + Ollama 翻译工具所需环境
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║           📱 MobileTran 安装脚本                 ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查是否在 Termux 环境
if [ ! -d "/data/data/com.termux" ] && [ ! -f "$PREFIX/bin/termux-info" ]; then
    echo -e "${YELLOW}⚠ 警告: 未检测到 Termux 环境"
    echo -e "此脚本专为 Termux 设计，请确保在 Termux 中运行${NC}"
fi

# 1. 更新包管理器
echo -e "\n${CYAN}[1/6] 更新 Termux 包管理器...${NC}"
pkg update -y && pkg upgrade -y

# 2. 安装必要的系统包
echo -e "\n${CYAN}[2/6] 安装必要的系统工具...${NC}"
pkg install -y python python-pip git curl cmake build-essential

# 3. 安装 Python 依赖
echo -e "\n${CYAN}[3/6] 安装 Python 依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 4. 检查 Ollama 是否已安装
echo -e "\n${CYAN}[4/6] 检查 Ollama 状态...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama 已安装${NC}"
else
    echo -e "${YELLOW}⚠ Ollama 未安装"
    echo -e "请在 Termux 中手动安装 Ollama:${NC}"
    echo -e "  ${CYAN}curl -fsSL https://ollama.com/install.sh | sh${NC}"
    echo -e "  ${YELLOW}或参考: https://github.com/termux/termux-packages/wiki/Ollama${NC}"
fi

# 5. 检查翻译模型
echo -e "\n${CYAN}[5/6] 检查翻译模型...${NC}"
if command -v ollama &> /dev/null; then
    MODELS=$(ollama list 2>/dev/null | grep "Hy-MT1.5" || true)
    if [ -n "$MODELS" ]; then
        echo -e "${GREEN}✅ 翻译模型 Hy-MT1.5 已安装${NC}"
    else
        echo -e "${YELLOW}⚠ 翻译模型 Hy-MT1.5 未安装"
        echo -e "正在下载模型 (约 1GB)...${NC}"
        echo -e "${CYAN}ollama pull Hy-MT1.5-1.8B-1.25bit${NC}"
        ollama pull Hy-MT1.5-1.8B-1.25bit || {
            echo -e "${YELLOW}⚠ 自动下载失败，请手动执行以下命令:${NC}"
            echo -e "  ${CYAN}ollama pull Hy-MT1.5-1.8B-1.25bit${NC}"
        }
    fi
else
    echo -e "${YELLOW}⚠ 请先安装 Ollama，然后手动下载模型:${NC}"
    echo -e "  ${CYAN}ollama pull Hy-MT1.5-1.8B-1.25bit${NC}"
fi

# 6. 创建快捷启动脚本
echo -e "\n${CYAN}[6/6] 创建快捷启动方式...${NC}"

# 创建 termux-url-opener 配置(可选:支持从文件管理器直接打开文本翻译)
OPENNER_DIR="$HOME/bin"
mkdir -p "$OPENNER_DIR"

# 创建启动脚本
cat > "$PREFIX/bin/mobiletran" << 'SCRIPT_EOF'
#!/data/data/com.termux/files/usr/bin/bash
# MobileTran 启动脚本
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
TRANSLATE_DIR="$(find /data/data/com.termux/files/home -type d -name "mobiletran_app" 2>/dev/null | head -1)"

if [ -z "$TRANSLATE_DIR" ]; then
    # 尝试当前目录
    if [ -f "$(dirname "$0")/../translate.py" ]; then
        TRANSLATE_DIR="$(dirname "$0")/.."
    else
        echo -e "\033[31m❌ 未找到 MobileTran 程序目录\033[0m"
        echo "请先进入 mobiletran_app 目录运行"
        exit 1
    fi
fi

cd "$TRANSLATE_DIR"

# 检查 Ollama 是否运行
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "\033[33m⚠ Ollama 未运行，正在启动...\033[0m"
    ollama serve &
    sleep 3
fi

# 启动翻译工具
python translate.py "$@"
SCRIPT_EOF

chmod +x "$PREFIX/bin/mobiletran"

# 创建桌面快捷方式脚本(可选)
cat > "$OPENNER_DIR/termux-url-opener" << 'OPENNER_EOF'
#!/data/data/com.termux/files/usr/bin/bash
# 此文件允许从 Termux 文件管理器直接打开文本文件进行翻译
# 在文件管理器中点击 .txt 文件时，会询问是否用 MobileTran 翻译

if [[ "$1" == *.txt ]] || [[ "$1" == *.md ]]; then
    echo -e "\033[36m📄 检测到文本文件: $1\033[0m"
    echo -e "\033[36m是否使用 MobileTran 翻译? [Y/n]: \033[0m"
    read -r choice
    if [[ "$choice" != "n" ]] && [[ "$choice" != "N" ]]; then
        mobiletran -f "$1"
        exit $?
    fi
fi
OPENNER_EOF

chmod +x "$OPENNER_DIR/termux-url-opener"

echo -e "\n${GREEN}══════════════════════════════════════════════════"
echo -e "  ✅ MobileTran 安装完成!"
echo -e "══════════════════════════════════════════════════${NC}"

echo -e "\n${CYAN}📖 使用方法:${NC}"
echo -e "  ${GREEN}1. 交互模式:${NC}"
echo -e "     ${YELLOW}mobiletran${NC}"
echo -e ""
echo -e "  ${GREEN}2. 快速翻译文本:${NC}"
echo -e "     ${YELLOW}mobiletran -t \"Hello World\" -l Chinese${NC}"
echo -e ""
echo -e "  ${GREEN}3. 翻译文件:${NC}"
echo -e "     ${YELLOW}mobiletran -f document.txt -l English${NC}"
echo -e ""
echo -e "  ${GREEN}4. 指定源语言:${NC}"
echo -e "     ${YELLOW}mobiletran -t \"你好\" -l English -s Chinese${NC}"
echo -e ""
echo -e "  ${GREEN}5. 保存到文件:${NC}"
echo -e "     ${YELLOW}mobiletran -t \"Hello\" -l Chinese -o result.txt${NC}"

echo -e "\n${CYAN}📋 使用前提:${NC}"
echo -e "  ${YELLOW}1.${NC} 确保 Ollama 已启动: ${GREEN}ollama serve${NC}"
echo -e "  ${YELLOW}2.${NC} 确保模型已下载: ${GREEN}ollama pull Hy-MT1.5-1.8B-1.25bit${NC}"
echo -e "  ${YELLOW}3.${NC} 运行翻译工具: ${GREEN}mobiletran${NC}"

echo -e "\n${GREEN}🎉 安装成功! 请执行 'mobiletran' 启动翻译工具${NC}\n"
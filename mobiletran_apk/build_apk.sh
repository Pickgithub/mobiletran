#!/bin/bash
# ============================================
# MobileTran APK 构建脚本
# 在 Linux/macOS 主机上构建 Android APK
# ============================================

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║     📱 MobileTran APK 构建工具                    ║"
echo "╚══════════════════════════════════════════════════╝"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 检查是否在正确的目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "\n${CYAN}[1/5] 检查依赖...${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3${NC}"
    echo "请安装 Python 3.8+: https://www.python.org/downloads/"
    exit 1
fi
echo -e "${GREEN}✅ Python3 $(python3 --version | cut -d' ' -f2)${NC}"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 pip3${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 已安装${NC}"

# 检查 Java (需要 JDK 17+)
if ! command -v java &> /dev/null; then
    echo -e "${YELLOW}⚠ 未找到 Java，正在安装...${NC}"
    sudo apt-get install -y openjdk-17-jdk || {
        echo -e "${RED}❌ 请手动安装 JDK 17+:${NC}"
        echo "  sudo apt-get install openjdk-17-jdk"
        exit 1
    }
fi
echo -e "${GREEN}✅ Java $(java -version 2>&1 | head -1 | cut -d'"' -f2)${NC}"

# 检查必要的系统包
echo -e "\n${CYAN}[2/5] 安装系统依赖...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y \
        python3-pip \
        python3-dev \
        python3-venv \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg8-dev \
        zlib1g-dev \
        wget \
        curl \
        git \
        unzip \
        zip \
        autoconf \
        automake \
        libtool \
        pkg-config \
        || echo -e "${YELLOW}⚠ 部分包安装失败，尝试继续...${NC}"
elif command -v brew &> /dev/null; then
    brew install python libffi libxml2 libxslt libjpeg zlib wget curl git
fi

# 安装/更新 buildozer
echo -e "\n${CYAN}[3/5] 安装 Buildozer...${NC}"
pip3 install --upgrade pip wheel setuptools
pip3 install --upgrade buildozer cython

# 验证 buildozer
if ! command -v buildozer &> /dev/null; then
    echo -e "${RED}❌ Buildozer 安装失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Buildozer $(buildozer --version 2>/dev/null || echo '已安装')${NC}"

# 生成应用图标（如果没有）
echo -e "\n${CYAN}[4/5] 生成应用图标...${NC}"
if [ ! -f "icon.png" ]; then
    echo -e "${YELLOW}正在生成默认图标...${NC}"
    python3 -c "
import struct, zlib

def create_png(width, height, r, g, b):
    def create_chunk(chunk_type, data):
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return struct.pack('>I', len(data)) + chunk + crc
    
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = create_chunk(b'IHDR', ihdr_data)
    
    # IDAT chunk - image data
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter byte
        for x in range(width):
            # Check if pixel is in the center area for pattern
            cx, cy = width // 2, height // 2
            dx, dy = abs(x - cx), abs(y - cy)
            dist = (dx*dx + dy*dy) ** 0.5
            
            # Simple gradient logo-like pattern
            if dist < min(width, height) * 0.35:
                # Inner circle - white 'T' shape
                if abs(x - cx) < width * 0.12 or (abs(y - cy) < height * 0.12 and x < cx + width * 0.25):
                    raw_data += bytes([255, 255, 255])  # White
                else:
                    raw_data += bytes([r, g, b])  # Primary
            elif dist < min(width, height) * 0.4:
                raw_data += bytes([min(255, int(r*1.2)), min(255, int(g*1.2)), min(255, int(b*1.2))])
            else:
                raw_data += bytes([r, g, b])
    
    compressed = zlib.compress(raw_data)
    idat = create_chunk(b'IDAT', compressed)
    
    # IEND chunk
    iend = create_chunk(b'IEND', b'')
    
    return signature + ihdr + idat + iend

# 创建 128x128 图标
png_data = create_png(128, 128, 26, 115, 232)  # #1a73e8
with open('icon.png', 'wb') as f:
    f.write(png_data)
print('✅ 图标已生成: icon.png (128x128)')

# 创建高分辨率版本用于不同DPI
png_data = create_png(256, 256, 26, 115, 232)
with open('icon_256.png', 'wb') as f:
    f.write(png_data)
print('✅ 图标已生成: icon_256.png (256x256)')
" || echo -e "${YELLOW}⚠ 图标生成失败，将使用 Buildozer 默认图标${NC}"
else
    echo -e "${GREEN}✅ 图标已存在${NC}"
fi

# 构建 APK
echo -e "\n${CYAN}[5/5] 开始构建 APK...${NC}"
echo -e "\n${YELLOW}📌 构建说明:${NC}"
echo -e "  - 首次构建需要下载 Android SDK/NDK (约 1-2GB)"
echo -e "  - 构建时间可能需要 10-30 分钟（取决于网络和机器性能）"
echo -e "  - 请确保有足够的磁盘空间 (至少 10GB)\n"

# 清理旧的构建文件
echo -e "${CYAN}清理旧的构建缓存...${NC}"
rm -rf .buildozer bin 2>/dev/null || true

# 创建 bin 目录
mkdir -p bin

# 构建 debug APK
echo -e "${CYAN}构建 Debug APK...${NC}"
buildozer android debug 2>&1 | tee build.log

# 检查构建结果
if [ -f "bin/mobiletran-*-debug.apk" ]; then
    APK_FILE=$(ls bin/mobiletran-*-debug.apk 2>/dev/null | head -1)
    APK_SIZE=$(ls -lh "$APK_FILE" 2>/dev/null | awk '{print $5}')
    echo -e "\n${GREEN}══════════════════════════════════════════════════"
    echo -e "  ✅ APK 构建成功!"
    echo -e "══════════════════════════════════════════════════${NC}"
    echo -e ""
    echo -e "${CYAN}📍 APK 位置:${NC} ${APK_FILE}"
    echo -e "${CYAN}📦 文件大小:${NC} ${APK_SIZE}"
    echo -e ""
    echo -e "${YELLOW}📱 安装到设备:${NC}"
    echo -e "   adb install ${APK_FILE}"
    echo -e ""
    echo -e "${YELLOW}📋 发布签名:${NC}"
    echo -e "   要发布到应用市场，需要创建签名 APK:"
    echo -e "   buildozer android release"
else
    echo -e "\n${RED}❌ APK 构建失败${NC}"
    echo -e "${YELLOW}查看 build.log 获取详细错误信息${NC}"
    echo -e "${YELLOW}常见问题:${NC}"
    echo -e "  1. 网络问题: 重试 buildozer android debug"
    echo -e "  2. SDK 路径问题: 检查 buildozer.spec 中的 android.sdk_path"
    echo -e "  3. JDK 版本: 确保使用 JDK 17+"
    echo -e "  4. 内存不足: 增加 swap 或减少 android.num_threads"
    exit 1
fi
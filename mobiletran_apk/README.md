# 📱 MobileTran APK - Android 本地翻译应用

将 Termux 中的 **Ollama + Hy-MT1.5** 翻译模型打包为原生 Android APK 应用，提供优雅的图形界面。

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🎯 **文本翻译** | 输入文本即可翻译，实时显示字符数 |
| 📂 **文件导入** | 支持 TXT/MD/HTML/JSON/CSV/SRT/XML |
| 🌐 **16种语言** | 中/英/日/韩/法/德/西/俄/葡/阿/泰/越/意/荷/波/土 |
| 🔄 **智能分段** | 大文本自动分段，确保翻译质量 |
| ⚡ **并行翻译** | 多段并行翻译，大幅提高大文件翻译速度 |
| 💾 **保存结果** | 翻译结果一键保存到 Download 目录 |
| 📊 **实时统计** | 字符数、变化率、进度条实时显示 |
| 🔌 **自动检测** | 启动时自动检测 Ollama 和模型状态 |
| 🔒 **完全离线** | 数据不离开设备，保护隐私 |

## 📋 前置要求

| 要求 | 说明 |
|------|------|
| Android 手机 | Android 8.0 (API 26) 及以上 |
| Termux | 已安装并配置好 Ollama |
| Ollama | 正在运行 (`ollama serve`) |
| 翻译模型 | 已下载 `Hy-MT1.5-1.8B-1.25bit` |

## 🚀 两种使用方式

### 方式一：直接安装 APK（推荐）

1. **下载 APK** 从 [Releases](https://github.com/yourusername/mobiletran/releases) 页面下载 `MobileTran-v1.0.0.apk`
2. **安装 APK** 在手机上打开安装
3. **启动 Ollama** 在 Termux 中运行：`ollama serve &`
4. **打开应用** 点击 MobileTran 图标开始翻译

### 方式二：自己构建 APK

> 在 **Linux 或 macOS** 主机上构建（不支持 Windows，建议使用 WSL2）

#### 前置条件

```bash
# 1. 安装系统依赖
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev \
    python3-venv libffi-dev libssl-dev libxml2-dev \
    libxslt1-dev libjpeg8-dev zlib1g-dev wget curl git \
    unzip zip autoconf automake libtool pkg-config \
    openjdk-17-jdk

# macOS (使用 Homebrew)
brew install python libffi libxml2 libxslt libjpeg zlib wget curl git openjdk@17

# 2. 安装 Buildozer
pip3 install --upgrade pip wheel setuptools
pip3 install --upgrade buildozer cython

# 3. 构建 APK
cd mobiletran_apk
bash build_apk.sh
```

#### Docker 构建（推荐）

```bash
# 使用 Docker 隔离构建环境
docker run -it --rm \
    -v $(pwd):/app \
    -w /app \
    ubuntu:22.04 bash

# 在容器内
apt-get update && apt-get install -y python3 python3-pip git openjdk-17-jdk
pip3 install buildozer
cd /app
buildozer android debug
```

#### 快速构建命令

```bash
# 进入项目目录
cd mobiletran_apk

# 一键构建
bash build_apk.sh

# 或手动分步
buildozer init          # 初始化（已有 buildozer.spec 可跳过）
buildozer android debug # 构建 debug APK
buildozer android release # 构建 release APK（需要签名）
```

## 📱 应用界面

### 主界面布局

```
┌─────────────────────────────┐
│  📱 MobileTran    ● 已连接  │ ← 顶部栏：应用名 + Ollama 状态
├─────────────────────────────┤
│  📝 输入文本         0 字符  │
│  ┌───────────────────────┐ │
│  │                       │ │ ← 多行文本输入框
│  │                       │ │
│  └───────────────────────┘ │
│                             │
│  🌐 源语言: 自动检测        │
│  目标语言: [中文 ▼]        │ ← 16种语言可选
│                             │
│  ┌───────┬─────────┐       │
│  │ 🚀 翻译 │ 📂 导入  │       │ ← 操作按钮
│  ├───────┼─────────┤       │
│  │ 🗑️清空 │ 💾 保存  │       │
│  └───────┴─────────┘       │
│                             │
│  📄 翻译结果      ✓ 45字符  │
│  ┌───────────────────────┐ │
│  │ 翻译结果在这里显示...   │ │ ← 只读结果框
│  └───────────────────────┘ │
│  ████████████████░░░░ 80%  │ ← 进度条（翻译时显示）
└─────────────────────────────┘
```

### 操作流程

1. **输入文本** → 直接输入或导入文件
2. **选择语言** → 从下拉菜单选择目标语言
3. **点击翻译** → 等待翻译完成
4. **查看结果** → 阅读翻译结果
5. **保存文件** → 点击保存，输入文件名

## ⚙️ 配置说明

### 修改 Ollama 地址

编辑 `main.py` 顶部配置：

```python
OLLAMA_HOST = "http://localhost:11434"  # Ollama API 地址
MODEL_NAME = "Hy-MT1.5-1.8B-1.25bit"    # 翻译模型名称
REQUEST_TIMEOUT = 120                    # 请求超时(秒)
```

如果 Ollama 运行在非标准端口或远程服务器，修改 `OLLAMA_HOST` 即可。

### 修改 Buildozer 配置

编辑 `buildozer.spec`：

```ini
# 应用信息
title = MobileTran
package.name = mobiletran
package.domain = com.mobiletran
version = 1.0.0

# Android 兼容性
android.api = 34        # 目标 API
android.minapi = 26     # 最低 API (Android 8.0)
android.targetapi = 34  # 目标 API

# 权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
```

## 🔧 常见问题

### 1. Ollama 连接失败

```
应用顶部显示: ○ Ollama 未启动
```

**解决：**
```bash
# 在 Termux 中启动 Ollama
ollama serve &

# 验证是否正常运行
curl http://localhost:11434/api/tags
```

### 2. 模型未找到

```
弹出提示: 未找到模型 Hy-MT1.5-1.8B-1.25bit
```

**解决：**
```bash
# 在 Termux 中下载模型
ollama pull Hy-MT1.5-1.8B-1.25bit

# 查看已安装模型
ollama list
```

### 3. APK 编译失败

**常见原因与解决：**

| 问题 | 解决 |
|------|------|
| JDK 版本不对 | 安装 JDK 17: `sudo apt-get install openjdk-17-jdk` |
| 网络超时 | 设置代理或重试: `buildozer android debug` |
| 内存不足 | `export GRADLE_OPTS="-Xmx2g"` 或减少线程数 |
| SDK 下载失败 | 手动下载 Android SDK 并配置路径 |

### 4. 应用闪退

```bash
# 通过 adb 查看日志
adb logcat | grep python

# 或查看 Termux 中 Ollama 是否在运行
```

## 📦 打包发布

### 生成 Release APK

```bash
# 1. 生成签名密钥
keytool -genkey -v -keystore mobiletran.keystore \
    -alias mobiletran -keyalg RSA -keysize 2048 \
    -validity 10000

# 2. 修改 buildozer.spec 添加签名信息
# android.release_artifact = True
# android.keystore = mobiletran.keystore

# 3. 构建 Release APK
buildozer android release

# 4. (可选) 优化 APK
zipalign -v -p 4 bin/MobileTran-release-unsigned.apk bin/MobileTran-aligned.apk
apksigner sign --ks mobiletran.keystore bin/MobileTran-aligned.apk
```

## 📁 项目结构

```
mobiletran_apk/
├── main.py              # Kivy Android 主程序 (原生界面)
├── buildozer.spec       # Buildozer 构建配置
├── build_apk.sh         # APK 构建脚本
├── icon.png             # 应用图标 (128x128)
├── icon_256.png         # 应用图标高清版 (256x256)
└── README.md            # 本文件
```

## 🔄 架构说明

```
┌─────────────────────────────────────────────┐
│                Android 手机                   │
│                                              │
│  ┌──────────────────────┐  ┌────────────────┐│
│  │  MobileTran APK      │  │  Termux        ││
│  │                      │  │                ││
│  │  Kivy GUI ──HTTP──► │  │  Ollama ──►    ││
│  │  (Python)  ◄──JSON──│  │  Model(Hy-MT1.5)││
│  │                      │  │                ││
│  └──────────────────────┘  └────────────────┘│
│         ↑ HTTP API (localhost:11434)         │
└─────────────────────────────────────────────┘
```

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-04 | 初始版本：基础翻译、文件导入、16种语言 |

## 📄 许可证

MIT License

## 🤝 贡献

欢迎 Issue 和 Pull Request！

---

**Made with ❤️ for Android - 利用 Termux + Ollama 实现本地 AI 翻译**
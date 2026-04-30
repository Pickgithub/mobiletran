# 📱 MobileTran - Termux + Ollama 智能翻译工具

在 Android 手机的 Termux 环境中，利用本地运行的 **Ollama** 和 **Hy-MT1.5** 翻译模型，实现**离线、快速、私密**的文本翻译。

## ✨ 功能特点

- ✅ **直接输入文本翻译** - 支持多行文本输入
- ✅ **导入文件翻译** - 支持 .txt / .md / .html / .json / .csv 等多种格式
- ✅ **16 种目标语言** - 中文、英语、日语、韩语、法语、德语、西班牙语等
- ✅ **自动检测源语言** - 无需手动指定源语言
- ✅ **智能分段** - 大文本自动分段翻译，确保质量
- ✅ **彩色终端界面** - 清晰美观的操作界面
- ✅ **保存翻译结果** - 支持保存为文本文件
- ✅ **命令行快速模式** - 支持命令行参数直接翻译
- ✅ **完全离线运行** - 数据不离开你的手机，保护隐私

## 🛠 技术栈

- **运行环境**: Android + Termux
- **翻译引擎**: Ollama + Hy-MT1.5-1.8B-1.25bit
- **编程语言**: Python 3
- **UI 框架**: Rich (彩色终端界面)
- **网络请求**: Requests (Ollama API)

## 📋 前提条件

1. **Android 手机** 已安装 [Termux](https://termux.com/) (推荐 F-Droid 版本)
2. **Termux** 内已安装 [Ollama](https://ollama.com/)
3. **Ollama** 内已安装 **Hy-MT1.5-1.8B-1.25bit** 模型

## 🚀 快速安装

### 方法一：一键安装脚本（推荐）

在 Termux 中执行：

```bash
# 克隆或下载本项目到 Termux 中
git clone https://github.com/yourusername/mobiletran.git
cd mobiletran/mobiletran_app

# 运行安装脚本
bash setup.sh

# 启动翻译工具
mobiletran
```

### 方法二：手动安装

```bash
# 1. 更新 Termux 并安装 Python
pkg update -y && pkg upgrade -y
pkg install -y python python-pip

# 2. 安装 Python 依赖
pip install requests rich

# 3. 确保 Ollama 在运行
ollama serve &

# 4. 确保已下载翻译模型
ollama pull Hy-MT1.5-1.8B-1.25bit

# 5. 运行翻译工具
cd mobiletran_app
python translate.py
```

## 📖 使用指南

### 🖥 交互模式（默认）

直接运行程序进入交互模式：

```bash
mobiletran
# 或
python translate.py
```

交互界面提供以下功能：

```
📋 主菜单:
  1. ✏️  输入文本翻译
  2. 📄  导入文件翻译
  3. 🔄  切换目标语言
  4. ℹ️  关于程序
  5. 🚪  退出程序
```

#### 文本翻译模式
1. 选择 `1` 进入文本输入模式
2. 输入待翻译文本（多行，空行结束）
3. 确认翻译
4. 查看翻译结果
5. 选择是否保存文件

**文本输入快捷键：**
- `/save` - 保存当前输入内容
- `/clear` - 清空输入
- `/exit` - 返回主菜单

#### 文件翻译模式
1. 选择 `2` 进入文件翻译模式
2. 输入文件路径（支持 Tab 补全）
3. 确认翻译
4. 查看翻译结果
5. 选择是否保存文件

### ⚡ 命令行快速模式

```bash
# 翻译文本到中文
mobiletran -t "Hello, how are you?" -l Chinese

# 翻译文本到日语，指定源语言
mobiletran -t "你好，今天天气不错" -l Japanese -s Chinese

# 翻译文件到英语
mobiletran -f /sdcard/Documents/article.txt -l English

# 翻译文件并直接保存结果
mobiletran -f input.txt -l Chinese -o output.txt

# 查看帮助
mobiletran --help
```

### 🌐 支持的语言

| 编号 | 语言 |
|------|------|
| 1 | 中文 (Chinese) |
| 2 | 英语 (English) |
| 3 | 日语 (Japanese) |
| 4 | 韩语 (Korean) |
| 5 | 法语 (French) |
| 6 | 德语 (German) |
| 7 | 西班牙语 (Spanish) |
| 8 | 俄语 (Russian) |
| 9 | 葡萄牙语 (Portuguese) |
| 10 | 阿拉伯语 (Arabic) |
| 11 | 泰语 (Thai) |
| 12 | 越南语 (Vietnamese) |
| 13 | 意大利语 (Italian) |
| 14 | 荷兰语 (Dutch) |
| 15 | 波兰语 (Polish) |
| 16 | 土耳其语 (Turkish) |

## ⚙️ 配置说明

你可以在 `translate.py` 顶部修改以下配置：

```python
OLLAMA_HOST = "http://localhost:11434"   # Ollama 服务地址
MODEL_NAME = "Hy-MT1.5-1.8B-1.25bit"    # 翻译模型名称
DEFAULT_TIMEOUT = 120                    # 翻译超时时间(秒)
```

## 📁 文件结构

```
mobiletran_app/
├── translate.py        # 主程序
├── requirements.txt    # Python 依赖
├── setup.sh           # Termux 安装脚本
└── README.md          # 本文件
```

## 🔧 常见问题

### ❓ Ollama 连接失败

```bash
# 确保 Ollama 正在运行
ollama serve &

# 检查 Ollama 状态
curl http://localhost:11434/api/tags
```

### ❓ 模型未找到

```bash
# 列出已安装的模型
ollama list

# 下载翻译模型
ollama pull Hy-MT1.5-1.8B-1.25bit
```

### ❓ 翻译结果不理想

- 尝试明确指定源语言（而非自动检测）
- 对于较长的文本，程序会自动分段翻译
- 调整提示词（prompt）格式可能改善结果

### ❓ 权限问题

```bash
# 确保脚本有执行权限
chmod +x mobiletran_app/setup.sh
chmod +x mobiletran_app/translate.py
```

## 📝 注意事项

- **首次运行**需要先启动 Ollama 服务：`ollama serve &`
- 翻译模型约 **1GB**，下载需要连接网络并有足够的存储空间
- 大文件（>8000 字符）会自动分段翻译，需要更多时间
- 所有翻译在本地进行，**不依赖互联网**（除模型下载外）

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ for Android + Termux**
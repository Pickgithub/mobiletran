#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MobileTran - Termux Ollama 翻译工具
利用 Termux 内 Ollama 运行的 Hy-MT1.5 模型进行文本翻译
"""

import sys
import os
import json
import time
from typing import Optional, List, Tuple

try:
    import requests
except ImportError:
    print("缺少依赖: requests")
    print("请运行: pip install requests")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich import box
    from rich.markdown import Markdown
except ImportError:
    print("缺少依赖: rich")
    print("请运行: pip install rich")
    sys.exit(1)


# ============ 配置区 ============
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "Hy-MT1.5-1.8B-1.25bit"
DEFAULT_TIMEOUT = 120  # 翻译超时时间(秒)

# 支持的目标语言
SUPPORTED_LANGUAGES = {
    "1": {"name": "中文", "code": "Chinese", "english_name": "Chinese"},
    "2": {"name": "英语", "code": "English", "english_name": "English"},
    "3": {"name": "日语", "code": "Japanese", "english_name": "Japanese"},
    "4": {"name": "韩语", "code": "Korean", "english_name": "Korean"},
    "5": {"name": "法语", "code": "French", "english_name": "French"},
    "6": {"name": "德语", "code": "German", "english_name": "German"},
    "7": {"name": "西班牙语", "code": "Spanish", "english_name": "Spanish"},
    "8": {"name": "俄语", "code": "Russian", "english_name": "Russian"},
    "9": {"name": "葡萄牙语", "code": "Portuguese", "english_name": "Portuguese"},
    "10": {"name": "阿拉伯语", "code": "Arabic", "english_name": "Arabic"},
    "11": {"name": "泰语", "code": "Thai", "english_name": "Thai"},
    "12": {"name": "越南语", "code": "Vietnamese", "english_name": "Vietnamese"},
    "13": {"name": "意大利语", "code": "Italian", "english_name": "Italian"},
    "14": {"name": "荷兰语", "code": "Dutch", "english_name": "Dutch"},
    "15": {"name": "波兰语", "code": "Polish", "english_name": "Polish"},
    "16": {"name": "土耳其语", "code": "Turkish", "english_name": "Turkish"},
}

console = Console()


# ============ 工具函数 ============

def check_ollama_status() -> bool:
    """检查 Ollama 服务是否在运行"""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            if MODEL_NAME in model_names:
                return True
            else:
                console.print(f"[yellow]⚠ 未找到模型 '{MODEL_NAME}'[/yellow]")
                console.print(f"[dim]已安装的模型: {', '.join(model_names) if model_names else '无'}[/dim]")
                return False
        return False
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False


def list_available_models() -> List[str]:
    """列出 Ollama 中可用的模型"""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        return []
    except Exception:
        return []


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> Optional[str]:
    """
    调用 Ollama API 进行翻译
    """
    # 构建翻译提示词
    if source_lang == "auto":
        prompt = f"""请将以下文本翻译成{target_lang}。
只返回翻译结果，不要包含任何解释、备注或额外内容。

待翻译文本：
{text}

翻译结果："""
    else:
        prompt = f"""请将以下{source_lang}文本翻译成{target_lang}。
只返回翻译结果，不要包含任何解释、备注或额外内容。

待翻译文本：
{text}

翻译结果："""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # 低温度以获得更准确的翻译
            "num_predict": 4096,  # 最大输出token数
        }
    }

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="[cyan]正在翻译中，请稍候...", total=None)
            
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json=payload,
                timeout=DEFAULT_TIMEOUT
            )
        
        if response.status_code == 200:
            result = response.json()
            translated = result.get("response", "").strip()
            
            # 清理可能的引号和多余内容
            translated = translated.strip('"').strip("'").strip()
            
            # 如果翻译结果为空，尝试另一种提示方式
            if not translated:
                return _fallback_translate(text, target_lang, source_lang)
            
            return translated
        else:
            console.print(f"[red]❌ API 返回错误: {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            return None
            
    except requests.exceptions.Timeout:
        console.print(f"[red]⏱ 翻译超时(>{DEFAULT_TIMEOUT}秒)，文本可能过长[/red]")
        return None
    except requests.exceptions.ConnectionError:
        console.print("[red]🔌 无法连接到 Ollama 服务[/red]")
        console.print("[yellow]请确保 Ollama 已在 Termux 中启动: ollama serve[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]❌ 翻译出错: {str(e)}[/red]")
        return None


def _fallback_translate(text: str, target_lang: str, source_lang: str) -> Optional[str]:
    """备用翻译方法 - 使用不同的提示词格式"""
    prompt = f"Translate to {target_lang}: {text}"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 4096,
        }
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=DEFAULT_TIMEOUT
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return None
    except Exception:
        return None


def translate_file(file_path: str, target_lang: str, source_lang: str = "auto") -> Optional[str]:
    """翻译文件内容"""
    try:
        # 检查文件编码
        encodings = ["utf-8", "gbk", "gb2312", "big5", "shift-jis", "euc-kr"]
        
        content = None
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            # 尝试二进制读取
            with open(file_path, "rb") as f:
                raw = f.read()
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                content = raw.decode("utf-8", errors="replace")
        
        if not content.strip():
            console.print("[yellow]⚠ 文件内容为空[/yellow]")
            return None
        
        # 显示文件信息
        file_size = len(content)
        line_count = content.count("\n") + 1
        console.print(f"[dim]文件信息: {os.path.basename(file_path)} | "
                      f"{file_size} 字节 | {line_count} 行[/dim]")
        
        # 文件太大时分段翻译
        if file_size > 8000:
            console.print("[yellow]📄 文件较大，将分段翻译...[/yellow]")
            return translate_large_text(content, target_lang, source_lang)
        
        return translate_text(content, target_lang, source_lang)
        
    except FileNotFoundError:
        console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
        return None
    except PermissionError:
        console.print(f"[red]❌ 无权限读取文件: {file_path}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]❌ 读取文件出错: {str(e)}[/red]")
        return None


def translate_large_text(text: str, target_lang: str, source_lang: str = "auto",
                        chunk_size: int = 2000) -> Optional[str]:
    """分段翻译大文本"""
    # 按段落分组，尽量在自然断点处分段
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n" + para
            else:
                current_chunk = para
    
    if current_chunk:
        chunks.append(current_chunk)
    
    console.print(f"[dim]共 {len(chunks)} 段，开始逐段翻译...[/dim]")
    
    translated_parts = []
    for i, chunk in enumerate(chunks, 1):
        console.print(f"[cyan]  翻译第 {i}/{len(chunks)} 段...[/cyan]")
        result = translate_text(chunk, target_lang, source_lang)
        if result:
            translated_parts.append(result)
        else:
            console.print(f"[red]  第 {i} 段翻译失败[/red]")
            translated_parts.append(f"[翻译失败: 第{i}段]")
        time.sleep(0.5)  # 避免请求过快
    
    return "\n".join(translated_parts)


def save_to_file(content: str, default_name: str = "translation") -> bool:
    """保存翻译结果到文件"""
    while True:
        file_name = Prompt.ask(
            "[cyan]📁 请输入保存的文件名[/cyan]",
            default=default_name
        )
        
        # 确保有扩展名
        if "." not in file_name:
            file_name += ".txt"
        
        # 检查文件是否已存在
        if os.path.exists(file_name):
            overwrite = Confirm.ask(
                f"[yellow]⚠ 文件 '{file_name}' 已存在，是否覆盖?[/yellow]",
                default=False
            )
            if not overwrite:
                continue
        
        try:
            # 自动检测编码问题，写入UTF-8 BOM以便中文正确显示
            with open(file_name, "w", encoding="utf-8-sig") as f:
                f.write(content)
            
            file_path = os.path.abspath(file_name)
            file_size = len(content.encode("utf-8"))
            
            console.print(f"[green]✅ 翻译结果已保存[/green]")
            console.print(f"  [bold]文件路径:[/bold] {file_path}")
            console.print(f"  [bold]文件大小:[/bold] {file_size:,} 字节")
            console.print(f"  [bold]字符数:[/bold] {len(content):,}")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ 保存失败: {str(e)}[/red]")
            retry = Confirm.ask("[yellow]是否重试?[/yellow]", default=True)
            if not retry:
                return False


# ============ UI 界面 ============

def show_banner():
    """显示启动横幅"""
    banner = """
[bold cyan]
╔══════════════════════════════════════════════════╗
║                 📱 MobileTran                    ║
║          Termux + Ollama 智能翻译工具             ║
╚══════════════════════════════════════════════════╝
[/bold cyan]"""
    console.print(banner)


def show_status_bar():
    """显示 Ollama 状态"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[cyan]正在检查 Ollama 服务...", total=None)
        is_connected = check_ollama_status()
    
    if is_connected:
        console.print(Panel(
            f"[green]✅ Ollama 已连接 | 模型: {MODEL_NAME}[/green]",
            style="green",
            box=box.ROUNDED
        ))
    else:
        console.print(Panel(
            "[red]❌ Ollama 未连接[/red]\n"
            "[yellow]请确保:[/yellow]\n"
            "  1. Termux 已启动\n"
            "  2. Ollama 已运行: [bold]ollama serve[/bold]\n"
            f"  3. 模型 {MODEL_NAME} 已安装: [bold]ollama pull {MODEL_NAME}[/bold]",
            style="red",
            box=box.ROUNDED
        ))
        
        # 列出可用模型
        models = list_available_models()
        if models:
            console.print("\n[dim]可用模型:[/dim]")
            for m in models:
                console.print(f"  [dim]• {m}[/dim]")
        
        return False
    
    return True


def show_language_menu() -> Tuple[str, str]:
    """显示语言选择菜单"""
    console.print("\n[bold]🌐 选择目标语言:[/bold]")
    
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("编号", style="cyan", justify="right", width=4)
    table.add_column("语言", style="white")
    
    # 按行排列显示
    items = list(SUPPORTED_LANGUAGES.items())
    for i in range(0, len(items), 2):
        left = items[i]
        if i + 1 < len(items):
            right = items[i + 1]
            table.add_row(
                f"{left[0]}.",
                f"{left[1]['name']} ({left[1]['english_name']})",
            )
            table.add_row(
                f"{right[0]}.",
                f"{right[1]['name']} ({right[1]['english_name']})",
            )
        else:
            table.add_row(
                f"{left[0]}.",
                f"{left[1]['name']} ({left[1]['english_name']})",
            )
    
    console.print(table)
    
    while True:
        choice = Prompt.ask(
            "[cyan]请输入编号[/cyan]",
            default="1"
        )
        
        if choice in SUPPORTED_LANGUAGES:
            lang_info = SUPPORTED_LANGUAGES[choice]
            console.print(f"[green]✅ 目标语言: {lang_info['name']} ({lang_info['english_name']})[/green]")
            return lang_info["english_name"], lang_info["name"]
        
        console.print("[red]❌ 无效编号，请重新选择[/red]")


def show_source_language_menu() -> str:
    """选择源语言（可选）"""
    console.print("\n[bold]🔤 选择源语言 (可选):[/bold]")
    console.print("[dim]如果选择「自动检测」，程序将让模型自动识别源语言[/dim]")
    
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("编号", style="cyan", justify="right", width=4)
    table.add_column("语言", style="white")
    
    # 添加"自动检测"选项
    table.add_row("0.", "🤖 自动检测")
    
    for key, lang in SUPPORTED_LANGUAGES.items():
        table.add_row(f"{key}.", f"{lang['name']} ({lang['english_name']})")
    
    console.print(table)
    
    while True:
        choice = Prompt.ask(
            "[cyan]请输入编号[/cyan]",
            default="0"
        )
        
        if choice == "0":
            console.print("[green]✅ 源语言: 自动检测[/green]")
            return "auto"
        elif choice in SUPPORTED_LANGUAGES:
            lang_info = SUPPORTED_LANGUAGES[choice]
            console.print(f"[green]✅ 源语言: {lang_info['name']} ({lang_info['english_name']})[/green]")
            return lang_info["english_name"]
        
        console.print("[red]❌ 无效编号，请重新选择[/red]")


def show_main_menu() -> str:
    """显示主菜单"""
    console.print("\n[bold]📋 主菜单:[/bold]")
    
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("选项", style="cyan", justify="right", width=6)
    table.add_column("功能", style="white")
    table.add_row("1.", "✏️   输入文本翻译")
    table.add_row("2.", "📄   导入文件翻译")
    table.add_row("3.", "🔄   切换目标语言")
    table.add_row("4.", "ℹ️   关于程序")
    table.add_row("5.", "🚪   退出程序")
    
    console.print(table)
    
    while True:
        choice = Prompt.ask(
            "[cyan]请选择操作[/cyan]",
            default="1"
        )
        
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        
        console.print("[red]❌ 无效选项，请重新选择[/red]")


def text_input_mode(target_lang_english: str, target_lang_native: str,
                    source_lang: str) -> None:
    """文本输入模式"""
    console.print("\n[bold]✏️  文本翻译模式[/bold]")
    console.print(f"[dim]目标语言: {target_lang_native} | 源语言: "
                  f"{'自动检测' if source_lang == 'auto' else source_lang}[/dim]")
    console.print("[dim]输入 /save 保存当前输入 | /clear 清空 | /exit 返回主菜单[/dim]")
    
    # 多行输入
    lines = []
    console.print("\n[cyan]请输入待翻译文本 (输入空行结束):[/cyan]")
    
    while True:
        try:
            line = input()
            if line == "/exit":
                return
            elif line == "/save":
                if lines:
                    text = "\n".join(lines)
                    save_to_file(text, "input_text")
                else:
                    console.print("[yellow]⚠ 还没有输入内容[/yellow]")
                continue
            elif line == "/clear":
                lines = []
                console.print("[green]✅ 已清空输入[/green]")
                continue
            elif line == "" and lines:
                # 空行结束输入
                break
            elif line == "":
                continue
            
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break
    
    if not lines:
        console.print("[yellow]⚠ 没有输入文本[/yellow]")
        return
    
    text = "\n".join(lines)
    
    console.print(f"\n[dim]输入内容预览:[/dim]")
    preview = text[:200] + ("..." if len(text) > 200 else "")
    console.print(Panel(preview, style="dim", box=box.ROUNDED))
    
    if not Confirm.ask("[cyan]是否开始翻译?[/cyan]", default=True):
        return
    
    # 执行翻译
    result = translate_text(text, target_lang_english, source_lang)
    
    if result:
        show_translation_result(text, result, target_lang_native)


def file_input_mode(target_lang_english: str, target_lang_native: str,
                    source_lang: str) -> None:
    """文件输入模式"""
    console.print("\n[bold]📄 文件翻译模式[/bold]")
    console.print("[dim]支持: .txt, .md, .html, .json, .csv, .srt 等文本格式[/dim]")
    
    while True:
        file_path = Prompt.ask(
            "[cyan]📂 请输入文件路径[/cyan]"
        )
        
        # 处理带引号的路径
        file_path = file_path.strip('"').strip("'").strip()
        
        if not os.path.exists(file_path):
            console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
            if not Confirm.ask("[yellow]是否重试?[/yellow]", default=True):
                return
            continue
        
        if os.path.isdir(file_path):
            # 如果是目录，列出目录下的文本文件
            console.print(f"[yellow]'{file_path}' 是一个目录[/yellow]")
            text_files = []
            for f in os.listdir(file_path):
                if f.endswith((".txt", ".md", ".html", ".json", ".csv", ".srt",
                              ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf",
                              ".log", ".py", ".js", ".ts", ".java", ".c", ".cpp",
                              ".h", ".hpp", ".rs", ".go", ".rb", ".php", ".sh")):
                    text_files.append(f)
            
            if text_files:
                console.print("\n[cyan]目录中的文本文件:[/cyan]")
                for i, f in enumerate(text_files, 1):
                    console.print(f"  {i}. {f}")
                
                choice = Prompt.ask(
                    "[cyan]选择文件编号，或输入完整路径[/cyan]"
                )
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(text_files):
                        file_path = os.path.join(file_path, text_files[idx])
                    else:
                        console.print("[red]❌ 无效编号[/red]")
                        continue
                except ValueError:
                    continue
            else:
                console.print("[yellow]⚠ 目录中没有找到文本文件[/yellow]")
                if not Confirm.ask("[yellow]是否重新输入路径?[/yellow]", default=True):
                    return
                continue
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:  # 超过1MB
            console.print(f"[red]❌ 文件过大 ({file_size / 1024 / 1024:.1f} MB)[/red]")
            console.print("[yellow]请使用较小的文件(建议 < 1MB)[/yellow]")
            if not Confirm.ask("[yellow]是否尝试继续?[/yellow]", default=False):
                return
        
        break
    
    # 执行翻译
    console.print(f"\n[cyan]开始翻译文件: {os.path.basename(file_path)}[/cyan]")
    result = translate_file(file_path, target_lang_english, source_lang)
    
    if result:
        show_translation_result(
            f"[文件: {os.path.basename(file_path)}]",
            result,
            target_lang_native
        )


def show_translation_result(original: str, translated: str, target_lang: str) -> None:
    """显示翻译结果"""
    console.print("\n" + "═" * 60)
    console.print(f"[bold green]✅ 翻译完成! ({target_lang})[/bold green]")
    console.print("═" * 60)
    
    # 显示结果
    console.print("\n[bold]翻译结果:[/bold]")
    console.print(Panel(
        translated,
        style="green",
        box=box.HEAVY,
        border_style="green"
    ))
    
    # 显示统计信息
    original_chars = len(original) if isinstance(original, str) else len(str(original))
    translated_chars = len(translated)
    
    stats_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    stats_table.add_column("指标", style="dim", width=15)
    stats_table.add_column("数值")
    stats_table.add_row("原文长度", f"{original_chars:,} 字符")
    stats_table.add_row("译文长度", f"{translated_chars:,} 字符")
    stats_table.add_row("变化率", f"{((translated_chars - original_chars) / max(original_chars, 1) * 100):+.1f}%")
    
    console.print("\n[dim]统计信息:[/dim]")
    console.print(stats_table)
    
    # 询问是否保存
    if Confirm.ask("\n[cyan]💾 是否保存翻译结果到文件?[/cyan]", default=True):
        save_to_file(translated, f"translation_{int(time.time())}")
    
    console.print("\n[dim]按 Enter 键继续...[/dim]")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass


def show_about():
    """显示关于信息"""
    about_text = f"""
[bold cyan]📱 MobileTran - 移动端翻译工具[/bold cyan]

[bold]版本:[/bold]     v1.0.0
[bold]模型:[/bold]     {MODEL_NAME}
[bold]接口:[/bold]     Ollama API (localhost:11434)
[bold]技术栈:[/bold]   Python + Rich + Requests

[bold]功能特点:[/bold]
• 支持直接输入文本翻译
• 支持导入文本文件翻译
• 支持 16 种目标语言
• 自动检测源语言
• 智能分段翻译大文本
• 彩色终端界面
• 翻译结果保存到文件

[bold]使用前提:[/bold]
1. Termux 已安装并启动
2. Ollama 已运行 (ollama serve)
3. 翻译模型已安装 (ollama pull {MODEL_NAME})

[dim]Made with ❤️ for Android + Termux[/dim]
"""
    console.print(Panel(about_text, box=box.DOUBLE, border_style="cyan"))
    
    console.print("\n[dim]按 Enter 键返回主菜单...[/dim]")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass


def quick_translate_mode():
    """快速翻译模式 - 直接翻译命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MobileTran - Termux Ollama 翻译工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s -t "Hello World" -l English
  %(prog)s -f document.txt -l Chinese
  %(prog)s -t "你好" -l Japanese -s Chinese
        """
    )
    
    parser.add_argument("-t", "--text", help="要翻译的文本")
    parser.add_argument("-f", "--file", help="要翻译的文件路径")
    parser.add_argument("-l", "--language", help="目标语言 (如: Chinese, English, Japanese)")
    parser.add_argument("-s", "--source", help="源语言 (默认: auto 自动检测)")
    parser.add_argument("-o", "--output", help="输出文件路径 (可选)")
    
    args = parser.parse_args()
    
    if not args.text and not args.file:
        parser.print_help()
        return
    
    if not args.language:
        console.print("[red]❌ 请指定目标语言 (-l/--language)[/red]")
        return
    
    # 验证目标语言
    valid_langs = [lang["english_name"].lower() for lang in SUPPORTED_LANGUAGES.values()]
    if args.language.lower() not in valid_langs:
        console.print(f"[red]❌ 不支持的语言: {args.language}[/red]")
        console.print(f"[yellow]支持的语言: {', '.join(sorted(set(valid_langs)))}[/yellow]")
        return
    
    source_lang = args.source if args.source else "auto"
    
    console.print(Panel(
        f"[bold]快速翻译模式[/bold]\n"
        f"目标语言: {args.language}\n"
        f"源语言: {'自动检测' if source_lang == 'auto' else source_lang}",
        box=box.ROUNDED
    ))
    
    if args.text:
        result = translate_text(args.text, args.language, source_lang)
        if result:
            console.print("\n[bold]✅ 翻译结果:[/bold]")
            console.print(Panel(result, style="green", box=box.HEAVY))
            
            if args.output:
                save_to_file(result, args.output)
            elif Confirm.ask("\n[cyan]是否保存结果?[/cyan]", default=False):
                save_to_file(result)
    
    elif args.file:
        result = translate_file(args.file, args.language, source_lang)
        if result:
            if args.output:
                save_to_file(result, args.output)
            else:
                console.print("\n[bold]✅ 翻译结果:[/bold]")
                console.print(Panel(result, style="green", box=box.HEAVY))
                if Confirm.ask("\n[cyan]是否保存结果?[/cyan]", default=False):
                    save_to_file(result)


# ============ 主程序 ============

def main():
    """主程序入口"""
    # 检查命令行模式
    if len(sys.argv) > 1:
        quick_translate_mode()
        return
    
    try:
        # 显示启动界面
        console.clear()
        show_banner()
        
        # 初始化状态
        target_lang_english = "Chinese"
        target_lang_native = "中文"
        source_lang = "auto"
        
        # 检查服务状态
        ollama_connected = show_status_bar()
        
        if not ollama_connected:
            console.print("\n[yellow]提示: 进入交互模式后，你也可以随时检查连接状态[/yellow]")
            if not Confirm.ask("[cyan]是否继续进入程序?[/cyan]", default=True):
                console.print("[yellow]已退出[/yellow]")
                return
        
        # 首次运行选择目标语言
        console.print("\n[bold]⚙️  初始化设置[/bold]")
        target_lang_english, target_lang_native = show_language_menu()
        source_lang = show_source_language_menu()
        
        # 主循环
        while True:
            console.clear()
            show_banner()
            
            # 显示当前状态
            status_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
            status_table.add_column("项目", style="dim", width=12)
            status_table.add_column("状态")
            status_table.add_row("Ollama", "✅ 已连接" if ollama_connected else "❌ 未连接")
            status_table.add_row("模型", MODEL_NAME)
            status_table.add_row("目标语言", target_lang_native)
            status_table.add_row("源语言", "自动检测" if source_lang == "auto" else source_lang)
            console.print(Panel(status_table, title="[bold]📊 当前状态[/bold]", box=box.ROUNDED))
            
            choice = show_main_menu()
            
            if choice == "1":
                text_input_mode(target_lang_english, target_lang_native, source_lang)
            
            elif choice == "2":
                file_input_mode(target_lang_english, target_lang_native, source_lang)
            
            elif choice == "3":
                console.clear()
                show_banner()
                console.print("\n[bold]🔄 切换语言设置[/bold]")
                target_lang_english, target_lang_native = show_language_menu()
                source_lang = show_source_language_menu()
                console.print("\n[green]✅ 语言设置已更新![/green]")
                time.sleep(1)
            
            elif choice == "4":
                console.clear()
                show_banner()
                show_about()
            
            elif choice == "5":
                console.print("\n[bold cyan]感谢使用 MobileTran! 👋[/bold cyan]")
                console.print("[dim]Made with ❤️ for Android + Termux[/dim]\n")
                break
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]程序被用户中断[/yellow]")
        console.print("[dim]感谢使用 MobileTran! 👋[/dim]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ 程序异常: {str(e)}[/red]")
        console.print("[dim]请报告此错误[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
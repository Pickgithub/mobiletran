"""
MobileTran - Android 端到端翻译应用
使用 Kivy 构建原生 Android APK
通过 Ollama API 调用本地翻译模型 Hy-MT1.5
"""

import json
import os
import threading
import requests
import time
from datetime import datetime

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform, get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation

# ======================== 配置 ========================
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "Hy-MT1.5-1.8B-1.25bit"
REQUEST_TIMEOUT = 120

# 支持的语言
LANGUAGES = [
    ("中文", "Chinese"),
    ("英语", "English"),
    ("日语", "Japanese"),
    ("韩语", "Korean"),
    ("法语", "French"),
    ("德语", "German"),
    ("西班牙语", "Spanish"),
    ("俄语", "Russian"),
    ("葡萄牙语", "Portuguese"),
    ("阿拉伯语", "Arabic"),
    ("泰语", "Thai"),
    ("越南语", "Vietnamese"),
    ("意大利语", "Italian"),
    ("荷兰语", "Dutch"),
    ("波兰语", "Polish"),
    ("土耳其语", "Turkish"),
]

# ======================== 颜色主题 ========================
COLORS = {
    'primary': '#1a73e8',
    'primary_dark': '#1557b0',
    'primary_light': '#e8f0fe',
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'text': '#202124',
    'text_secondary': '#5f6368',
    'accent': '#34a853',
    'warning': '#ea4335',
    'border': '#dadce0',
    'success': '#34a853',
    'error': '#ea4335',
}

# ======================== 自定义组件 ========================

class RoundedButton(Button):
    """圆角按钮组件"""
    def __init__(self, bg_color=COLORS['primary'], text_color='#ffffff', **kwargs):
        super().__init__(**kwargs)
        self.bg_color = get_color_from_hex(bg_color)
        self.text_color = get_color_from_hex(text_color)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.color = self.text_color
        self.font_size = sp(16)
        self.size_hint_y = None
        self.height = dp(48)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])


class RoundedInput(TextInput):
    """圆角输入框组件"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.foreground_color = get_color_from_hex(COLORS['text'])
        self.font_size = sp(16)
        self.padding = [dp(12), dp(12)]
        self.bind(pos=self.update_canvas, size=self.update_canvas, focus=self.on_focus_change)
        self.is_focused = False

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # 背景
            Color(*get_color_from_hex('#ffffff'))
            border_color = COLORS['primary'] if self.is_focused else COLORS['border']
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            # 边框
            Color(*get_color_from_hex(border_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)], width=dp(1.5))

    def on_focus_change(self, instance, value):
        self.is_focused = value
        self.update_canvas()


class LanguageSelector(BoxLayout):
    """语言选择器组件"""
    def __init__(self, title="目标语言", default_index=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(48)
        self.spacing = dp(8)

        # 标题标签
        title_label = Label(
            text=title,
            size_hint_x=0.3,
            font_size=sp(15),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            text_size=(dp(100), dp(48))
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)

        # 下拉选择器按钮
        self.selected_index = default_index
        self.selector_btn = Button(
            text=LANGUAGES[default_index][0],
            size_hint_x=0.7,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            background_color=(0, 0, 0, 0),
            background_normal=''
        )
        self.selector_btn.bind(on_release=self.open_dropdown)
        self.selector_btn.bind(pos=self.update_btn_bg, size=self.update_btn_bg)
        self.add_widget(self.selector_btn)

        # 创建下拉菜单
        self.dropdown = DropDown()
        for i, (lang_display, lang_code) in enumerate(LANGUAGES):
            btn = Button(
                text=lang_display,
                size_hint_y=None,
                height=dp(44),
                font_size=sp(14),
                color=get_color_from_hex(COLORS['text'])
            )
            btn.bind(on_release=lambda btn=btn, idx=i: self.select_language(idx, btn))
            self.dropdown.add_widget(btn)

    def update_btn_bg(self, *args):
        self.selector_btn.canvas.before.clear()
        with self.selector_btn.canvas.before:
            Color(*get_color_from_hex(COLORS['primary_light']))
            RoundedRectangle(pos=self.selector_btn.pos, size=self.selector_btn.size, radius=[dp(8)])

    def open_dropdown(self, button):
        self.dropdown.open(button)

    def select_language(self, index, button):
        self.selected_index = index
        self.selector_btn.text = LANGUAGES[index][0]
        self.dropdown.dismiss()

    def get_selected_language(self):
        return LANGUAGES[self.selected_index][1]

    def get_selected_display(self):
        return LANGUAGES[self.selected_index][0]


class FileChooserPopup(Popup):
    """文件选择弹窗"""
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "选择文本文件"
        self.size_hint = (0.9, 0.8)
        self.auto_dismiss = False

        content = BoxLayout(orientation='vertical', spacing=dp(8))
        
        # 文件选择器
        file_chooser = FileChooserListView(
            filters=['*.txt', '*.md', '*.html', '*.json', '*.csv', '*.srt', '*.xml'],
            path='/sdcard' if platform == 'android' else '/'
        )
        self.file_chooser = file_chooser
        content.add_widget(file_chooser)

        # 文件名显示
        self.file_label = Label(
            text="未选择文件",
            size_hint_y=None,
            height=dp(36),
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        content.add_widget(self.file_label)

        file_chooser.bind(on_submit=self.file_selected)
        file_chooser.bind(selection=lambda *x: self.update_file_label(file_chooser.selection))

        # 按钮行
        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        cancel_btn = Button(
            text="取消",
            font_size=sp(15),
            color=get_color_from_hex(COLORS['text']),
            background_color=(0, 0, 0, 0),
            background_normal=''
        )
        cancel_btn.bind(on_release=self.dismiss)
        cancel_btn.bind(pos=self._cancel_bg, size=self._cancel_bg)
        
        confirm_btn = RoundedButton(
            text="确定翻译此文件",
            bg_color=COLORS['primary'],
            text_color='#ffffff'
        )
        confirm_btn.bind(on_release=self.confirm_file)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)

        self.content = content

    def _cancel_bg(self, *args):
        pass

    def update_file_label(self, selection):
        if selection:
            self.file_label.text = f"已选择: {os.path.basename(selection[0])}"
        else:
            self.file_label.text = "未选择文件"

    def file_selected(self, chooser, selection, *args):
        if selection:
            self.file_label.text = f"已选择: {os.path.basename(selection[0])}"

    def confirm_file(self, *args):
        if self.file_chooser.selection:
            self.callback(self.file_chooser.selection[0])
            self.dismiss()


# ======================== 主界面 ========================

class MainScreen(Screen):
    """主翻译界面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.translating = False
        self.ollama_checked = False
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=[0, 0, 0, 0])
        
        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        
        # ===== 顶部栏 =====
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(8), dp(16), dp(8)]
        )
        with header.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            Rectangle(pos=header.pos, size=header.size)
            Color(*get_color_from_hex(COLORS['border']))
            Rectangle(pos=(header.x, header.y), size=(header.width, dp(0.5)))

        header.add_widget(Label(
            text="📱 MobileTran",
            font_size=sp(20),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            halign='left',
            valign='middle',
            text_size=(dp(200), dp(44)),
            size_hint_x=0.7
        ))
        
        # 状态指示器
        self.status_label = Label(
            text="● 检查中",
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='right',
            size_hint_x=0.3
        )
        header.add_widget(self.status_label)
        main_layout.add_widget(header)

        # ===== 可滚动内容区域 =====
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=[dp(16), dp(12), dp(16), dp(12)])
        content.bind(minimum_height=content.setter('height'))
        self.content_layout = content

        # ---- 源语言区域 ----
        source_box = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        source_box.bind(minimum_height=source_box.setter('height'))
        
        source_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(32))
        source_header.add_widget(Label(
            text="📝 输入文本",
            font_size=sp(15),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            text_size=(dp(200), dp(32)),
            size_hint_x=0.7
        ))
        
        char_count = Label(
            text="0 字符",
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='right',
            size_hint_x=0.3
        )
        self.char_count_label = char_count
        source_header.add_widget(char_count)
        source_box.add_widget(source_header)

        # 文本输入
        self.text_input = RoundedInput(
            hint_text='在此输入要翻译的文本...',
            multiline=True,
            size_hint_y=None,
            height=dp(160),
            minimum_height=dp(80)
        )
        self.text_input.bind(text=self.on_text_change)
        source_box.add_widget(self.text_input)
        content.add_widget(source_box)

        # ---- 语言选择区域 ----
        lang_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(110))
        
        lang_card = BoxLayout(orientation='vertical', spacing=dp(4), padding=[dp(12), dp(8)])
        with lang_card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            RoundedRectangle(pos=lang_card.pos, size=lang_card.size, radius=[dp(8)])
        
        # 源语言
        src_lang = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36))
        src_lang.add_widget(Label(
            text="🌐 源语言: 自动检测",
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_x=0.7,
            text_size=(dp(200), dp(36))
        ))
        lang_card.add_widget(src_lang)

        # 目标语言选择
        self.lang_selector = LanguageSelector(title="目标语言:", default_index=0)
        lang_card.add_widget(self.lang_selector)
        
        lang_box.add_widget(lang_card)
        content.add_widget(lang_box)

        # ---- 功能区 ----
        action_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(240))
        
        action_card = BoxLayout(orientation='vertical', spacing=dp(8), padding=[dp(12), dp(8)])
        with action_card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            RoundedRectangle(pos=action_card.pos, size=action_card.size, radius=[dp(8)])

        action_card.add_widget(Label(
            text="⚡ 操作",
            font_size=sp(15),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(32),
            halign='left',
            text_size=(dp(280), dp(32))
        ))

        # 按钮网格
        btn_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(120))

        self.translate_btn = RoundedButton(
            text="🚀 翻译",
            bg_color=COLORS['primary'],
            text_color='#ffffff'
        )
        self.translate_btn.bind(on_release=self.start_translation)
        btn_grid.add_widget(self.translate_btn)

        import_btn = RoundedButton(
            text="📂 导入文件",
            bg_color=COLORS['accent'],
            text_color='#ffffff'
        )
        import_btn.bind(on_release=self.import_file)
        btn_grid.add_widget(import_btn)

        clear_btn = RoundedButton(
            text="🗑️ 清空",
            bg_color='#f1f3f4',
            text_color=COLORS['text']
        )
        clear_btn.bind(on_release=self.clear_input)
        btn_grid.add_widget(clear_btn)

        save_btn = RoundedButton(
            text="💾 保存结果",
            bg_color='#f1f3f4',
            text_color=COLORS['text']
        )
        save_btn.bind(on_release=self.save_result)
        btn_grid.add_widget(save_btn)

        action_card.add_widget(btn_grid)
        action_box.add_widget(action_card)
        content.add_widget(action_box)

        # ---- 翻译结果区域 ----
        result_box = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        result_box.bind(minimum_height=result_box.setter('height'))

        result_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(32))
        result_header.add_widget(Label(
            text="📄 翻译结果",
            font_size=sp(15),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            text_size=(dp(200), dp(32)),
            size_hint_x=0.7
        ))
        self.result_status = Label(
            text="",
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='right',
            size_hint_x=0.3
        )
        result_header.add_widget(self.result_status)
        result_box.add_widget(result_header)

        # 结果输出框
        self.result_input = RoundedInput(
            hint_text='翻译结果将在这里显示...',
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=dp(160),
            minimum_height=dp(80)
        )
        self.result_input.foreground_color = get_color_from_hex(COLORS['primary_dark'])
        result_box.add_widget(self.result_input)
        content.add_widget(result_box)

        # 进度条
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(4)
        )
        self.progress_bar.opacity = 0
        content.add_widget(self.progress_bar)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

        # 检查 Ollama 状态
        Clock.schedule_once(self.check_ollama, 0.5)

    def on_text_change(self, instance, value):
        count = len(value.replace('\n', ''))
        self.char_count_label.text = f"{count} 字符"
        # 清空结果当输入改变
        if value and self.result_input.text and not self.translating:
            pass  # 保持结果可见

    def update_status(self, text, is_ok=False):
        def _update(dt):
            if is_ok:
                self.status_label.text = f"● {text}"
                self.status_label.color = get_color_from_hex(COLORS['accent'])
            else:
                self.status_label.text = f"○ {text}"
                self.status_label.color = get_color_from_hex(COLORS['warning'])
        Clock.schedule_once(_update)

    def check_ollama(self, dt=None):
        def check():
            try:
                resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
                if resp.status_code == 200:
                    models = resp.json().get('models', [])
                    model_found = any(MODEL_NAME in m.get('name', '') for m in models)
                    if model_found:
                        self.update_status(f"{MODEL_NAME} ✓", True)
                    else:
                        self.update_status(f"模型未找到 ✗", False)
                        Clock.schedule_once(lambda dt: self.show_model_warning(models), 0)
                else:
                    self.update_status("Ollama 异常", False)
            except requests.exceptions.ConnectionError:
                self.update_status("Ollama 未启动", False)
            except Exception as e:
                self.update_status(f"错误: {str(e)[:20]}", False)
            self.ollama_checked = True
        threading.Thread(target=check, daemon=True).start()

    def show_model_warning(self, models):
        model_list = "\n".join([m.get('name', '未知') for m in models[:5]])
        msg = f"未找到模型 {MODEL_NAME}\n\n已安装模型:\n{model_list if model_list else '(无)'}\n\n请在 Termux 中运行:\nollama pull {MODEL_NAME}"
        Clock.schedule_once(lambda dt: self.show_popup("⚠️ 模型未找到", msg, COLORS['warning']))

    def show_popup(self, title, message, color=COLORS['primary']):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=[dp(16)])
        content.add_widget(Label(
            text=message,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            text_size=(dp(250), None),
            halign='center',
            size_hint_y=None,
            height=dp(120)
        ))
        btn = RoundedButton(text="确定", bg_color=color)
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def clear_input(self, *args):
        self.text_input.text = ""
        self.result_input.text = ""
        self.result_status.text = ""

    def import_file(self, *args):
        FileChooserPopup(callback=self.on_file_selected).open()

    def on_file_selected(self, filepath):
        try:
            # 尝试多种编码读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'utf-16', 'latin-1']
            content = None
            used_encoding = None
            for enc in encodings:
                try:
                    with open(filepath, 'r', encoding=enc) as f:
                        content = f.read()
                    used_encoding = enc
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue

            if content is None:
                self.show_popup("错误", "无法读取文件编码", COLORS['error'])
                return

            self.text_input.text = content
            self.show_popup(
                "文件已加载",
                f"已加载: {os.path.basename(filepath)}\n大小: {len(content)} 字符\n编码: {used_encoding}",
                COLORS['accent']
            )
        except Exception as e:
            self.show_popup("错误", f"读取文件失败: {str(e)}", COLORS['error'])

    def start_translation(self, *args):
        text = self.text_input.text.strip()
        if not text:
            self.show_popup("提示", "请先输入要翻译的文本", COLORS['warning'])
            return

        if self.translating:
            return

        # 检查文本长度
        if len(text) > 50000:
            self.show_popup("提示", "文本过长（超过50000字符），请减少输入", COLORS['warning'])
            return

        self.translating = True
        self.translate_btn.text = "⏳ 翻译中..."
        self.translate_btn.disabled = True
        self.progress_bar.opacity = 1
        self.progress_bar.value = 10
        self.result_input.text = ""
        self.result_status.text = "翻译中..."

        target_lang = self.lang_selector.get_selected_language()
        threading.Thread(target=self.do_translate, args=(text, target_lang), daemon=True).start()

    def update_progress(self, value):
        def _update(dt):
            self.progress_bar.value = value
        Clock.schedule_once(_update)

    def do_translate(self, text, target_lang):
        try:
            self.update_progress(20)

            # 分段处理大文本
            segments = self.split_text(text, max_chars=6000)
            total_segments = len(segments)
            results = []

            for i, segment in enumerate(segments):
                prompt = self.build_translate_prompt(segment, target_lang)
                
                payload = {
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 2048
                    }
                }

                resp = requests.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )

                if resp.status_code != 200:
                    self.update_progress(0)
                    Clock.schedule_once(lambda dt: self.on_translate_error(f"Ollama 返回错误: {resp.status_code}"), 0)
                    return

                result = resp.json().get('response', '').strip()
                
                # 如果主结果为空，尝试备用提示词
                if not result or result == segment:
                    backup_prompt = self.build_backup_prompt(segment, target_lang)
                    payload["prompt"] = backup_prompt
                    resp = requests.post(
                        f"{OLLAMA_HOST}/api/generate",
                        json=payload,
                        timeout=REQUEST_TIMEOUT
                    )
                    if resp.status_code == 200:
                        result = resp.json().get('response', '').strip()

                results.append(result if result else f"[翻译失败: 第{i+1}段]")

                # 更新进度
                progress = 20 + int((i + 1) / total_segments * 70)
                self.update_progress(progress)

            final_result = "\n".join(results)
            self.update_progress(95)

            Clock.schedule_once(lambda dt: self.on_translate_success(final_result, text), 0)

        except requests.exceptions.Timeout:
            self.update_progress(0)
            Clock.schedule_once(lambda dt: self.on_translate_error("翻译超时，请检查模型响应"), 0)
        except requests.exceptions.ConnectionError:
            self.update_progress(0)
            Clock.schedule_once(lambda dt: self.on_translate_error("无法连接 Ollama，请确保服务已启动"), 0)
        except Exception as e:
            self.update_progress(0)
            Clock.schedule_once(lambda dt: self.on_translate_error(f"翻译错误: {str(e)}"), 0)

    def build_translate_prompt(self, text, target_lang):
        return f"""你是一个专业翻译引擎。请将以下文本翻译成{target_lang}。

要求：
1. 保持原文的语义、语气和风格
2. 专业术语请准确翻译
3. 长句要合理切分，确保译文通顺自然
4. 不要添加任何额外解释或说明
5. 只返回翻译结果

待翻译文本：
{text}"""

    def build_backup_prompt(self, text, target_lang):
        return f"""Translate the following text to {target_lang}. Return ONLY the translation, nothing else.

Text:
{text}

Translation:"""

    def split_text(self, text, max_chars=6000):
        """智能分段"""
        if len(text) <= max_chars:
            return [text]

        segments = []
        
        # 优先按段落分
        paragraphs = text.split('\n')
        current = ""
        
        for para in paragraphs:
            if len(current) + len(para) + 1 <= max_chars:
                current += para + '\n'
            else:
                if current:
                    segments.append(current.strip())
                # 如果段落本身超过限制，按句号分
                if len(para) > max_chars:
                    sentences = para.replace('。', '．').replace('！', '！').replace('？', '？')
                    # 简单分段
                    for i in range(0, len(para), max_chars):
                        segments.append(para[i:i+max_chars])
                else:
                    current = para + '\n'
        
        if current:
            segments.append(current.strip())
        
        return segments

    def on_translate_success(self, result, original_text):
        self.translating = False
        self.translate_btn.text = "🚀 翻译"
        self.translate_btn.disabled = False
        self.progress_bar.opacity = 0
        self.result_input.text = result
        
        # 统计信息
        orig_len = len(original_text.replace('\n', ''))
        trans_len = len(result.replace('\n', ''))
        change_rate = ((trans_len - orig_len) / orig_len * 100) if orig_len > 0 else 0
        change_str = f"+{change_rate:.0f}%" if change_rate > 0 else f"{change_rate:.0f}%"
        self.result_status.text = f"✓ {len(result)} 字符 ({change_str})"

    def on_translate_error(self, error_msg):
        self.translating = False
        self.translate_btn.text = "🚀 翻译"
        self.translate_btn.disabled = False
        self.progress_bar.opacity = 0
        self.result_input.text = f"[错误] {error_msg}"
        self.result_status.text = "翻译失败"
        self.show_popup("翻译失败", error_msg, COLORS['error'])

    def save_result(self, *args):
        text = self.result_input.text.strip()
        if not text or text.startswith('[错误]'):
            self.show_popup("提示", "没有可保存的翻译结果", COLORS['warning'])
            return

        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=[dp(16)])
        content.add_widget(Label(
            text="输入文件名:",
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30)
        ))
        
        filename_input = RoundedInput(
            hint_text="文件名（不含后缀）",
            multiline=False,
            size_hint_y=None,
            height=dp(44)
        )
        filename_input.text = f"translated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        content.add_widget(filename_input)

        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(48))
        
        cancel_btn = Button(
            text="取消",
            font_size=sp(15),
            color=get_color_from_hex(COLORS['text']),
            background_color=(0, 0, 0, 0),
            background_normal=''
        )
        
        save_btn = RoundedButton(text="保存", bg_color=COLORS['primary'])
        
        popup = Popup(
            title="💾 保存翻译结果",
            content=content,
            size_hint=(0.85, 0.4),
            auto_dismiss=False
        )
        
        def do_save(*args):
            fname = filename_input.text.strip()
            if not fname:
                return
            if not fname.endswith('.txt'):
                fname += '.txt'
            
            try:
                # 保存到下载目录
                save_dir = '/sdcard/Download' if platform == 'android' else '.'
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, fname)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                popup.dismiss()
                file_size = os.path.getsize(save_path)
                self.show_popup(
                    "保存成功",
                    f"已保存到:\n{save_path}\n\n文件大小: {file_size:,} 字节",
                    COLORS['accent']
                )
            except Exception as e:
                self.show_popup("保存失败", str(e), COLORS['error'])

        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)

        popup.open()


class AboutScreen(Screen):
    """关于界面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'about'
        
        layout = BoxLayout(orientation='vertical', spacing=dp(16), padding=[dp(24)])
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            Rectangle(pos=layout.pos, size=layout.size)

        # 标题
        layout.add_widget(Label(
            text="📱 MobileTran",
            font_size=sp(28),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_y=None,
            height=dp(60)
        ))

        # 版本信息
        info_box = BoxLayout(orientation='vertical', spacing=dp(8), padding=[dp(16), dp(12)])
        with info_box.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            RoundedRectangle(pos=info_box.pos, size=info_box.size, radius=[dp(12)])

        info_items = [
            ("版本", "1.0.0"),
            ("翻译引擎", f"Ollama + {MODEL_NAME}"),
            ("运行方式", "本地离线翻译"),
            ("隐私保护", "数据不离开设备"),
            ("支持格式", "TXT/MD/HTML/JSON/CSV/SRT"),
        ]
        for label, value in info_items:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36))
            row.add_widget(Label(
                text=label,
                font_size=sp(14),
                bold=True,
                color=get_color_from_hex(COLORS['text']),
                halign='left',
                size_hint_x=0.35,
                text_size=(dp(100), dp(36))
            ))
            row.add_widget(Label(
                text=value,
                font_size=sp(14),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_x=0.65,
                text_size=(dp(200), dp(36))
            ))
            info_box.add_widget(row)
        
        layout.add_widget(info_box)
        layout.add_widget(Label(
            text="Made with ❤️ for Android",
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(40)
        ))

        # 返回按钮
        back_btn = RoundedButton(text="← 返回", bg_color=COLORS['primary'])
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        layout.add_widget(Label(size_hint_y=None, height=dp(20)))

        self.add_widget(layout)


# ======================== App 主入口 ========================

class MobileTranApp(App):
    """MobileTran Android 应用"""
    def build(self):
        self.title = "MobileTran"
        self.icon = 'icon.png'
        
        # 设置主题
        Window.clearcolor = get_color_from_hex(COLORS['background'])
        
        # 屏幕管理器
        sm = ScreenManager(transition=SlideTransition(duration=0.3))
        sm.add_widget(MainScreen())
        sm.add_widget(AboutScreen())
        
        # 窗口大小默认合适
        if platform != 'android':
            Window.size = (400, 700)
        
        return sm

    def on_pause(self):
        """Android 暂停回调"""
        return True

    def on_resume(self):
        """Android 恢复回调"""
        pass


if __name__ == '__main__':
    MobileTranApp().run()
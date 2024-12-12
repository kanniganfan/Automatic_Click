import win32gui
import win32con
import win32api
from tkinter import *
from tkinter import ttk, messagebox
import keyboard
import time
import json
import os
from threading import Thread
from win32_helper import (
    get_cursor_pos, get_control_at_pos, click_control,
    get_window_info, find_window_by_title, click_at_position,
    get_relative_pos
)

class AutoClicker:
    def __init__(self):
        self.window = Tk()
        self.window.title("自动点击工具")
        self.window.geometry("1200x800")
        self.window.configure(bg='#ffffff')
        self.window.attributes('-topmost', True)
        
        # 设置字体和颜色
        self.FONTS = {
            'heading1': ('微软雅黑', 24, 'bold'),
            'heading2': ('微软雅黑', 18, 'bold'),
            'heading3': ('微软雅黑', 14, 'bold'),
            'body': ('微软雅黑', 10),
            'caption': ('微软雅黑', 9),
            'code': ('Consolas', 10)
        }
        
        self.COLORS = {
            'primary': '#2196F3',       # 主色调
            'primary_light': '#BBDEFB',
            'primary_dark': '#1976D2',
            'secondary': '#FF4081',     # 强调色
            'success': '#4CAF50',
            'warning': '#FFC107',
            'danger': '#F44336',
            'info': '#00BCD4',
            'background': '#FFFFFF',
            'surface': '#F5F5F5',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'border': '#E0E0E0',
            'divider': '#EEEEEE'
        }
        
        # 设置样式
        self.style = ttk.Style()
        
        # 配置全局样式
        self.style.configure('TFrame', background=self.COLORS['background'])
        self.style.configure('Surface.TFrame', background=self.COLORS['surface'])
        
        # 标签样式
        self.style.configure('TLabel', 
            font=self.FONTS['body'],
            background=self.COLORS['background'],
            foreground=self.COLORS['text_primary'])
            
        self.style.configure('Heading1.TLabel',
            font=self.FONTS['heading1'],
            background=self.COLORS['background'],
            foreground=self.COLORS['primary_dark'])
            
        self.style.configure('Heading2.TLabel',
            font=self.FONTS['heading2'],
            background=self.COLORS['background'],
            foreground=self.COLORS['text_primary'])
            
        self.style.configure('Caption.TLabel',
            font=self.FONTS['caption'],
            background=self.COLORS['background'],
            foreground=self.COLORS['text_secondary'])
        
        # 按钮样式
        self.style.configure('TButton',
            font=self.FONTS['body'],
            padding=(20, 10))
            
        self.style.configure('Primary.TButton',
            font=self.FONTS['body'],
            padding=(20, 10))
            
        self.style.configure('Secondary.TButton',
            font=self.FONTS['body'],
            padding=(20, 10))
            
        self.style.configure('Success.TButton',
            font=self.FONTS['body'],
            padding=(20, 10))
            
        self.style.configure('Warning.TButton',
            font=self.FONTS['body'],
            padding=(20, 10))
            
        self.style.configure('Danger.TButton',
            font=self.FONTS['body'],
            padding=(20, 10))
        
        # 标签框样式
        self.style.configure('Card.TLabelframe',
            background=self.COLORS['background'])
            
        self.style.configure('Card.TLabelframe.Label',
            font=self.FONTS['heading3'],
            background=self.COLORS['background'],
            foreground=self.COLORS['text_primary'])
        
        # 保存的按钮配置
        self.config_file = "button_config.json"
        self.button_configs = self.load_configs()
        
        # 按键录制状态
        self.recording = False
        self.current_keys = set()
        
        # 实时检测状态
        self.detecting = False
        self.current_window = None
        self.current_pos = None
        
        self.create_widgets()
        self.start_hotkey_listener()
        
        # 添加最小化热键
        keyboard.add_hotkey('ctrl+m', self.minimize_window)
    
    def minimize_window(self):
        """最小化窗口"""
        self.window.iconify()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.window, style='TFrame')
        main_frame.pack(fill=BOTH, expand=True, padx=30, pady=20)
        
        # 顶部区域
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=X, pady=(0, 30))
        
        # Logo和标题区
        title_frame = ttk.Frame(header_frame, style='TFrame')
        title_frame.pack(side=LEFT)
        
        ttk.Label(title_frame, text="自动点击工具", 
                 style='Heading1.TLabel').pack(side=TOP, anchor=W)
        ttk.Label(title_frame, text="快速、便捷的自动化点击解决方案", 
                 style='Caption.TLabel').pack(side=TOP, anchor=W, pady=(5,0))
        
        # 右上角操作区
        action_frame = ttk.Frame(header_frame, style='TFrame')
        action_frame.pack(side=RIGHT, pady=(10,0))
        
        ttk.Label(action_frame, text="Ctrl+M 快速最小化", 
                 style='Caption.TLabel').pack(side=RIGHT)
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').pack(fill=X, pady=(0, 30))
        
        # 内容区域
        content_frame = ttk.Frame(main_frame, style='TFrame')
        content_frame.pack(fill=BOTH, expand=True)
        
        # 左侧：控件检测
        left_frame = ttk.LabelFrame(content_frame, text="位置检测", 
                                  style='Card.TLabelframe')
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 15))
        
        # 说明卡片
        info_card = ttk.Frame(left_frame, style='Surface.TFrame')
        info_card.pack(fill=X, pady=(0, 20))
        
        ttk.Label(info_card, text="使用说明",
                 style='Heading2.TLabel').pack(anchor=W, padx=20, pady=(20,10))
        
        steps = [
            "1. 点击'开始检测'按钮",
            "2. 将鼠标移到目标位置",
            "3. 按F1记录位置",
            "4. 按ESC停止检测"
        ]
        
        for step in steps:
            ttk.Label(info_card, text=step,
                     style='TLabel').pack(anchor=W, padx=20, pady=2)
        
        ttk.Separator(info_card, orient='horizontal').pack(fill=X, padx=20, pady=20)
        
        # 检测按钮
        self.detect_btn = ttk.Button(left_frame, 
            text="开始检测",
            command=self.toggle_detect,
            style='Primary.TButton')
        self.detect_btn.pack(pady=(0,20))
        
        # 信息显示区
        info_frame = ttk.LabelFrame(left_frame, text="实时信息", 
                                  style='Card.TLabelframe')
        info_frame.pack(fill=BOTH, expand=True)
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(fill=BOTH, expand=True, padx=1, pady=1)
        
        self.info_text = Text(text_frame,
            font=self.FONTS['code'],
            bg=self.COLORS['surface'],
            fg=self.COLORS['text_primary'],
            relief='flat',
            padx=15,
            pady=15,
            spacing1=5,
            spacing2=5,
            spacing3=5,
            selectbackground=self.COLORS['primary_light'],
            selectforeground=self.COLORS['text_primary'],
            wrap='none')
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(text_frame, orient="vertical", 
                                  command=self.info_text.yview)
        scrollbar_x = ttk.Scrollbar(info_frame, orient="horizontal", 
                                  command=self.info_text.xview)
        
        self.info_text.configure(yscrollcommand=scrollbar_y.set,
                               xscrollcommand=scrollbar_x.set)
        
        # 布局文本框和滚动条
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.info_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar_x.pack(side=BOTTOM, fill=X)
        
        # 右侧：配置区域
        right_frame = ttk.LabelFrame(content_frame, text="配置管理", 
                                   style='Card.TLabelframe')
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(15,0))
        
        # 热键设置区
        hotkey_frame = ttk.Frame(right_frame, style='Surface.TFrame')
        hotkey_frame.pack(fill=X, pady=(0,20))
        
        ttk.Label(hotkey_frame, text="热键设置",
                 style='Heading2.TLabel').pack(anchor=W, padx=20, pady=(20,10))
        
        key_frame = ttk.Frame(hotkey_frame, style='Surface.TFrame')
        key_frame.pack(fill=X, padx=20, pady=(0,20))
        
        ttk.Label(key_frame, text="当前热键:", 
                 style='TLabel').pack(side=LEFT)
        self.hotkey_label = ttk.Label(key_frame,
            text="(未设置)",
            style='Caption.TLabel')
        self.hotkey_label.pack(side=LEFT, padx=10)
        
        self.record_btn = ttk.Button(hotkey_frame,
            text="录制热键",
            command=self.toggle_record,
            style='Success.TButton')
        self.record_btn.pack(padx=20, pady=(0,20))
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill=X, pady=20)
        
        # 配置设置区
        config_frame = ttk.Frame(right_frame, style='TFrame')
        config_frame.pack(fill=X, pady=(0,20))
        
        ttk.Label(config_frame, text="配置名称:", 
                 style='TLabel').pack(anchor=W)
        self.config_name_entry = ttk.Entry(config_frame, 
                                         font=self.FONTS['body'])
        self.config_name_entry.pack(fill=X, pady=(5,15))
        
        ttk.Label(config_frame, text="点击方式:", 
                 style='TLabel').pack(anchor=W)
        
        self.click_mode = StringVar(value="position")
        
        mode_frame = ttk.Frame(config_frame, style='TFrame')
        mode_frame.pack(fill=X, pady=5)
        
        ttk.Radiobutton(mode_frame,
            text="坐标点击（推荐）",
            variable=self.click_mode,
            value="position").pack(side=LEFT, padx=(0,20))
            
        ttk.Radiobutton(mode_frame,
            text="控件点击",
            variable=self.click_mode,
            value="control").pack(side=LEFT)
        
        # 操作按钮
        button_frame = ttk.Frame(config_frame, style='TFrame')
        button_frame.pack(fill=X, pady=20)
        
        ttk.Button(button_frame,
            text="保存配置",
            command=self.save_current_config,
            style='Primary.TButton').pack(side=LEFT, padx=(0,10))
            
        ttk.Button(button_frame,
            text="测试点击",
            command=self.test_click,
            style='Warning.TButton').pack(side=LEFT)
        
        # 配置列表
        list_frame = ttk.LabelFrame(right_frame, text="已保存配置", 
                                  style='Card.TLabelframe')
        list_frame.pack(fill=BOTH, expand=True)
        
        # 创建带滚动条的列表框
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=BOTH, expand=True, padx=1, pady=1)
        
        self.config_listbox = Listbox(listbox_frame,
            font=self.FONTS['body'],
            bg=self.COLORS['surface'],
            fg=self.COLORS['text_primary'],
            relief='flat',
            selectmode=SINGLE,
            selectbackground=self.COLORS['primary_light'],
            selectforeground=self.COLORS['text_primary'],
            activestyle='none')
            
        list_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical",
                                     command=self.config_listbox.yview)
        self.config_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        list_scrollbar.pack(side=RIGHT, fill=Y)
        self.config_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        ttk.Button(list_frame,
            text="删除选中",
            command=self.delete_selected_config,
            style='Danger.TButton').pack(pady=20)
        
        # 状态栏
        status_frame = ttk.Frame(self.window, style='Surface.TFrame')
        status_frame.pack(fill=X)
        
        self.status_label = ttk.Label(status_frame,
            text="状态：就绪",
            style='Caption.TLabel')
        self.status_label.pack(side=LEFT, padx=20, pady=10)
        
        # 更新配置列表
        self.update_config_list()
    
    def toggle_detect(self):
        """切换检测状态"""
        self.detecting = not self.detecting
        if self.detecting:
            self.detect_btn.configure(text="停止检测")
            self.status_label.configure(text="状态：正在检测...")
            self.detect_thread()
        else:
            self.detect_btn.configure(text="开始检测")
            self.status_label.configure(text="状态：就绪")
    
    def detect_thread(self):
        """实时检测线程"""
        def update():
            if not self.detecting:
                return
                
            try:
                # 获取鼠标位置
                x, y = get_cursor_pos()
                # 获取控件信息
                control_info = get_control_at_pos(x, y)
                
                if control_info and control_info['control']:
                    window_info = control_info['path'][-1]  # 最顶层窗口
                    
                    # 检查F1是否按下
                    if keyboard.is_pressed('f1'):
                        self.current_window = window_info['hwnd']
                        self.current_pos = get_relative_pos(self.current_window, x, y)
                        self.status_label.configure(text=f"状态：已记录位置 ({self.current_pos[0]}, {self.current_pos[1]})")
                        time.sleep(0.2)  # 防止重复触发
                    
                    # 更新信息显示
                    info = "--- 窗口��息 ---\n"
                    info += f"标题: {window_info['text']}\n"
                    info += f"类名: {window_info['class_name']}\n"
                    info += f"句柄: {window_info['hwnd']}\n"
                    info += f"大小: {window_info['width']}x{window_info['height']}\n\n"
                    
                    info += "--- 当前位置 ---\n"
                    info += f"屏幕坐标: ({x}, {y})\n"
                    rel_pos = get_relative_pos(window_info['hwnd'], x, y)
                    info += f"窗口相对坐标: ({rel_pos[0]}, {rel_pos[1]})\n"
                    
                    if self.current_pos:
                        info += f"\n--- 记录的位置 ---\n"
                        info += f"相对坐标: ({self.current_pos[0]}, {self.current_pos[1]})\n"
                    
                    if self.click_mode.get() == "control":
                        info += "\n--- 控件信息 ---\n"
                        info += f"类名: {control_info['control']['class_name']}\n"
                        info += f"文本: {control_info['control']['text']}\n"
                        info += f"句柄: {control_info['control']['hwnd']}\n"
                    
                    self.info_text.delete(1.0, END)
                    self.info_text.insert(END, info)
                    
                # 检查ESC是否按下
                if keyboard.is_pressed('esc'):
                    self.detecting = False
                    self.detect_btn.configure(text="开始检测")
                    self.status_label.configure(text="状态：就绪")
                    return
                
            except Exception as e:
                print(f"检测出错: {str(e)}")
            
            # 继续检测
            if self.detecting:
                self.window.after(100, update)
        
        update()
    
    def toggle_record(self):
        """切换录制状态"""
        if not self.current_window:
            messagebox.showwarning("警告", "请先检测并选择一个位置！")
            return
            
        if not self.recording:
            self.recording = True
            self.record_btn.configure(text="停止录制")
            self.current_keys.clear()
            self.hotkey_label.configure(text="请按下快捷键...")
            self.status_label.configure(text="状态：正在录制快捷键...")
            
            # 开始录制线程
            Thread(target=self.record_hotkey, daemon=True).start()
        else:
            self.recording = False
            self.record_btn.configure(text="录制热键")
            self.status_label.configure(text="状态：就绪")

    def record_hotkey(self):
        while self.recording:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                self.current_keys.add(event.name)
                key_text = ' + '.join(sorted(self.current_keys))
                self.hotkey_label.configure(text=key_text)
            elif event.event_type == keyboard.KEY_UP:
                if event.name in self.current_keys:
                    self.current_keys.remove(event.name)
            
            if not self.current_keys:  # 当所有键都释放时停止录制
                self.recording = False
                self.record_btn.configure(text="录制热键")
                self.status_label.configure(text="状态：就绪")
                break
            
            time.sleep(0.1)
    
    def test_click(self):
        """测试点击"""
        if not self.current_window:
            messagebox.showwarning("警告", "请先检测并选择一个位置！")
            return
            
        if self.click_mode.get() == "position":
            if click_at_position(self.current_window, self.current_pos[0], self.current_pos[1]):
                self.status_label.configure(text="状态：点击成功")
            else:
                self.status_label.configure(text="状态：点击失败")
        else:
            if click_control(self.current_window):
                self.status_label.configure(text="状态：点击成功")
            else:
                self.status_label.configure(text="状态：点击失败")

    def load_configs(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_configs(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.button_configs, f, ensure_ascii=False, indent=2)
    
    def update_config_list(self):
        self.config_listbox.delete(0, END)
        for name, config in self.button_configs.items():
            self.config_listbox.insert(END, f"{name} ({config['hotkey']})")
    
    def save_current_config(self):
        if not self.current_window:
            messagebox.showwarning("警告", "请先检测并选择一个位置！")
            return
            
        name = self.config_name_entry.get().strip()
        hotkey = self.hotkey_label.cget("text")
        
        if not name or hotkey == "(未设置)":
            messagebox.showwarning("警告", "请输入配置名称和设置热键！")
            return
        
        self.button_configs[name] = {
            'window_hwnd': self.current_window,
            'click_mode': self.click_mode.get(),
            'position': self.current_pos,
            'hotkey': hotkey,
            'window_info': get_window_info(self.current_window)
        }
        
        self.save_configs()
        self.update_config_list()
        self.status_label.configure(text=f"状态：配置已保存 - {name} ({hotkey})")
    
    def delete_selected_config(self):
        if not self.config_listbox.curselection():
            return
            
        index = self.config_listbox.curselection()[0]
        name = list(self.button_configs.keys())[index]
        del self.button_configs[name]
        
        self.save_configs()
        self.update_config_list()
        self.status_label.configure(text=f"状态：已删除配置 - {name}")

    def click_config(self, config):
        """执行点击配置"""
        try:
            hwnd = config['window_hwnd']
            
            # 获取窗口状态
            placement = win32gui.GetWindowPlacement(hwnd)
            was_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            
            # 如果窗口是最小化状态，先恢复它
            if was_minimized:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.1)  # 等待窗口恢复
            
            # 激活窗口并执行点击
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)  # 等待窗口激活
            
            if config['click_mode'] == 'position':
                click_at_position(hwnd, config['position'][0], config['position'][1])
            else:
                click_control(hwnd)
            
            # 如果之前是最小化状态，点击后重新最小化
            if was_minimized:
                time.sleep(0.1)  # 等待点击完成
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            
        except Exception as e:
            print(f"点击失败: {str(e)}")

    def start_hotkey_listener(self):
        def hotkey_thread():
            while True:
                for name, config in self.button_configs.items():
                    hotkey = config['hotkey'].lower()
                    keys = set(key.strip() for key in hotkey.split('+'))
                    
                    # 检查所有按键是否同时按下
                    if all(keyboard.is_pressed(key) for key in keys):
                        self.click_config(config)
                        # 等待按键释放
                        while any(keyboard.is_pressed(key) for key in keys):
                            time.sleep(0.01)
                
                time.sleep(0.01)  # 减少CPU使用率
        
        Thread(target=hotkey_thread, daemon=True).start()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = AutoClicker()
    app.run() 
import win32gui
import win32con
import win32api
from tkinter import *
from tkinter import ttk
import keyboard
import time

class ButtonHandleFinder:
    def __init__(self):
        self.window = Tk()
        self.window.title("按钮句柄获取工具")
        self.window.geometry("500x300")
        self.window.attributes('-topmost', True)  # 窗口置顶
        
        self.create_widgets()
        
    def create_widgets(self):
        # 说明标签
        instruction_label = ttk.Label(self.window, 
            text="使用方法：\n1. 点击'开始获取'按钮\n2. 将鼠标移动到目标按钮上\n3. 按下F2键获取句柄\n4. 按ESC键停止获取",
            justify=LEFT)
        instruction_label.pack(pady=10, padx=10)
        
        # 开始获取按钮
        self.start_btn = ttk.Button(self.window, text="开始获取", command=self.start_capture)
        self.start_btn.pack(pady=5)
        
        # 信息显示区域
        self.info_text = Text(self.window, width=60, height=10)
        self.info_text.pack(pady=10, padx=10)
        
        # 状态标签
        self.status_label = ttk.Label(self.window, text="状态：就绪")
        self.status_label.pack(pady=5)
        
        self.capturing = False
        
    def start_capture(self):
        if not self.capturing:
            self.capturing = True
            self.start_btn.configure(text="停止获取")
            self.status_label.configure(text="状态：正在获取（按F2获取句柄，ESC停止）")
            self.capture_thread()
        else:
            self.stop_capture()
    
    def stop_capture(self):
        self.capturing = False
        self.start_btn.configure(text="开始获取")
        self.status_label.configure(text="状态：就绪")
    
    def capture_thread(self):
        def on_f2_press():
            if not self.capturing:
                return
                
            # 获取鼠标位置
            x, y = win32api.GetCursorPos()
            # 获取鼠标位置下的窗口句柄
            hwnd = win32gui.WindowFromPoint((x, y))
            
            # 获取控件信息
            try:
                class_name = win32gui.GetClassName(hwnd)
                text = win32gui.GetWindowText(hwnd)
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                parent = win32gui.GetParent(hwnd)
                parent_text = win32gui.GetWindowText(parent)
                
                info = f"\n--- 新获取的控件信息 ---"
                info += f"\n句柄: {hwnd}"
                info += f"\n类名: {class_name}"
                info += f"\n文本: {text}"
                info += f"\n样式: {style}"
                info += f"\n父窗口: {parent_text} (句柄: {parent})"
                info += f"\n位置: ({x}, {y})\n"
                
                self.info_text.insert(END, info)
                self.info_text.see(END)
            except Exception as e:
                self.info_text.insert(END, f"\n获取控件信息时出错: {str(e)}\n")
                self.info_text.see(END)
        
        def check_keys():
            if not self.capturing:
                return
            
            if keyboard.is_pressed('f2'):
                on_f2_press()
                time.sleep(0.2)  # 防止重复触发
            elif keyboard.is_pressed('esc'):
                self.stop_capture()
                return
                
            self.window.after(100, check_keys)
        
        check_keys()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ButtonHandleFinder()
    app.run() 
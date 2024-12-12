import win32gui
import win32con
import win32api
from tkinter import *
from tkinter import ttk

class HandleFinder:
    def __init__(self):
        self.window = Tk()
        self.window.title("窗口句柄获取工具")
        self.window.geometry("600x400")
        
        # 创建界面元素
        self.create_widgets()
        
    def create_widgets(self):
        # 刷新按钮
        refresh_btn = ttk.Button(self.window, text="刷新窗口列表", command=self.refresh_windows)
        refresh_btn.pack(pady=10)
        
        # 窗口列表
        self.window_listbox = Listbox(self.window, width=70, height=10)
        self.window_listbox.pack(pady=5)
        self.window_listbox.bind('<<ListboxSelect>>', self.on_select_window)
        
        # 控件信息显示
        self.info_text = Text(self.window, width=70, height=10)
        self.info_text.pack(pady=5)
        
        # 初始化窗口列表
        self.refresh_windows()
        
    def refresh_windows(self):
        self.window_listbox.delete(0, END)
        self.windows = []
        
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    self.windows.append((hwnd, title))
                    self.window_listbox.insert(END, f"{title} (Handle: {hwnd})")
        
        win32gui.EnumWindows(enum_windows_callback, None)
    
    def on_select_window(self, event):
        if not self.window_listbox.curselection():
            return
            
        selected_idx = self.window_listbox.curselection()[0]
        hwnd = self.windows[selected_idx][0]
        
        self.info_text.delete(1.0, END)
        self.info_text.insert(END, f"选中窗口句柄: {hwnd}\n")
        
        # 获取窗口中的控件
        def enum_child_callback(child_hwnd, _):
            class_name = win32gui.GetClassName(child_hwnd)
            text = win32gui.GetWindowText(child_hwnd)
            style = win32gui.GetWindowLong(child_hwnd, win32con.GWL_STYLE)
            
            if "button" in class_name.lower() or style & win32con.BS_PUSHBUTTON:
                self.info_text.insert(END, f"\n按钮句柄: {child_hwnd}")
                self.info_text.insert(END, f"\n类名: {class_name}")
                self.info_text.insert(END, f"\n文本: {text}")
                self.info_text.insert(END, f"\n样式: {style}\n")
        
        try:
            win32gui.EnumChildWindows(hwnd, enum_child_callback, None)
        except Exception as e:
            self.info_text.insert(END, f"\n获取控件信息时出错: {str(e)}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = HandleFinder()
    app.run() 
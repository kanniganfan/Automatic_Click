import win32gui
import win32con
import win32api
import time

# 按钮相关消息
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_MOUSEMOVE = 0x0200
BM_CLICK = 0x00F5
MK_LBUTTON = 0x0001

def click_at_coords(hwnd, x, y):
    """在指定坐标点击"""
    # 获取窗口位置
    rect = win32gui.GetWindowRect(hwnd)
    # 计算相对坐标
    relative_x = x - rect[0]
    relative_y = y - rect[1]
    # 构造坐标参数
    lParam = relative_y << 16 | relative_x
    
    # 激活窗口
    parent = win32gui.GetParent(hwnd)
    if parent:
        win32gui.SetForegroundWindow(parent)
    else:
        win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    
    # 发送鼠标移动消息
    win32gui.SendMessage(hwnd, WM_MOUSEMOVE, 0, lParam)
    time.sleep(0.1)
    
    # 发送鼠标点击消息
    win32gui.SendMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lParam)
    time.sleep(0.1)
    win32gui.SendMessage(hwnd, WM_LBUTTONUP, 0, lParam)

def click_control(hwnd):
    """点击控件"""
    try:
        # 获取控件位置
        rect = win32gui.GetWindowRect(hwnd)
        # 计算中心点
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        
        # 保存当前鼠标位置
        current_pos = win32api.GetCursorPos()
        
        # 移动鼠标到控件中心
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.1)
        
        # 点击控件
        click_at_coords(hwnd, center_x, center_y)
        
        # 恢复鼠标位置
        win32api.SetCursorPos(current_pos)
        
    except Exception as e:
        print(f"点击失败: {str(e)}")

# 从button_finder导入函数
from button_finder import find_clickable_at_point
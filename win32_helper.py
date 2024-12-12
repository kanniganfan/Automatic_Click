import win32gui
import win32con
import win32api
import time
from ctypes import windll, c_long, c_wchar_p, c_ulong, byref, Structure, c_int

# Windows API常量
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_CLICK = 0x00F5
BM_CLICK = 0x00F5

# 窗口状态
SW_RESTORE = 9
SW_SHOW = 5
SW_SHOWNORMAL = 1

def fast_click(hwnd, lParam=0):
    """快速点击（无延时）"""
    try:
        win32gui.PostMessage(hwnd, WM_LBUTTONDOWN, 0, lParam)
        win32gui.PostMessage(hwnd, WM_LBUTTONUP, 0, lParam)
        win32gui.PostMessage(hwnd, BM_CLICK, 0, 0)
        return True
    except:
        return False

def click_at_position(hwnd, x, y, relative=True):
    """在指定位置点击（无鼠标移动）"""
    try:
        # 获取窗口位置
        rect = win32gui.GetWindowRect(hwnd)
        
        # 计算相对于窗口的坐标
        client_x = x if relative else (x - rect[0])
        client_y = y if relative else (y - rect[1])
        
        # 构造坐标参数
        lParam = client_y << 16 | client_x
        
        # 快速点击
        return fast_click(hwnd, lParam)
        
    except Exception as e:
        print(f"点击失败: {str(e)}")
        return False

def click_control(hwnd):
    """点击控件（无鼠标移动）"""
    try:
        # 直接发送点击消息
        return fast_click(hwnd)
    except Exception as e:
        print(f"点击失败: {str(e)}")
        return False

def get_cursor_pos():
    """获取鼠标位置"""
    return win32api.GetCursorPos()

def get_window_at_cursor():
    """获取鼠标位置的窗口信息"""
    x, y = get_cursor_pos()
    hwnd = win32gui.WindowFromPoint((x, y))
    if not hwnd:
        return None
        
    # 获取最上层子窗口
    child_hwnd = win32gui.ChildWindowFromPoint(hwnd, (x, y))
    if child_hwnd and child_hwnd != hwnd:
        hwnd = child_hwnd
        
    return get_window_info(hwnd)

def get_relative_pos(hwnd, x, y):
    """获取相对于窗口的坐标"""
    rect = win32gui.GetWindowRect(hwnd)
    return (x - rect[0], y - rect[1])

def get_window_info(hwnd):
    """获取窗口信息"""
    if not hwnd:
        return None
    
    try:
        class_name = win32gui.GetClassName(hwnd)
        window_text = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        
        return {
            'hwnd': hwnd,
            'class_name': class_name,
            'text': window_text,
            'rect': rect,
            'style': style,
            'ex_style': ex_style,
            'is_visible': bool(style & win32con.WS_VISIBLE),
            'is_enabled': not bool(style & win32con.WS_DISABLED),
            'width': rect[2] - rect[0],
            'height': rect[3] - rect[1]
        }
    except:
        return None

def get_control_path(hwnd):
    """获取控件的层级路径"""
    path = []
    current_hwnd = hwnd
    
    while current_hwnd:
        info = get_window_info(current_hwnd)
        if info:
            path.append(info)
        current_hwnd = win32gui.GetParent(current_hwnd)
    
    return path

def get_control_at_pos(x, y):
    """获取指定位置的控件完整信息"""
    hwnd = win32gui.WindowFromPoint((x, y))
    if not hwnd:
        return None
        
    # 获取最上层子窗口
    child_hwnd = win32gui.ChildWindowFromPoint(hwnd, (x, y))
    if child_hwnd and child_hwnd != hwnd:
        hwnd = child_hwnd
    
    # 获取控件路径
    control_path = get_control_path(hwnd)
    
    # 获取所有子窗口
    children = []
    def enum_child_proc(child_hwnd, mouse_pos):
        try:
            rect = win32gui.GetWindowRect(child_hwnd)
            if rect[0] <= mouse_pos[0] <= rect[2] and rect[1] <= mouse_pos[1] <= rect[3]:
                children.append(get_window_info(child_hwnd))
        except:
            pass
        return True
    
    win32gui.EnumChildWindows(hwnd, enum_child_proc, (x, y))
    
    return {
        'control': get_window_info(hwnd),
        'path': control_path,
        'children': children
    }

def find_window_by_title(title_part):
    """通过标题部分查找窗口"""
    result = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if title_part.lower() in window_text.lower():
                result.append(hwnd)
        return True
    win32gui.EnumWindows(callback, None)
    return result

def find_control_by_class(parent_hwnd, class_name):
    """查找指定类名的控件"""
    result = []
    def callback(hwnd, extra):
        if win32gui.GetClassName(hwnd) == class_name:
            result.append(hwnd)
        return True
    win32gui.EnumChildWindows(parent_hwnd, callback, None)
    return result 
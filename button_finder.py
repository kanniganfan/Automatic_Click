import win32gui
import win32con

def is_clickable_cursor():
    """检查当前鼠标是否为手型光标"""
    try:
        cursor = win32gui.GetCursorInfo()[1]
        return cursor in [32649, 65561]  # 手型光标的ID
    except:
        return False

def get_window_info(hwnd):
    """获取窗口信息"""
    try:
        class_name = win32gui.GetClassName(hwnd)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        return class_name, style, ex_style
    except:
        return None, None, None

def find_clickable_at_point(x, y):
    """查找可点击的控件"""
    # 获取鼠标位置的窗口句柄
    hwnd = win32gui.WindowFromPoint((x, y))
    if not hwnd:
        return None
        
    # 如果鼠标是手型，直接返回当前句柄
    if is_clickable_cursor():
        return hwnd
        
    # 获取子窗口
    child_hwnd = win32gui.ChildWindowFromPoint(hwnd, (x, y))
    if child_hwnd and child_hwnd != hwnd:
        if is_clickable_cursor():
            return child_hwnd
            
    # 获取所有子窗口
    child_windows = []
    def enum_child_proc(child_hwnd, mouse_pos):
        try:
            rect = win32gui.GetWindowRect(child_hwnd)
            if rect[0] <= mouse_pos[0] <= rect[2] and rect[1] <= mouse_pos[1] <= rect[3]:
                child_windows.append(child_hwnd)
        except:
            pass
        return True
    
    win32gui.EnumChildWindows(hwnd, enum_child_proc, (x, y))
    
    # 检查所有子窗口
    for child_hwnd in reversed(child_windows):  # 从上到下检查
        if is_clickable_cursor():
            return child_hwnd
    
    return hwnd 
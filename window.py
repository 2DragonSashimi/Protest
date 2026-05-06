class Window:
    def __init__(self, window_id, x, y, w, h, bg_color, parent=None):
        self.window_id = window_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bg_color = bg_color
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)
        self.sequence = 0

    def is_point_in_window(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def find_clicked_window(self, px, py):
        if not self.is_point_in_window(px, py):
            return None
        for child in reversed(self.children):
            result = child.find_clicked_window(px, py)
            if result:
                return result
        return self

    def move_to_front(self):
        if self.parent:
            self.parent.children.remove(self)
            self.parent.children.append(self)
            self.parent.move_to_front()

    def set_sequence(self, seq):
        self.sequence = seq
        for i, child in enumerate(self.children):
            seq = child.set_sequence(seq + 1)
        return seq

class WindowManager:
    def __init__(self):
        self.windows = {}
        self.root_id = None

    def init(self, mRoot, W, H):
        self.windows = {}
        root = Window(mRoot, 0, 0, W, H, 0)
        self.windows[mRoot] = root
        self.root_id = mRoot
        _ = root.set_sequence(1)

    def create(self, mID, x0, y0, w, h, mColor, mParent):
        parent = self.windows[mParent]
        new_x = parent.x + x0
        new_y = parent.y + y0
        new_w = w
        new_h = h
        window = Window(mID, new_x, new_y, new_w, new_h, mColor, parent)
        self.windows[mID] = window
        return len(self.windows)

    def remove(self, mID):
        window = self.windows.get(mID)
        if not window:
            return len(self.windows)

        children = window.children[:]
        for child in children:
            self.remove(child.window_id)

        if window.parent:
            window.parent.children.remove(window)

        del self.windows[mID]
        return len(self.windows)

    def click(self, x, y):
        clicked_window = list(self.windows.values())[0].find_clicked_window(x, y)
        if clicked_window:
            clicked_window.move_to_front()
            return clicked_window.window_id
        return -1

    def getColor(self, x, y):
        clicked_window = list(self.windows.values())[0].find_clicked_window(x, y)
        if clicked_window:
            return clicked_window.bg_color
        return 0

    def getOrder(self, mID):
        _ = self.windows[self.root_id].set_sequence(1)
        return self.windows[mID].sequence

wm = WindowManager()

def init(mRoot : int, W : int, H : int) -> None:
    wm.init(mRoot, W, H)

def create(mID : int, x0 : int, y0 : int, w : int, h : int, mColor : int, mParent : int) -> int:
    return wm.create(mID, x0, y0, w, h, mColor, mParent)

def remove(mID : int) -> int:
    return wm.remove(mID)

def click(x : int, y : int) -> int:
    return wm.click(x, y)

def getColor(x : int, y : int) -> int:
    return wm.getColor(x, y)

def getOrder(mID : int) -> int:
    return wm.getOrder(mID)

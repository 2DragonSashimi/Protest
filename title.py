class RESULT_E:
    def __init__(self, success, locname):
        self.success = success
        self.locname = locname

class RESULT_S:
    def __init__(self, cnt, carlist):
        self.cnt = cnt
        self.carlist = carlist # [str] * 5

def init(N : int, M : int, L : int) -> None:
    pass

def enter(mTime : int, mCarNo : str) -> RESULT_E:
    return RESULT_E(-1, "")

def pullout(mTime : int, mCarNo : str) -> int:
    return -1

def search(mTime : int, mStr : str) -> RESULT_S:
    return RESULT_S(-1, ["", "", "", "", ""])

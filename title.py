import heapq


class RESULT_E:
    def __init__(self, success, locname):
        self.success = success
        self.locname = locname


class RESULT_S:
    def __init__(self, cnt, carlist):
        self.cnt = cnt
        self.carlist = carlist  # [str] * 5


# global variables
gN = 0
gM = 0
gL = 0

free_cnt = []        # 각 구역의 빈 슬롯 개수
free_slots = []      # 각 구역의 빈 슬롯 번호 min-heap

parked = {}          # car -> (ticket, enter_time, zone, slot)
towed = {}           # car -> (ticket, tow_time)

tow_heap = []        # (tow_time, ticket, car)

park_suffix = {}     # suffix -> heap[(car, ticket)]
tow_suffix = {}      # suffix -> heap[(car, ticket)]

ticket_id = 0


def init(N: int, M: int, L: int) -> None:
    global gN, gM, gL
    global free_cnt, free_slots
    global parked, towed, tow_heap
    global park_suffix, tow_suffix
    global ticket_id

    gN = N
    gM = M
    gL = L

    free_cnt = [M] * N
    free_slots = [list(range(M)) for _ in range(N)]
    for i in range(N):
        heapq.heapify(free_slots[i])

    parked = {}
    towed = {}
    tow_heap = []

    park_suffix = {}
    tow_suffix = {}

    ticket_id = 0


def _suffix(car: str) -> str:
    return car[3:7]


def _locname(zone: int, slot: int) -> str:
    return chr(ord('A') + zone) + f"{slot:03d}"


def _best_zone() -> int:
    best_zone = -1
    best_free = -1

    for z in range(gN):
        if free_cnt[z] > best_free:
            best_free = free_cnt[z]
            best_zone = z

    return best_zone


def _free_slot(zone: int, slot: int) -> None:
    free_cnt[zone] += 1
    heapq.heappush(free_slots[zone], slot)


def _push_park_suffix(car: str, tk: int) -> None:
    s = _suffix(car)
    if s not in park_suffix:
        park_suffix[s] = []
    heapq.heappush(park_suffix[s], (car, tk))


def _push_tow_suffix(car: str, tk: int) -> None:
    s = _suffix(car)
    if s not in tow_suffix:
        tow_suffix[s] = []
    heapq.heappush(tow_suffix[s], (car, tk))


def _process_tow(mTime: int) -> None:
    while tow_heap and tow_heap[0][0] <= mTime:
        tow_time, tk, car = heapq.heappop(tow_heap)

        info = parked.get(car)
        if info is None:
            continue

        cur_tk, enter_time, zone, slot = info
        if cur_tk != tk:
            continue

        # 실제 견인 처리
        del parked[car]
        _free_slot(zone, slot)

        towed[car] = (tk, tow_time)
        _push_tow_suffix(car, tk)


def enter(mTime: int, mCarNo: str) -> RESULT_E:
    global ticket_id

    _process_tow(mTime)

    # 견인 기록이 있으면 주차 성공 여부와 관계없이 삭제
    if mCarNo in towed:
        del towed[mCarNo]

    zone = _best_zone()
    if zone == -1 or free_cnt[zone] == 0:
        return RESULT_E(0, "")

    slot = heapq.heappop(free_slots[zone])
    free_cnt[zone] -= 1

    ticket_id += 1
    tk = ticket_id

    parked[mCarNo] = (tk, mTime, zone, slot)
    heapq.heappush(tow_heap, (mTime + gL, tk, mCarNo))
    _push_park_suffix(mCarNo, tk)

    return RESULT_E(1, _locname(zone, slot))


def pullout(mTime: int, mCarNo: str) -> int:
    _process_tow(mTime)

    info = parked.get(mCarNo)
    if info is not None:
        tk, enter_time, zone, slot = info
        del parked[mCarNo]
        _free_slot(zone, slot)
        return mTime - enter_time

    info = towed.get(mCarNo)
    if info is not None:
        tk, tow_time = info
        del towed[mCarNo]
        return -(gL + (mTime - tow_time) * 5)

    return -1


def _collect(heap, active_map, limit: int):
    res = []
    temp = []

    while len(res) < limit and heap:
        car, tk = heapq.heappop(heap)

        info = active_map.get(car)
        if info is None:
            continue
        if info[0] != tk:
            continue

        res.append(car)
        temp.append((car, tk))

    for item in temp:
        heapq.heappush(heap, item)

    return res


def search(mTime: int, mStr: str) -> RESULT_S:
    _process_tow(mTime)

    parked_list = []
    towed_list = []

    if mStr in park_suffix:
        parked_list = _collect(park_suffix[mStr], parked, 5)

    remain = 5 - len(parked_list)
    if remain > 0 and mStr in tow_suffix:
        towed_list = _collect(tow_suffix[mStr], towed, remain)

    ans = parked_list + towed_list

    carlist = ["", "", "", "", ""]
    for i in range(len(ans)):
        carlist[i] = ans[i]

    return RESULT_S(len(ans), carlist)
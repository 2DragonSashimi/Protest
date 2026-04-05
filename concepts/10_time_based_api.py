# ============================================
# 10. Time Based API
# ============================================

# --------------------------------------------------
# [1. 왜 필요한가]
# --------------------------------------------------
# Time Based API 문제는
# "시간(timestamp)에 따라 값이 바뀌는 데이터를 저장하고 조회하는 문제"다.
#
# 대표 예:
# - 어떤 key에 대해 시간별 값 저장
# - 특정 시점 t에서의 최신 값 조회
# - t 이하 중 가장 최근 값 찾기
# - 버전 관리 / 로그 관리 / 이력 관리
#
# 코테에서는 LeetCode의 Time Based Key-Value Store 같은 형태로 자주 나온다.
#
# 핵심은:
# "key별로 시간순 이력을 저장하고,
# 조회 시에는 이분탐색으로 가장 최근 시점을 찾는다" 이다.


# --------------------------------------------------
# [2. 언제 떠올려야 하는가]
# --------------------------------------------------
# 문제를 읽다가 아래 신호가 보이면 Time Based API를 먼저 의심한다.
#
# - timestamp가 함께 주어진다
# - 특정 시점의 값을 물어본다
# - 과거 이력을 저장해야 한다
# - "가장 최근 값"을 찾아야 한다
# - key별로 시간에 따른 상태가 달라진다
# - set / get API 형태다
#
# 대표 예시:
# - TimeMap
# - 로그 이력 조회
# - 특정 시점 직전 상태 찾기
# - 사용자 상태 변화 기록
# - 가격/점수/설정의 시계열 버전 관리


# --------------------------------------------------
# [3. 핵심 아이디어]
# --------------------------------------------------
# Time Based API의 핵심 구조는 보통 아래와 같다.
#
# 1. key별로 기록을 저장
#    - dict[key] = [(timestamp, value), ...]
#
# 2. timestamp는 보통 증가 순서로 들어온다
#    - 따라서 append만 하면 시간순 정렬 유지
#
# 3. 조회할 때는
#    - timestamp <= t 를 만족하는 가장 마지막 기록을 찾는다
#
# 4. 이때 bisect(이분탐색)를 사용한다
#
# 즉:
# dict + list + bisect 조합이 핵심이다.


from bisect import bisect_left, bisect_right
from collections import defaultdict


# --------------------------------------------------
# [4. 가장 기본적인 형태]
# --------------------------------------------------
# key별로 (timestamp, value) 목록을 저장한다.

store = defaultdict(list)

store["foo"].append((1, "bar"))
store["foo"].append((4, "bar2"))
store["foo"].append((7, "bar3"))

# 예:
# store["foo"] = [(1, "bar"), (4, "bar2"), (7, "bar3")]


# --------------------------------------------------
# [5. 왜 정렬이 중요한가]
# --------------------------------------------------
# 조회할 때
# "t 이하 중 가장 마지막 timestamp"를 찾아야 한다.
#
# 이 값은 정렬되어 있어야 bisect로 빠르게 찾을 수 있다.
#
# 보통 문제에서는 set 호출의 timestamp가 증가하는 순서로 들어오므로
# append만 해도 정렬 상태가 유지된다.
#
# 만약 timestamp가 뒤죽박죽 들어오면
# insert 정렬 또는 정렬 유지 자료구조가 더 필요해질 수 있다.


# --------------------------------------------------
# [6. 가장 기본 조회 로직]
# --------------------------------------------------
# 예:
# 기록 = [(1, "bar"), (4, "bar2"), (7, "bar3")]
# query time = 5
#
# 원하는 답:
# timestamp <= 5 인 것 중 가장 최근 -> (4, "bar2")

records = [(1, "bar"), (4, "bar2"), (7, "bar3")]

# timestamps만 따로 보면 [1, 4, 7]
# 5를 삽입할 위치는 index 2
# 그 바로 왼쪽(index 1)이 원하는 값
timestamps = [1, 4, 7]
idx = bisect_right(timestamps, 5) - 1
value_at_5 = records[idx][1] if idx >= 0 else ""


# --------------------------------------------------
# [7. bisect_right를 왜 쓰는가]
# --------------------------------------------------
# bisect_right(arr, x):
# - x를 삽입할 수 있는 가장 오른쪽 위치
#
# 따라서
# idx = bisect_right(arr, t) - 1
#
# 이 idx는
# "t 이하 중 가장 마지막 원소 위치"가 된다.
#
# Time Based API에서 가장 자주 쓰는 형태다.


# --------------------------------------------------
# [8. 최소 TimeMap 구현]
# --------------------------------------------------
class TimeMapBasic:
    def __init__(self):
        self.data = defaultdict(list)

    def set(self, key, value, timestamp):
        self.data[key].append((timestamp, value))

    def get(self, key, timestamp):
        if key not in self.data:
            return ""

        records = self.data[key]
        times = [t for t, _ in records]
        idx = bisect_right(times, timestamp) - 1

        if idx < 0:
            return ""
        return records[idx][1]


tm_basic = TimeMapBasic()
tm_basic.set("foo", "bar", 1)
tm_basic.set("foo", "bar2", 4)

tm_get_1 = tm_basic.get("foo", 1)   # "bar"
tm_get_3 = tm_basic.get("foo", 3)   # "bar"
tm_get_4 = tm_basic.get("foo", 4)   # "bar2"
tm_get_0 = tm_basic.get("foo", 0)   # ""


# --------------------------------------------------
# [9. 위 구현의 아쉬운 점]
# --------------------------------------------------
# get() 할 때마다 times = [t for t, _ in records] 를 새로 만든다.
# 이러면 get이 O(N) + O(log N)이 되어 비효율적일 수 있다.
#
# 개선 방법:
# timestamps와 values를 분리해서 저장한다.
#
# 예:
# dict[key] = {
#   "times": [...],
#   "values": [...]
# }


# --------------------------------------------------
# [10. 실전형 TimeMap 구현]
# --------------------------------------------------
class TimeMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp):
        arr = self.times.get(key, [])
        idx = bisect_right(arr, timestamp) - 1

        if idx < 0:
            return ""
        return self.values[key][idx]


tm = TimeMap()
tm.set("foo", "bar", 1)
tm.set("foo", "bar2", 4)
tm.set("foo", "bar3", 7)

tm_result_1 = tm.get("foo", 5)   # "bar2"
tm_result_2 = tm.get("foo", 7)   # "bar3"
tm_result_3 = tm.get("foo", 0)   # ""


# --------------------------------------------------
# [11. 시간복잡도]
# --------------------------------------------------
# timestamp가 증가 순서로 들어온다고 가정하면:
#
# set:
# - append만 하므로 O(1)
#
# get:
# - bisect_right -> O(log N)
#
# 따라서 매우 효율적이다.
#
# 이게 Time Based API의 가장 대표적인 풀이 패턴이다.


# --------------------------------------------------
# [12. key가 여러 개일 때]
# --------------------------------------------------
# 핵심은 "key별로 독립적인 시계열"을 관리하는 것이다.
#
# 예:
# foo -> [(1, bar), (4, bar2)]
# baz -> [(2, x), (6, y)]
#
# 즉, dict를 통해 key별 기록을 따로 저장하면 된다.

multi_store = defaultdict(list)
multi_store["foo"].append((1, "bar"))
multi_store["baz"].append((2, "x"))
multi_store["foo"].append((4, "bar2"))
multi_store["baz"].append((6, "y"))


# --------------------------------------------------
# [13. 응용 1 - 숫자 값의 시계열]
# --------------------------------------------------
# 값이 문자열이 아니라 숫자여도 구조는 동일하다.

price_log = defaultdict(list)
price_log["AAPL"].append((1, 100))
price_log["AAPL"].append((3, 120))
price_log["AAPL"].append((10, 115))


# --------------------------------------------------
# [14. 응용 2 - 상태 이력 관리]
# --------------------------------------------------
# 예:
# user_status["alice"] = [(1, "offline"), (5, "online"), (9, "away")]
#
# 특정 시점의 상태를 묻는 문제도 동일하게 처리 가능하다.

status_log = defaultdict(list)
status_log["alice"].append((1, "offline"))
status_log["alice"].append((5, "online"))
status_log["alice"].append((9, "away"))


# --------------------------------------------------
# [15. 응용 3 - 직전 값 / 직후 값]
# --------------------------------------------------
# Time Based API는 보통 "t 이하 중 가장 최근"을 찾지만,
# 가끔 "t 이상 중 가장 빠른" 값을 찾는 경우도 있다.
#
# 이때는 bisect_left를 사용할 수 있다.

times_example = [1, 4, 7]

# t 이상 중 가장 빠른 위치
idx_ge = bisect_left(times_example, 5)   # 2 -> time 7

# t 이하 중 가장 최근 위치
idx_le = bisect_right(times_example, 5) - 1   # 1 -> time 4


# --------------------------------------------------
# [16. bisect_left / bisect_right 감각]
# --------------------------------------------------
# bisect_left(arr, x):
# - x 이상이 처음 나오는 위치
#
# bisect_right(arr, x):
# - x 초과가 처음 나오는 위치
#
# 따라서:
# - t 이하 최대 위치 -> bisect_right - 1
# - t 이상 최소 위치 -> bisect_left
#
# Time Based API에서는 보통 전자가 더 중요하다.


# --------------------------------------------------
# [17. 값이 같은 timestamp에 여러 번 들어오면?]
# --------------------------------------------------
# 문제 조건을 잘 봐야 한다.
#
# 보통은 같은 key에 대해 timestamp가 strictly increasing 이거나
# non-decreasing 조건이 있다.
#
# 만약 같은 timestamp가 여러 번 가능하다면:
# - bisect_right를 쓰면 그 시점의 가장 마지막 값이 선택된다.
#
# 즉, 같은 timestamp에서 마지막으로 set된 값을 쓰고 싶다면
# bisect_right가 자연스럽다.


# --------------------------------------------------
# [18. timestamp가 정렬 보장 안 되면?]
# --------------------------------------------------
# 이 경우 단순 append로는 안 된다.
#
# 선택지:
# 1) 매번 삽입 위치를 찾아 insert
#    -> O(N)
#
# 2) set들을 모았다가 나중에 정렬
#
# 3) balanced tree 같은 더 복잡한 자료구조
#
# 하지만 대부분의 코테 문제에서는
# timestamp가 증가 순으로 들어오도록 조건을 준다.


# --------------------------------------------------
# [19. 범위 조회도 가능하다]
# --------------------------------------------------
# 예:
# key에 대해 [start, end] 구간에 들어가는 기록들을 찾고 싶다.
#
# left = bisect_left(times, start)
# right = bisect_right(times, end)
# records[left:right]
#
# 이런 식으로 범위 이력 조회도 가능하다.

def get_range(records, start, end):
    times = [t for t, _ in records]
    l = bisect_left(times, start)
    r = bisect_right(times, end)
    return records[l:r]

range_example = get_range([(1, "a"), (4, "b"), (7, "c"), (10, "d")], 3, 8)


# --------------------------------------------------
# [20. 대표 문제 유형]
# --------------------------------------------------
# Time Based API는 아래 유형으로 자주 나온다.
#
# 1) set / get TimeMap
#    - key별 timestamp 저장
#
# 2) 특정 시점 직전 상태 조회
#    - t 이하 중 가장 최근 값
#
# 3) 상태/가격/점수 이력 관리
#    - user status
#    - stock price
#    - config history
#
# 4) 로그 범위 조회
#    - 특정 시간 구간의 기록 반환
#
# 5) 버전 관리
#    - 가장 최근 유효 버전 찾기


# --------------------------------------------------
# [21. 자주 하는 실수]
# --------------------------------------------------
# 1) key가 없을 때 예외 처리 누락
#    -> "" 또는 기본값 반환
#
# 2) bisect_left / bisect_right를 혼동
#
# 3) idx = bisect_right(...) - 1 후
#    idx < 0 인 경우 처리 누락
#
# 4) get 때마다 times 리스트를 새로 만들어 비효율
#
# 5) timestamp 정렬 보장이 없는데 append만 사용
#
# 6) "가장 최근"인데 bisect_left를 잘못 써서
#    정확히 같은 timestamp 처리에 실수
#
# 7) key별 시계열을 분리하지 않고 한 배열에 다 넣어버림


# --------------------------------------------------
# [22. 문제를 보고 Time Based API를 떠올리는 체크리스트]
# --------------------------------------------------
# 아래 질문 중 하나라도 "예"면 Time Based API 후보일 가능성이 높다.
#
# - timestamp가 함께 주어지는가?
# - 특정 시점의 값을 묻는가?
# - 과거 이력을 저장해야 하는가?
# - key별로 시간이 흐르며 값이 바뀌는가?
# - t 이하 중 가장 최근 값을 찾아야 하는가?
# - dict + list + bisect 조합이 자연스러운가?


# --------------------------------------------------
# [23. 실전 템플릿 1 - TimeMap 기본]
# --------------------------------------------------
class TimeMapTemplate:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp):
        arr = self.times.get(key, [])
        idx = bisect_right(arr, timestamp) - 1
        if idx < 0:
            return ""
        return self.values[key][idx]


# --------------------------------------------------
# [24. 실전 템플릿 2 - 숫자 값 버전]
# --------------------------------------------------
class TimeNumberMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp, default=None):
        arr = self.times.get(key, [])
        idx = bisect_right(arr, timestamp) - 1
        if idx < 0:
            return default
        return self.values[key][idx]


# --------------------------------------------------
# [25. 실전 템플릿 3 - 범위 조회]
# --------------------------------------------------
class TimeRangeMap:
    def __init__(self):
        self.data = defaultdict(list)

    def set(self, key, value, timestamp):
        self.data[key].append((timestamp, value))

    def get_latest(self, key, timestamp):
        records = self.data.get(key, [])
        if not records:
            return None

        times = [t for t, _ in records]
        idx = bisect_right(times, timestamp) - 1
        if idx < 0:
            return None
        return records[idx]

    def get_range(self, key, start, end):
        records = self.data.get(key, [])
        if not records:
            return []

        times = [t for t, _ in records]
        l = bisect_left(times, start)
        r = bisect_right(times, end)
        return records[l:r]


# --------------------------------------------------
# [26. 실전 템플릿 4 - 상태 로그]
# --------------------------------------------------
class UserStatusLog:
    def __init__(self):
        self.times = defaultdict(list)
        self.status = defaultdict(list)

    def set_status(self, user, status, timestamp):
        self.times[user].append(timestamp)
        self.status[user].append(status)

    def get_status(self, user, timestamp):
        arr = self.times.get(user, [])
        idx = bisect_right(arr, timestamp) - 1
        if idx < 0:
            return "unknown"
        return self.status[user][idx]


# --------------------------------------------------
# [27. 실전 템플릿 5 - 가장 가까운 직후 값]
# --------------------------------------------------
class FutureLookupMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get_first_at_or_after(self, key, timestamp):
        arr = self.times.get(key, [])
        idx = bisect_left(arr, timestamp)
        if idx == len(arr):
            return None
        return self.values[key][idx]


# --------------------------------------------------
# [28. 예제 문제 감각]
# --------------------------------------------------
# 예제 1)
# key, value, timestamp를 저장하고
# t 시점의 값을 반환하라
# -> TimeMap
#
# 예제 2)
# 사용자의 특정 시점 상태를 반환하라
# -> user별 시계열 저장 + bisect
#
# 예제 3)
# 주가의 과거 시점 값을 조회하라
# -> stock별 timestamp/value 저장
#
# 예제 4)
# 특정 시간 구간의 로그를 반환하라
# -> bisect_left / bisect_right
#
# 예제 5)
# 가장 최근 유효 설정 값을 반환하라
# -> t 이하 최신값 찾기


# --------------------------------------------------
# [29. Time Based API와 다른 주제의 연결]
# --------------------------------------------------
# - Hash:
#   key별 저장이므로 dict가 핵심이다
#
# - Binary Search:
#   timestamp 검색에 bisect를 사용하므로 매우 밀접하다
#
# - String:
#   key가 문자열인 경우가 많다
#
# - Implementation:
#   API 설계, 예외 처리, 자료구조 구성 능력이 중요하다
#
# - Sorting:
#   timestamp 정렬 보장이 없다면 정렬 이슈가 생긴다


# --------------------------------------------------
# [30. 한 줄 요약]
# --------------------------------------------------
# Time Based API = key별 시간 이력을 저장하고,
# 특정 시점의 최신 값을 dict + list + bisect로 빠르게 조회하는 문제 유형


# --------------------------------------------------
# [31. 최소 암기 포인트]
# --------------------------------------------------
# 1) 구조:
#    dict[key] = timestamps / values
#
# 2) set:
#    append
#
# 3) get:
#    idx = bisect_right(times, t) - 1
#
# 4) idx < 0:
#    값 없음
#
# 5) timestamp 증가 순서 가정이 중요
#
# 6) 핵심 조합:
#    defaultdict + list + bisect_right


# --------------------------------------------------
# [32. 다음 주제]
# --------------------------------------------------
# 다음 파일은 11_implementation_time_attack.py 로 이어진다.
# 구현 타임어택에서는
# 시뮬레이션, 조건 분기, 좌표 처리, 디버깅 습관,
# 실전 속도 향상 전략 등을 정리한다.


# --------------------------------------------------
# [참고]
# --------------------------------------------------
# 이 파일은 개념 정리용이다.
# 필요한 부분만 복붙해서 템플릿처럼 사용하면 된다.
# Time Based API의 본질은
# "시간순 기록 + 이분탐색 조회" 라고 이해하면 된다.
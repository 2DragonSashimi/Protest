# ============================================
# 00. Python Basics for Coding Test
# ============================================

# --------------------------------------------------
# [1. 왜 필요한가]
# --------------------------------------------------
# 파이썬 코딩테스트에서는 언어 문법 자체가 곧 풀이 도구인 경우가 많다.
# 예:
# - Hash      -> dict, set
# - BFS       -> deque
# - PriorityQ -> heapq
# - Binary Search -> bisect
#
# 즉, 알고리즘 개념을 배우기 전에
# "파이썬에서 자주 쓰는 자료구조와 문법"을 먼저 손에 익혀야 한다.


# --------------------------------------------------
# [2. 언제 필요한가]
# --------------------------------------------------
# 사실상 모든 문제에서 필요하다.
#
# - 입력 처리
# - 리스트 / 딕셔너리 / 셋 사용
# - 정렬
# - 큐 / 스택 / 힙
# - 문자열 파싱
# - 이분탐색
# - 구현 문제
#
# 이 파일은 이후 모든 주제의 공통 기반이다.


# --------------------------------------------------
# [3. 핵심 아이디어]
# --------------------------------------------------
# 코테 파이썬의 핵심은 아래 8개다.
#
# 1. 빠른 입력
# 2. 리스트 / 딕셔너리 / 셋 운용
# 3. 정렬
# 4. 스택 / 큐
# 5. 힙
# 6. 문자열 처리
# 7. 이분탐색
# 8. 자주 쓰는 내장함수와 표준 라이브러리


# --------------------------------------------------
# [4. 빠른 입력]
# --------------------------------------------------
# 기본 입력
#
# n = int(input())
# arr = list(map(int, input().split()))
# s = input().strip()
#
# 입력이 많으면 아래처럼 사용한다.

import sys
input = sys.stdin.readline

# 예시
# n = int(input())
# arr = list(map(int, input().split()))
# graph = [list(map(int, input().split())) for _ in range(n)]


# --------------------------------------------------
# [5. 리스트]
# --------------------------------------------------
# 생성
arr = [1, 2, 3]
zeros = [0] * 5

n, m = 3, 4
matrix = [[0] * m for _ in range(n)]   # 올바른 2차원 리스트 생성

# 주의:
# 아래 방식은 같은 내부 리스트를 참조해서 문제가 생길 수 있다.
bad_matrix = [[0] * m] * n

# 자주 쓰는 연산
temp = [3, 1, 2]
temp.append(5)          # [3, 1, 2, 5]
temp.pop()              # 맨 뒤 제거
temp.sort()             # 오름차순 정렬
temp.sort(reverse=True) # 내림차순 정렬
temp.reverse()          # 순서 뒤집기

# 슬라이싱
sample = [10, 20, 30, 40, 50]
a = sample[:]     # 전체 복사
b = sample[1:4]   # [20, 30, 40]
c = sample[::-1]  # 역순

# 자주 쓰는 값
length = len(sample)
total = sum(sample)
mx = max(sample)
mn = min(sample)


# --------------------------------------------------
# [6. 튜플]
# --------------------------------------------------
# 튜플은 변경 불가능한 자료형이다.
# 좌표, 정렬, heap, 상태 저장 등에 자주 쓴다.

point = (3, 5)
x, y = point

# 예:
# arr = [(2, 3), (1, 5), (2, 1)]
# arr.sort()  # 첫 번째 원소부터 비교


# --------------------------------------------------
# [7. 딕셔너리(dict)]
# --------------------------------------------------
# Hash의 핵심 자료구조.
# key -> value 형태로 저장한다.

d = {}
d["apple"] = 3
apple_count = d["apple"]

# 존재 확인
exists = "apple" in d

# 반복
for key in d:
    value = d[key]
    pass

for key, value in d.items():
    pass

# 자주 쓰는 패턴: 빈도수 세기
freq = {}
nums = [1, 3, 2, 1, 3, 1, 5]
for num in nums:
    if num not in freq:
        freq[num] = 0
    freq[num] += 1

# 안전한 조회
# key가 없을 수도 있으므로 get을 쓸 수 있다.
banana_count = d.get("banana", 0)


# --------------------------------------------------
# [8. set]
# --------------------------------------------------
# 중복 제거와 존재 확인에 매우 강하다.

s = set()
s.add(3)
s.add(5)

# remove: 없으면 에러 가능
# s.remove(10)

# discard: 없어도 에러 없음
s.discard(10)

has_five = 5 in s

# 중복 제거
arr = [1, 2, 2, 3, 3, 3]
unique = list(set(arr))

# 주의: set은 순서를 보장하지 않는다.


# --------------------------------------------------
# [9. collections 모듈]
# --------------------------------------------------
from collections import deque, defaultdict, Counter


# 9-1. deque
# BFS, 양끝 삽입/삭제에 사용한다.
q = deque()
q.append(1)
q.append(2)
q.appendleft(0)
right = q.pop()
left = q.popleft()

# 리스트에서 pop(0)은 느리므로 BFS에서는 deque를 쓴다.


# 9-2. defaultdict
# 기본값이 자동으로 들어가는 dict이다.

freq_dd = defaultdict(int)
for num in nums:
    freq_dd[num] += 1

graph = defaultdict(list)
graph[1].append(2)
graph[1].append(3)


# 9-3. Counter
# 빈도수 세기에 특화.
cnt = Counter(nums)
count_of_1 = cnt[1]
top2 = cnt.most_common(2)


# --------------------------------------------------
# [10. heapq]
# --------------------------------------------------
# 파이썬의 우선순위 큐는 기본적으로 최소 힙이다.

import heapq

hq = []
heapq.heappush(hq, 3)
heapq.heappush(hq, 1)
heapq.heappush(hq, 5)
smallest = heapq.heappop(hq)   # 1

# 최대 힙처럼 쓰기: 음수 부호를 붙인다.
max_hq = []
heapq.heappush(max_hq, -3)
heapq.heappush(max_hq, -1)
heapq.heappush(max_hq, -5)
largest = -heapq.heappop(max_hq)  # 5

# 튜플 힙
pair_hq = []
heapq.heappush(pair_hq, (2, "b"))
heapq.heappush(pair_hq, (1, "a"))
heapq.heappush(pair_hq, (3, "c"))
# 앞 원소부터 우선 비교한다.


# --------------------------------------------------
# [11. 정렬]
# --------------------------------------------------
arr = [3, 1, 4, 2]
arr.sort()                  # 오름차순
arr.sort(reverse=True)      # 내림차순

sorted_arr = sorted(arr)    # 원본 유지, 정렬된 새 리스트 반환

# key 사용
pairs = [(2, 3), (1, 5), (2, 1)]
pairs.sort(key=lambda x: (x[0], x[1]))

# 두 번째 값 기준 정렬
pairs.sort(key=lambda x: x[1])

# 문자열 길이 기준 정렬
words = ["banana", "kiwi", "apple", "a"]
words.sort(key=len)


# --------------------------------------------------
# [12. bisect]
# --------------------------------------------------
# 직접 이분탐색을 구현하지 않고 사용할 수 있다.

from bisect import bisect_left, bisect_right

sorted_nums = [1, 2, 2, 2, 4, 5]

left_idx = bisect_left(sorted_nums, 2)    # 1
right_idx = bisect_right(sorted_nums, 2)  # 4

# 값의 개수 구하기
count_2 = right_idx - left_idx


# --------------------------------------------------
# [13. 문자열 처리 기본]
# --------------------------------------------------
text = "hello world"

# 자주 쓰는 함수
split_default = text.split()
split_comma = "a,b,c".split(",")
joined = "-".join(["a", "b", "c"])
stripped = "  abc  ".strip()
lowered = "ABC".lower()
uppered = "abc".upper()
replaced = "hello".replace("l", "x")

# 부분 문자열
first_char = text[0]
last_char = text[-1]
sub = text[1:4]
reversed_text = text[::-1]

# 숫자 / 문자 판별
char = "A"
is_digit = char.isdigit()
is_alpha = char.isalpha()
is_alnum = char.isalnum()


# --------------------------------------------------
# [14. enumerate / zip]
# --------------------------------------------------
arr = [10, 20, 30]

# enumerate: 인덱스와 값을 같이 사용
for i, value in enumerate(arr):
    pass

# zip: 여러 리스트를 묶어서 순회
a = [1, 2, 3]
b = ["a", "b", "c"]
for x, y in zip(a, b):
    pass


# --------------------------------------------------
# [15. 자주 쓰는 내장 함수]
# --------------------------------------------------
abs_val = abs(-3)
min_val = min(1, 2, 3)
max_val = max(1, 2, 3)
sum_val = sum([1, 2, 3])
len_val = len([1, 2, 3])

# 진법 변환
bin_val = bin(10)   # '0b1010'
oct_val = oct(10)   # '0o12'
hex_val = hex(10)   # '0xa'


# --------------------------------------------------
# [16. 리스트 컴프리헨션]
# --------------------------------------------------
squares = [x * x for x in range(10)]
evens = [x for x in range(10) if x % 2 == 0]

# 짧고 편리하지만 너무 복잡하게 쓰지는 말자.


# --------------------------------------------------
# [17. 함수]
# --------------------------------------------------
def add(a, b):
    return a + b

# 코테에서는 작은 함수로 분리하면 디버깅에 도움이 된다.


# --------------------------------------------------
# [18. 재귀 주의]
# --------------------------------------------------
# 파이썬은 재귀 깊이 제한이 있다.
# DFS를 재귀로 짤 때는 주의해야 한다.

sys.setrecursionlimit(10**6)

# 그래도 너무 깊은 재귀는 스택 문제를 일으킬 수 있으므로,
# 상황에 따라 반복문 DFS도 고려한다.


# --------------------------------------------------
# [19. 시간복잡도 감각]
# --------------------------------------------------
# 대략적인 기준:
#
# - 리스트 인덱스 접근      : O(1)
# - dict / set 조회         : 평균 O(1)
# - 정렬                    : O(N log N)
# - 리스트 맨 뒤 append/pop : O(1)
# - 리스트 맨 앞 삽입/삭제   : O(N)
# - deque 양끝 삽입/삭제     : O(1)
# - heap push/pop           : O(log N)
# - bisect                  : O(log N)


# --------------------------------------------------
# [20. 코테에서 자주 하는 실수]
# --------------------------------------------------
# 1) 입력 느리게 받기
#    입력이 많을 때 input()만 쓰면 느릴 수 있다.
#
# 2) 2차원 배열 잘못 생성하기
#    arr = [[0] * m] * n
#    이 방식은 참조가 공유된다.
#
# 3) BFS에서 list.pop(0) 사용
#    느리다. deque.popleft()를 써야 한다.
#
# 4) set / dict는 정렬되지 않음
#    순서가 필요하면 sorted()를 써야 한다.
#
# 5) 재귀 깊이 초과
#    DFS를 재귀로 짤 때 주의해야 한다.
#
# 6) 문자열 누적을 반복문에서 많이 하기
#    문자열은 immutable이라 누적 비용이 커질 수 있다.
#    경우에 따라 리스트에 모아 ''.join()을 사용한다.


# --------------------------------------------------
# [21. 실전 체크리스트]
# --------------------------------------------------
# 문제를 풀기 전에 확인할 것:
#
# - 입력 크기가 큰가?
# - 빠른 조회가 필요한가? -> dict / set
# - BFS인가? -> deque
# - 우선순위가 필요한가? -> heapq
# - 정렬 후 탐색인가? -> sort / bisect
# - 문자열 파싱이 필요한가? -> split / join / slicing


# --------------------------------------------------
# [22. 한 줄 요약]
# --------------------------------------------------
# - 빠른 조회: dict, set
# - BFS: deque
# - 우선순위 큐: heapq
# - 이분탐색: bisect
# - 빈도수: defaultdict, Counter
# - 정렬: sort, sorted


# --------------------------------------------------
# [23. 최소 템플릿 모음]
# --------------------------------------------------

# 빠른 입력
# import sys
# input = sys.stdin.readline

# BFS용 큐
# from collections import deque
# q = deque()

# 빈도수 세기
# from collections import defaultdict
# freq = defaultdict(int)

# 최소 힙
# import heapq
# hq = []

# 이분탐색
# from bisect import bisect_left, bisect_right


# --------------------------------------------------
# [24. 다음 주제]
# --------------------------------------------------
# 다음 파일은 01_hash.py 로 이어진다.
# Hash에서는 dict, set, defaultdict, Counter를 중심으로
# 빈도수 / 존재 확인 / 매핑 / 대표 문제 패턴을 정리한다.


# --------------------------------------------------
# [참고]
# --------------------------------------------------
# 이 파일은 "개념 정리용"이다.
# 실행해도 큰 의미는 없고, 필요한 부분만 복붙해서 사용하면 된다.
# 예제 코드를 직접 수정해보면서 손에 익히는 것이 중요하다.

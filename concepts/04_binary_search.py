# ============================================
# 04. Binary Search
# ============================================

# --------------------------------------------------
# [1. 왜 필요한가]
# --------------------------------------------------
# Binary Search(이분탐색)는
# "정답 후보를 절반씩 줄여가며 빠르게 찾는 방법"이다.
#
# 단순 선형 탐색은 O(N)이지만,
# 이분탐색은 보통 O(log N)에 해결할 수 있다.
#
# 예:
# - 정렬된 배열에서 특정 값 찾기
# - 어떤 값이 처음/마지막으로 등장하는 위치 찾기
# - 조건을 만족하는 최소값/최대값 찾기
# - 가능한 답의 범위를 탐색하는 매개변수 탐색
#
# 코테에서는 단순 배열 탐색보다
# "정답을 탐색하는 사고방식"으로 훨씬 자주 쓰인다.


# --------------------------------------------------
# [2. 언제 떠올려야 하는가]
# --------------------------------------------------
# 문제를 읽다가 아래 신호가 보이면 Binary Search를 먼저 의심한다.
#
# - 정렬된 배열에서 값을 찾아야 한다
# - 어떤 조건을 만족하는 최소/최대 지점을 찾아야 한다
# - "가능/불가능" 판정이 된다
# - 답의 범위가 숫자로 주어지고, 그 범위가 크다
# - 완전탐색은 너무 느리다
# - mid를 기준으로 왼쪽/오른쪽 중 하나를 버릴 수 있다
#
# 대표 예시:
# - 특정 수 찾기
# - lower bound / upper bound 느낌 문제
# - 입국심사
# - 랜선 자르기
# - 공유기 설치
# - 예산 / 용량 / 시간 최소화 문제


# --------------------------------------------------
# [3. 핵심 아이디어]
# --------------------------------------------------
# Binary Search는 크게 2종류로 보면 된다.
#
# 1. 정렬된 배열에서 값 찾기
#    - target이 어디 있는가?
#    - 처음/마지막 위치는 어디인가?
#
# 2. 정답 자체를 탐색하기
#    - 어떤 값 X가 가능하면, 그보다 작은/큰 값도 가능/불가능한가?
#    - 즉, 조건이 단조성(monotonicity)을 가지는가?
#
# 코테에서는 2번이 특히 중요하다.
# 흔히 "매개변수 탐색"이라고 부른다.


from bisect import bisect_left, bisect_right


# --------------------------------------------------
# [4. 기본 이분탐색 - 정렬된 배열에서 값 찾기]
# --------------------------------------------------
def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


example_arr = [1, 3, 5, 7, 9]
example_idx = binary_search(example_arr, 7)   # 3
not_found_idx = binary_search(example_arr, 4) # -1


# --------------------------------------------------
# [5. 왜 빠른가]
# --------------------------------------------------
# 매 단계마다 탐색 구간을 절반으로 줄인다.
#
# N개를 선형 탐색하면 O(N)
# N개를 이분탐색하면 O(log N)
#
# 예:
# N = 1,000,000 이어도
# log2(1,000,000)은 대략 20 정도라 매우 빠르다.


# --------------------------------------------------
# [6. bisect]
# --------------------------------------------------
# Python에서는 bisect 모듈로 이분탐색을 편하게 할 수 있다.

arr = [1, 2, 2, 2, 4, 5]

left_idx = bisect_left(arr, 2)    # 1
right_idx = bisect_right(arr, 2)  # 4

# 의미:
# - bisect_left(arr, x):
#   x를 삽입할 수 있는 가장 왼쪽 위치
#
# - bisect_right(arr, x):
#   x를 삽입할 수 있는 가장 오른쪽 위치

count_of_2 = right_idx - left_idx   # 3


# --------------------------------------------------
# [7. lower bound / upper bound 감각]
# --------------------------------------------------
# 자주 이렇게 생각하면 된다.
#
# lower bound:
# - "x 이상이 처음 나오는 위치"
#
# upper bound:
# - "x 초과가 처음 나오는 위치"
#
# 따라서
# 특정 값 x의 개수는
# upper bound - lower bound 로 구할 수 있다.


# --------------------------------------------------
# [8. 정렬이 전제 조건]
# --------------------------------------------------
# 매우 중요:
# 배열 탐색용 이분탐색은 "정렬된 배열"이어야 한다.

sorted_arr = [1, 3, 5, 7, 9]
# 이 경우만 binary search / bisect 사용 가능

unsorted_arr = [5, 1, 9, 3, 7]
# 이 상태에서 이분탐색 사용하면 안 된다.


# --------------------------------------------------
# [9. 가장 자주 쓰는 패턴 1 - 존재 여부 확인]
# --------------------------------------------------
def exists(arr, target):
    idx = bisect_left(arr, target)
    return idx < len(arr) and arr[idx] == target


exists_result1 = exists([1, 2, 3, 4, 5], 3)  # True
exists_result2 = exists([1, 2, 3, 4, 5], 6)  # False


# --------------------------------------------------
# [10. 가장 자주 쓰는 패턴 2 - 개수 구하기]
# --------------------------------------------------
def count_target(arr, target):
    return bisect_right(arr, target) - bisect_left(arr, target)


count_result = count_target([1, 2, 2, 2, 4, 5], 2)  # 3


# --------------------------------------------------
# [11. 가장 자주 쓰는 패턴 3 - 첫 위치 / 마지막 위치]
# --------------------------------------------------
def first_position(arr, target):
    idx = bisect_left(arr, target)
    if idx < len(arr) and arr[idx] == target:
        return idx
    return -1


def last_position(arr, target):
    idx = bisect_right(arr, target) - 1
    if 0 <= idx < len(arr) and arr[idx] == target:
        return idx
    return -1


first_pos = first_position([1, 2, 2, 2, 4, 5], 2)  # 1
last_pos = last_position([1, 2, 2, 2, 4, 5], 2)    # 3


# --------------------------------------------------
# [12. 배열 탐색과 매개변수 탐색의 차이]
# --------------------------------------------------
# 배열 탐색:
# - 정렬된 배열에서 target을 찾는다
#
# 매개변수 탐색:
# - "정답이 될 수 있는 값의 범위"를 탐색한다
#
# 예:
# "시간 t 안에 모든 사람 심사가 가능한가?"
# -> t가 가능하면 더 큰 시간도 가능
# -> 단조성 존재
# -> 이분탐색 가능
#
# 즉, 배열이 없어도 "답의 범위"만 있으면 이분탐색이 가능하다.


# --------------------------------------------------
# [13. 매개변수 탐색의 핵심]
# --------------------------------------------------
# 어떤 값 mid에 대해 check(mid)를 정의할 수 있어야 한다.
#
# 예:
# - mid 길이로 랜선을 잘랐을 때 필요한 개수가 나오는가?
# - mid 시간 안에 모든 작업이 끝나는가?
# - mid 거리 이상으로 공유기를 설치할 수 있는가?
#
# 그리고 check(mid)의 결과가
# False False False True True True
# 또는
# True True True False False False
# 같은 "단조성"을 가져야 한다.


# --------------------------------------------------
# [14. 매개변수 탐색 템플릿 - 최소값 찾기]
# --------------------------------------------------
# 조건을 만족하는 가장 작은 값을 찾는 템플릿

def lower_bound_answer(left, right, check):
    ans = right
    while left <= right:
        mid = (left + right) // 2

        if check(mid):
            ans = mid
            right = mid - 1
        else:
            left = mid + 1

    return ans


# 예시 check 함수
def example_check_min(x):
    return x >= 7


example_min_answer = lower_bound_answer(1, 20, example_check_min)  # 7


# --------------------------------------------------
# [15. 매개변수 탐색 템플릿 - 최대값 찾기]
# --------------------------------------------------
# 조건을 만족하는 가장 큰 값을 찾는 템플릿

def upper_bound_answer(left, right, check):
    ans = left - 1
    while left <= right:
        mid = (left + right) // 2

        if check(mid):
            ans = mid
            left = mid + 1
        else:
            right = mid - 1

    return ans


# 예시 check 함수
def example_check_max(x):
    return x <= 7


example_max_answer = upper_bound_answer(1, 20, example_check_max)  # 7


# --------------------------------------------------
# [16. 매개변수 탐색 예시 1 - 랜선 자르기 느낌]
# --------------------------------------------------
# 길이 mid로 잘랐을 때 K개 이상 만들 수 있는가?
# -> 가능하면 더 크게도 시도해볼 수 있으므로 "최대값 찾기"

def max_cut_length(cables, need):
    def check(length):
        if length == 0:
            return True
        count = 0
        for cable in cables:
            count += cable // length
        return count >= need

    left, right = 1, max(cables)
    ans = 0

    while left <= right:
        mid = (left + right) // 2
        if check(mid):
            ans = mid
            left = mid + 1
        else:
            right = mid - 1

    return ans


cut_result = max_cut_length([802, 743, 457, 539], 11)


# --------------------------------------------------
# [17. 매개변수 탐색 예시 2 - 입국심사 느낌]
# --------------------------------------------------
# 시간 mid 안에 모든 사람 처리가 가능한가?
# -> 가능하면 더 작은 시간도 시도해야 하므로 "최소값 찾기"

def min_process_time(times, n):
    def check(time_limit):
        total = 0
        for t in times:
            total += time_limit // t
        return total >= n

    left, right = 1, max(times) * n
    ans = right

    while left <= right:
        mid = (left + right) // 2
        if check(mid):
            ans = mid
            right = mid - 1
        else:
            left = mid + 1

    return ans


process_result = min_process_time([7, 10], 6)


# --------------------------------------------------
# [18. 시간복잡도]
# --------------------------------------------------
# 기본 이분탐색:
# - O(log N)
#
# 매개변수 탐색:
# - O(log 답의범위 * check 비용)
#
# 예를 들어,
# check가 O(N)이고
# 답의 범위가 1 ~ 10^9 이면
# 전체는 대략 O(N log 10^9) 정도로 본다.


# --------------------------------------------------
# [19. 대표 문제 유형]
# --------------------------------------------------
# Binary Search는 아래 유형으로 자주 나온다.
#
# 1) 정렬 배열에서 값 찾기
#    - 존재 여부
#    - 위치 찾기
#
# 2) 개수 구하기
#    - 특정 값이 몇 개 있는가?
#
# 3) 첫/마지막 위치
#    - lower / upper bound
#
# 4) 매개변수 탐색
#    - 최소 시간
#    - 최대 길이
#    - 최소 용량
#    - 최대 거리
#
# 5) 답의 범위가 매우 큰 문제
#    - 10^9, 10^12 같은 범위
#    - 완전탐색 불가능


# --------------------------------------------------
# [20. 자주 하는 실수]
# --------------------------------------------------
# 1) 정렬되지 않은 배열에 이분탐색 사용
#
# 2) left, right 갱신을 반대로 함
#
# 3) while 조건을 헷갈림
#    보통 while left <= right 를 많이 쓴다.
#
# 4) mid 계산 후 무한루프
#    left/right가 줄어들지 않으면 무한루프 가능
#
# 5) 정답을 저장하지 않고 지나감
#    특히 매개변수 탐색에서 ans 갱신을 빼먹기 쉽다.
#
# 6) 최소값 찾기 / 최대값 찾기 방향을 반대로 잡음
#
# 7) bisect_left / bisect_right 의미를 헷갈림
#
# 8) 답의 범위 설정을 잘못 잡음
#    예: right를 너무 작게 잡아 정답이 범위 밖으로 나감


# --------------------------------------------------
# [21. 문제를 보고 Binary Search를 떠올리는 체크리스트]
# --------------------------------------------------
# 아래 질문 중 하나라도 "예"면 Binary Search 후보일 가능성이 높다.
#
# - 정렬된 배열인가?
# - 값의 존재 여부 / 위치를 빨리 찾아야 하는가?
# - 답의 범위가 크고, check(mid)가 가능한가?
# - 조건을 만족하는 최소/최대값을 찾아야 하는가?
# - check 결과가 단조성을 가지는가?
# - 완전탐색이 너무 느린가?


# --------------------------------------------------
# [22. 실전 템플릿 1 - 배열에서 값 찾기]
# --------------------------------------------------
def binary_search_basic(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


bs_basic_result = binary_search_basic([1, 3, 5, 7, 9], 5)


# --------------------------------------------------
# [23. 실전 템플릿 2 - 존재 여부]
# --------------------------------------------------
def exists_with_bisect(arr, target):
    idx = bisect_left(arr, target)
    return idx < len(arr) and arr[idx] == target


exists_bisect_result = exists_with_bisect([1, 2, 4, 4, 4, 7], 4)


# --------------------------------------------------
# [24. 실전 템플릿 3 - 개수 구하기]
# --------------------------------------------------
def count_with_bisect(arr, target):
    return bisect_right(arr, target) - bisect_left(arr, target)


count_bisect_result = count_with_bisect([1, 2, 4, 4, 4, 7], 4)


# --------------------------------------------------
# [25. 실전 템플릿 4 - 최소값 찾는 매개변수 탐색]
# --------------------------------------------------
def find_minimum_valid(left, right, check):
    ans = right
    while left <= right:
        mid = (left + right) // 2

        if check(mid):
            ans = mid
            right = mid - 1
        else:
            left = mid + 1

    return ans


# 예시
def check_min_example(x):
    return x >= 13


min_valid_result = find_minimum_valid(1, 100, check_min_example)


# --------------------------------------------------
# [26. 실전 템플릿 5 - 최대값 찾는 매개변수 탐색]
# --------------------------------------------------
def find_maximum_valid(left, right, check):
    ans = left - 1
    while left <= right:
        mid = (left + right) // 2

        if check(mid):
            ans = mid
            left = mid + 1
        else:
            right = mid - 1

    return ans


# 예시
def check_max_example(x):
    return x <= 13


max_valid_result = find_maximum_valid(1, 100, check_max_example)


# --------------------------------------------------
# [27. 예제 문제 감각]
# --------------------------------------------------
# 예제 1)
# 정렬된 배열에서 7이 존재하는가?
# -> 기본 이분탐색 / bisect
#
# 예제 2)
# 배열에서 4가 몇 번 등장하는가?
# -> bisect_right - bisect_left
#
# 예제 3)
# 조건을 만족하는 가장 작은 시간은?
# -> 매개변수 탐색 (최소값)
#
# 예제 4)
# 길이를 최대 얼마까지 자를 수 있는가?
# -> 매개변수 탐색 (최대값)
#
# 예제 5)
# 공유기 사이 최소 거리를 최대화하라
# -> 거리 기준 check(mid) + 매개변수 탐색


# --------------------------------------------------
# [28. Binary Search와 다른 주제의 연결]
# --------------------------------------------------
# - Hash:
#   직접 연결은 덜하지만 전처리 후 존재 확인/검증과 섞일 수 있다
#
# - String:
#   정렬된 문자열 배열 탐색 가능
#
# - Time Based API:
#   시간 배열에서 특정 시점 직전/직후 값을 찾을 때 매우 중요
#
# - 구현:
#   check 함수 구현이 핵심인 경우가 많다
#
# - 최적화 문제:
#   완전탐색 대신 답을 이분탐색하는 경우가 많다


# --------------------------------------------------
# [29. 한 줄 요약]
# --------------------------------------------------
# Binary Search = 정렬된 배열 또는 답의 범위에서
# 절반씩 줄여가며 위치나 정답을 찾는 방법


# --------------------------------------------------
# [30. 최소 암기 포인트]
# --------------------------------------------------
# 1) 정렬 배열 탐색:
#    while left <= right:
#        mid = (left + right) // 2
#
# 2) 존재 여부:
#    idx = bisect_left(arr, x)
#
# 3) 개수:
#    bisect_right(arr, x) - bisect_left(arr, x)
#
# 4) 최소값 찾기:
#    check(mid) True -> right = mid - 1
#
# 5) 최대값 찾기:
#    check(mid) True -> left = mid + 1
#
# 6) 핵심:
#    단조성이 있어야 매개변수 탐색 가능


# --------------------------------------------------
# [31. 다음 주제]
# --------------------------------------------------
# 다음 파일은 05_bfs_dfs.py 로 이어진다.
# BFS / DFS에서는
# 그래프 탐색, 격자 탐색, 방문 처리, 연결 요소,
# 최단거리(BFS) 등을 중심으로 정리한다.


# --------------------------------------------------
# [참고]
# --------------------------------------------------
# 이 파일은 개념 정리용이다.
# 필요한 부분만 복붙해서 템플릿처럼 사용하면 된다.
# Binary Search는 "정렬 배열 탐색"보다도
# "답을 탐색하는 사고방식"이 핵심이다.

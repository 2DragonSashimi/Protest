# ============================================
# 09. Square Root Decomposition / Bucket
# ============================================

# --------------------------------------------------
# [1. 왜 필요한가]
# --------------------------------------------------
# Square Root Decomposition(제곱근 분할) / Bucket은
# 배열이나 값 범위를 "적당한 크기의 블록"으로 나누어
# 쿼리를 더 빠르게 처리하는 아이디어다.
#
# 세그먼트 트리처럼 강력한 자료구조를 쓰기 전에
# 더 단순한 구조로 충분히 해결 가능한 문제에서 자주 유용하다.
#
# 예:
# - 구간합 / 구간쿼리
# - 구간 빈도 계산
# - 값 범위를 블록으로 나눠 빠르게 탐색
# - top/first candidate를 블록 단위로 찾기
# - 오프라인/시뮬레이션 최적화
#
# 핵심은:
# "전체를 한 칸씩 보지 말고, 블록 단위로 묶어서 처리하자" 이다.


# --------------------------------------------------
# [2. 언제 떠올려야 하는가]
# --------------------------------------------------
# 문제를 읽다가 아래 신호가 보이면 sqrt decomposition / bucket을 의심한다.
#
# - 배열 길이가 커서 매번 O(N) 순회는 느리다
# - 구간 [l, r] 쿼리가 많이 들어온다
# - 업데이트와 쿼리가 섞여 있다
# - 값 범위가 비교적 작거나 관리 가능한 수준이다
# - "블록 단위로 처리하면 빨라질 것 같다"는 감각이 든다
# - 세그먼트 트리까지는 필요 없어 보이는데 O(NQ)는 너무 느리다
#
# 대표 예시:
# - 구간합
# - 구간 내 조건 만족 원소 수
# - 어떤 값 이상의 첫 위치 찾기
# - 버킷으로 빈도 관리
# - 점프 게임/다음 위치 갱신 류 문제


# --------------------------------------------------
# [3. 핵심 아이디어]
# --------------------------------------------------
# 길이 N의 배열을 대략 sqrt(N) 크기의 블록으로 나눈다.
#
# 예:
# N = 16
# block size = 4
#
# [0 1 2 3] [4 5 6 7] [8 9 10 11] [12 13 14 15]
#
# 각 블록마다 요약 정보를 저장한다.
#
# 예:
# - 블록 합
# - 블록 최솟값 / 최댓값
# - 블록 내 빈도
# - 블록 내 정렬된 리스트
#
# 그러면 쿼리할 때
# - 양 끝의 애매한 부분만 직접 순회
# - 중간의 꽉 찬 블록은 요약 정보 사용
#
# 이런 방식으로 속도를 줄인다.


import math
from bisect import bisect_left, bisect_right, insort


# --------------------------------------------------
# [4. 블록 크기]
# --------------------------------------------------
# 보통 block_size = int(sqrt(N)) 정도로 잡는다.
#
# 직관:
# - 블록 개수는 약 sqrt(N)
# - 각 블록 길이도 약 sqrt(N)
#
# 그래서 한 쿼리에서
# 양 끝 자투리 O(sqrt(N))
# 중간 블록 O(sqrt(N))
# 정도가 되어 전체 O(sqrt(N)) 감각이 나온다.

arr = [5, 1, 7, 3, 2, 6, 4, 8, 9, 0]
n = len(arr)
block_size = int(math.sqrt(n)) + 1


# --------------------------------------------------
# [5. 가장 기본형 - 구간합]
# --------------------------------------------------
# 각 블록의 합을 저장해두면
# 구간합을 더 빠르게 계산할 수 있다.

class SqrtSum:
    def __init__(self, arr):
        self.arr = arr[:]
        self.n = len(arr)
        self.block_size = int(math.sqrt(self.n)) + 1
        self.block_count = (self.n + self.block_size - 1) // self.block_size
        self.block_sum = [0] * self.block_count

        for i, value in enumerate(arr):
            self.block_sum[i // self.block_size] += value

    def update(self, idx, value):
        block = idx // self.block_size
        self.block_sum[block] += value - self.arr[idx]
        self.arr[idx] = value

    def query(self, left, right):
        result = 0

        while left <= right and left % self.block_size != 0:
            result += self.arr[left]
            left += 1

        while left + self.block_size - 1 <= right:
            result += self.block_sum[left // self.block_size]
            left += self.block_size

        while left <= right:
            result += self.arr[left]
            left += 1

        return result


sqrt_sum_example = SqrtSum([5, 1, 7, 3, 2, 6, 4, 8, 9, 0])
sum_query_1 = sqrt_sum_example.query(2, 7)   # arr[2:8] 합
sqrt_sum_example.update(3, 10)
sum_query_2 = sqrt_sum_example.query(2, 7)


# --------------------------------------------------
# [6. 구간합 쿼리의 감각]
# --------------------------------------------------
# query(left, right)에서
#
# 1) left가 블록 시작점에 맞을 때까지 직접 더함
# 2) 중간의 꽉 찬 블록은 block_sum 사용
# 3) 마지막 자투리 직접 더함
#
# 이게 제곱근 분할의 가장 기본적인 형태다.


# --------------------------------------------------
# [7. 시간복잡도 - 기본 구간합]
# --------------------------------------------------
# 전처리:
# - O(N)
#
# 점 업데이트:
# - O(1)
#
# 구간합 쿼리:
# - O(sqrt(N)) 정도
#
# 세그먼트 트리보다 느릴 수 있지만,
# 구현이 훨씬 단순하다.


# --------------------------------------------------
# [8. 버킷(Bucket) 아이디어]
# --------------------------------------------------
# bucket은 꼭 "배열 인덱스 블록"만 뜻하는 건 아니다.
# "값의 범위"를 나누는 방식도 자주 bucket이라고 부른다.
#
# 예:
# 값 범위가 0 ~ 100000 이라면
# 이를 블록 단위로 나눠서 빈도를 관리할 수 있다.
#
# 그러면:
# - 특정 값 존재 여부
# - 특정 값 이상 첫 원소
# - k번째 값 찾기
#
# 같은 문제를 빠르게 처리할 수 있다.


# --------------------------------------------------
# [9. 값 범위 버킷 - 빈도 관리 예시]
# --------------------------------------------------
class FrequencyBucket:
    def __init__(self, max_value):
        self.max_value = max_value
        self.block_size = int(math.sqrt(max_value + 1)) + 1
        self.block_count = (max_value + self.block_size) // self.block_size
        self.freq = [0] * (max_value + 1)
        self.bucket = [0] * self.block_count

    def add(self, x):
        self.freq[x] += 1
        self.bucket[x // self.block_size] += 1

    def remove(self, x):
        if self.freq[x] > 0:
            self.freq[x] -= 1
            self.bucket[x // self.block_size] -= 1

    def count(self, x):
        return self.freq[x]

    def exists(self, x):
        return self.freq[x] > 0

    def first_existing_at_least(self, x):
        block = x // self.block_size

        # 시작 블록의 자투리
        start = x
        end = min(self.max_value, (block + 1) * self.block_size - 1)
        for value in range(start, end + 1):
            if self.freq[value] > 0:
                return value

        # 이후 블록은 bucket count로 건너뜀
        for b in range(block + 1, self.block_count):
            if self.bucket[b] == 0:
                continue
            start = b * self.block_size
            end = min(self.max_value, (b + 1) * self.block_size - 1)
            for value in range(start, end + 1):
                if self.freq[value] > 0:
                    return value

        return -1


freq_bucket = FrequencyBucket(100)
freq_bucket.add(7)
freq_bucket.add(20)
freq_bucket.add(21)
freq_bucket.add(50)

exists_20 = freq_bucket.exists(20)                  # True
first_ge_19 = freq_bucket.first_existing_at_least(19)  # 20


# --------------------------------------------------
# [10. 왜 버킷이 유용한가]
# --------------------------------------------------
# 값 범위를 전부 하나씩 보면 O(MAX_VALUE)지만,
# 버킷 단위로 비어 있는 구간을 한 번에 건너뛸 수 있다.
#
# 즉,
# - 비어 있는 블록은 통째로 skip
# - 값이 있는 블록만 자세히 확인
#
# 이런 식으로 효율을 높인다.


# --------------------------------------------------
# [11. 정렬된 블록]
# --------------------------------------------------
# 어떤 문제는 "구간 [l, r] 안에서 x 이상인 원소 개수"처럼
# 단순 합이 아니라 비교/정렬 정보가 필요할 수 있다.
#
# 이럴 때 각 블록을 정렬된 리스트로 유지하는 방법이 있다.
#
# 쿼리:
# - 자투리 직접 확인
# - 꽉 찬 블록은 bisect로 빠르게 계산
#
# 업데이트:
# - 블록에서 기존 값 제거
# - 새 값 삽입


class SqrtSortedBlocks:
    def __init__(self, arr):
        self.arr = arr[:]
        self.n = len(arr)
        self.block_size = int(math.sqrt(self.n)) + 1
        self.block_count = (self.n + self.block_size - 1) // self.block_size
        self.blocks = [[] for _ in range(self.block_count)]

        for i, value in enumerate(arr):
            self.blocks[i // self.block_size].append(value)

        for b in range(self.block_count):
            self.blocks[b].sort()

    def update(self, idx, value):
        block = idx // self.block_size
        old = self.arr[idx]

        # old 제거
        pos = bisect_left(self.blocks[block], old)
        self.blocks[block].pop(pos)

        # new 삽입
        insort(self.blocks[block], value)
        self.arr[idx] = value

    def count_ge(self, left, right, x):
        result = 0

        while left <= right and left % self.block_size != 0:
            if self.arr[left] >= x:
                result += 1
            left += 1

        while left + self.block_size - 1 <= right:
            block = left // self.block_size
            block_arr = self.blocks[block]
            pos = bisect_left(block_arr, x)
            result += len(block_arr) - pos
            left += self.block_size

        while left <= right:
            if self.arr[left] >= x:
                result += 1
            left += 1

        return result


sorted_block_example = SqrtSortedBlocks([5, 1, 7, 3, 2, 6, 4, 8, 9, 0])
count_ge_result_1 = sorted_block_example.count_ge(2, 8, 5)
sorted_block_example.update(3, 10)
count_ge_result_2 = sorted_block_example.count_ge(2, 8, 5)


# --------------------------------------------------
# [12. 정렬된 블록 문제 감각]
# --------------------------------------------------
# 각 블록을 정렬해두면
# "블록 전체에서 x 이상 개수"를 bisect로 빠르게 구할 수 있다.
#
# 이런 문제는 보통
# - 구간 내 x 이상 개수
# - 구간 내 x 초과 개수
# - 구간 내 x 이하 개수
#
# 류에서 등장한다.


# --------------------------------------------------
# [13. Square Root Decomposition의 전형적인 패턴]
# --------------------------------------------------
# 보통 아래와 같은 흐름이다.
#
# 1) 배열을 블록으로 나눈다
# 2) 각 블록의 요약 정보 저장
# 3) 쿼리할 때:
#    - 자투리 직접 처리
#    - 중간 블록은 요약 정보 사용
# 4) 업데이트 시:
#    - 해당 원소가 속한 블록 정보만 갱신
#
# "블록 요약 정보"가 무엇인지는 문제마다 달라진다.


# --------------------------------------------------
# [14. 대표적인 블록 요약 정보]
# --------------------------------------------------
# 문제에 따라 블록마다 저장할 수 있는 정보:
#
# - 합(sum)
# - 최솟값(min)
# - 최댓값(max)
# - 개수(count)
# - 정렬된 리스트(sorted block)
# - 빈도 배열(frequency)
# - 점프 횟수 / 다음 위치
#
# 즉, sqrt decomposition은 하나의 정형 템플릿이라기보다
# "블록으로 나누고 각 블록을 요약한다"는 아이디어에 가깝다.


# --------------------------------------------------
# [15. 점프류 문제에서도 사용됨]
# --------------------------------------------------
# 어떤 문제는 각 칸에서 다음 칸으로 이동하는 규칙이 있고,
# 이를 블록 단위로 압축해서 빠르게 점프 횟수를 계산할 수 있다.
#
# 예:
# - next[i] = i + arr[i]
# - 블록 안에서는 미리 다음 블록 진입 지점과 점프 수 저장
#
# 이런 식으로도 sqrt decomposition이 자주 활용된다.
#
# 이건 전형적인 "블록 DP / 블록 점프" 감각이다.


# --------------------------------------------------
# [16. 시간복잡도 감각]
# --------------------------------------------------
# 아주 전형적인 형태에서는 보통:
#
# - 전처리: O(N)
# - 쿼리: O(sqrt(N))
# - 업데이트: O(1) ~ O(sqrt(N)) ~ O(sqrt(N) log N)
#
# 문제에 따라 블록 내부 자료구조가 달라지면
# 시간복잡도도 조금 달라질 수 있다.
#
# 중요한 건 O(NQ)를 O((N+Q)sqrt(N)) 또는 그 비슷한 수준으로
# 줄일 수 있다는 점이다.


# --------------------------------------------------
# [17. 언제 세그먼트 트리 대신 쓸까]
# --------------------------------------------------
# sqrt decomposition이 좋은 경우:
# - 구현을 단순하게 하고 싶다
# - 문제 규모가 세그먼트 트리까지는 필요 없다
# - 블록 내부를 문제에 맞게 커스텀하고 싶다
# - 오프라인/특수 쿼리 구조에 잘 맞는다
#
# 세그먼트 트리가 좋은 경우:
# - 더 강한 성능이 필요하다
# - 범용적인 구간 쿼리/업데이트가 많다
#
# 즉, sqrt decomposition은 "구현 난이도 대비 효율이 좋은" 편이다.


# --------------------------------------------------
# [18. 대표 문제 유형]
# --------------------------------------------------
# sqrt / bucket은 아래 유형으로 자주 나온다.
#
# 1) 구간합 / 구간통계
#    - sum, count, min, max
#
# 2) 값 범위 버킷
#    - 존재 여부
#    - 첫 값 찾기
#    - 빈도 관리
#
# 3) 정렬된 블록
#    - 구간 내 x 이상/이하 개수
#
# 4) 점프/다음 위치 압축
#    - 블록 단위 점프 최적화
#
# 5) 구현형 최적화
#    - 단순 O(N) 반복을 블록 단위로 줄이기


# --------------------------------------------------
# [19. 자주 하는 실수]
# --------------------------------------------------
# 1) block_size / block_count 계산 실수
#
# 2) left/right 자투리 처리에서 인덱스 오류
#
# 3) 업데이트 시 원래 배열(arr)과 블록 정보가 불일치
#
# 4) 정렬된 블록 업데이트에서 기존 값 제거 위치를 잘못 찾음
#
# 5) 0-index / 1-index 혼동
#
# 6) 블록이 꽉 차지 않은 마지막 블록 처리 누락
#
# 7) 시간복잡도를 제대로 계산하지 않고
#    블록 내부에서 또 O(block_size) 이상 작업을 과하게 함
#
# 8) "블록 전체 처리 가능한지"를 확인하지 않고
#    애매한 경계도 전부 직접 순회해버림


# --------------------------------------------------
# [20. 문제를 보고 sqrt / bucket을 떠올리는 체크리스트]
# --------------------------------------------------
# 아래 질문 중 하나라도 "예"면 sqrt / bucket 후보일 가능성이 높다.
#
# - 배열을 구간으로 자주 질의하는가?
# - O(N) per query는 너무 느린가?
# - 블록 단위 요약이 가능해 보이는가?
# - 값 범위를 블록 단위로 나눌 수 있는가?
# - 세그먼트 트리보다 더 간단한 구조로 충분한가?
# - 자투리 + 꽉 찬 블록 분할이 자연스러운가?


# --------------------------------------------------
# [21. 실전 템플릿 1 - 구간합]
# --------------------------------------------------
class SqrtRangeSum:
    def __init__(self, arr):
        self.arr = arr[:]
        self.n = len(arr)
        self.block_size = int(math.sqrt(self.n)) + 1
        self.block_sum = [0] * ((self.n + self.block_size - 1) // self.block_size)

        for i, value in enumerate(arr):
            self.block_sum[i // self.block_size] += value

    def update(self, idx, value):
        block = idx // self.block_size
        self.block_sum[block] += value - self.arr[idx]
        self.arr[idx] = value

    def query(self, left, right):
        result = 0

        while left <= right and left % self.block_size != 0:
            result += self.arr[left]
            left += 1

        while left + self.block_size - 1 <= right:
            result += self.block_sum[left // self.block_size]
            left += self.block_size

        while left <= right:
            result += self.arr[left]
            left += 1

        return result


# --------------------------------------------------
# [22. 실전 템플릿 2 - 값 범위 빈도 버킷]
# --------------------------------------------------
class ValueBucket:
    def __init__(self, max_value):
        self.max_value = max_value
        self.block_size = int(math.sqrt(max_value + 1)) + 1
        self.freq = [0] * (max_value + 1)
        self.bucket = [0] * ((max_value + self.block_size) // self.block_size)

    def add(self, x):
        self.freq[x] += 1
        self.bucket[x // self.block_size] += 1

    def remove(self, x):
        if self.freq[x] > 0:
            self.freq[x] -= 1
            self.bucket[x // self.block_size] -= 1

    def exists(self, x):
        return self.freq[x] > 0


# --------------------------------------------------
# [23. 실전 템플릿 3 - 첫 값 찾기]
# --------------------------------------------------
class FirstAtLeastBucket:
    def __init__(self, max_value):
        self.max_value = max_value
        self.block_size = int(math.sqrt(max_value + 1)) + 1
        self.freq = [0] * (max_value + 1)
        self.bucket = [0] * ((max_value + self.block_size) // self.block_size)

    def add(self, x):
        self.freq[x] += 1
        self.bucket[x // self.block_size] += 1

    def remove(self, x):
        if self.freq[x] > 0:
            self.freq[x] -= 1
            self.bucket[x // self.block_size] -= 1

    def first_at_least(self, x):
        block = x // self.block_size

        start = x
        end = min(self.max_value, (block + 1) * self.block_size - 1)
        for value in range(start, end + 1):
            if self.freq[value] > 0:
                return value

        for b in range(block + 1, len(self.bucket)):
            if self.bucket[b] == 0:
                continue

            start = b * self.block_size
            end = min(self.max_value, (b + 1) * self.block_size - 1)
            for value in range(start, end + 1):
                if self.freq[value] > 0:
                    return value

        return -1


# --------------------------------------------------
# [24. 실전 템플릿 4 - 정렬된 블록]
# --------------------------------------------------
class RangeCountGE:
    def __init__(self, arr):
        self.arr = arr[:]
        self.n = len(arr)
        self.block_size = int(math.sqrt(self.n)) + 1
        self.blocks = [[] for _ in range((self.n + self.block_size - 1) // self.block_size)]

        for i, value in enumerate(arr):
            self.blocks[i // self.block_size].append(value)

        for block in self.blocks:
            block.sort()

    def update(self, idx, value):
        block_idx = idx // self.block_size
        old = self.arr[idx]

        pos = bisect_left(self.blocks[block_idx], old)
        self.blocks[block_idx].pop(pos)
        insort(self.blocks[block_idx], value)
        self.arr[idx] = value

    def count_ge(self, left, right, x):
        result = 0

        while left <= right and left % self.block_size != 0:
            if self.arr[left] >= x:
                result += 1
            left += 1

        while left + self.block_size - 1 <= right:
            block_idx = left // self.block_size
            block = self.blocks[block_idx]
            pos = bisect_left(block, x)
            result += len(block) - pos
            left += self.block_size

        while left <= right:
            if self.arr[left] >= x:
                result += 1
            left += 1

        return result


# --------------------------------------------------
# [25. 실전 템플릿 5 - 블록 최소값]
# --------------------------------------------------
class SqrtRangeMin:
    def __init__(self, arr):
        self.arr = arr[:]
        self.n = len(arr)
        self.block_size = int(math.sqrt(self.n)) + 1
        self.block_min = [float('inf')] * ((self.n + self.block_size - 1) // self.block_size)

        for i, value in enumerate(arr):
            block = i // self.block_size
            self.block_min[block] = min(self.block_min[block], value)

    def rebuild_block(self, block):
        start = block * self.block_size
        end = min(self.n, start + self.block_size)
        self.block_min[block] = min(self.arr[start:end])

    def update(self, idx, value):
        self.arr[idx] = value
        self.rebuild_block(idx // self.block_size)

    def query(self, left, right):
        result = float('inf')

        while left <= right and left % self.block_size != 0:
            result = min(result, self.arr[left])
            left += 1

        while left + self.block_size - 1 <= right:
            result = min(result, self.block_min[left // self.block_size])
            left += self.block_size

        while left <= right:
            result = min(result, self.arr[left])
            left += 1

        return result


# --------------------------------------------------
# [26. 예제 문제 감각]
# --------------------------------------------------
# 예제 1)
# 배열의 구간합 쿼리와 점 업데이트가 있다
# -> sqrt range sum
#
# 예제 2)
# 값 집합에서 x 이상인 가장 작은 값을 찾고 싶다
# -> value bucket
#
# 예제 3)
# 구간 [l, r] 안에서 x 이상인 수가 몇 개인가?
# -> 정렬된 블록 + bisect
#
# 예제 4)
# 구간 최솟값을 자주 구한다
# -> block min
#
# 예제 5)
# 각 위치에서 점프하는 문제를 블록 단위로 압축
# -> sqrt jump decomposition


# --------------------------------------------------
# [27. sqrt / bucket과 다른 주제의 연결]
# --------------------------------------------------
# - Binary Search:
#   정렬된 블록 + bisect 조합이 자주 나온다
#
# - Hash:
#   블록 내부 빈도/상태를 dict로 관리할 수도 있다
#
# - Implementation:
#   블록 경계 처리, 업데이트 반영이 핵심이다
#
# - Priority Queue:
#   직접 연결은 약하지만 블록 요약 정보를 관리하는 관점은 비슷하다
#
# - Time Based API:
#   직접 연결은 적지만 구간/범위 질의 최적화 감각은 이어진다


# --------------------------------------------------
# [28. 한 줄 요약]
# --------------------------------------------------
# Square Root Decomposition / Bucket = 배열이나 값 범위를 블록으로 나누고
# 각 블록의 요약 정보를 이용해 쿼리를 빠르게 처리하는 아이디어


# --------------------------------------------------
# [29. 최소 암기 포인트]
# --------------------------------------------------
# 1) block_size ≈ sqrt(N)
#
# 2) 자투리는 직접 처리
#
# 3) 꽉 찬 블록은 요약 정보 사용
#
# 4) update는 해당 블록만 갱신
#
# 5) 블록 요약 정보는 문제마다 다름
#    - sum / min / max / count / sorted list / freq
#
# 6) 세그먼트 트리보다 단순한 대안이 될 수 있음


# --------------------------------------------------
# [30. 다음 주제]
# --------------------------------------------------
# 다음 파일은 10_time_based_api.py 로 이어진다.
# Time Based API에서는
# timestamp 기준 저장, 시점 조회, dict + list + bisect 조합,
# time map 류 문제 패턴을 정리한다.


# --------------------------------------------------
# [참고]
# --------------------------------------------------
# 이 파일은 개념 정리용이다.
# 필요한 부분만 복붙해서 템플릿처럼 사용하면 된다.
# sqrt decomposition은 "블록으로 나누면 빨라질까?"라는 감각이 핵심이다.

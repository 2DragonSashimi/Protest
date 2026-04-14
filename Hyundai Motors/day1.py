# =========================
# Day 2 문법 / 도구 정리
# =========================

from collections import deque
import sys
input = sys.stdin.readline

# -------------------------------------------------
# 1) 배열 / 리스트
# -------------------------------------------------

arr = [3, 1, 4, 1, 5]

# 순회
for x in arr:
    print(x)

# 인덱스와 함께 순회
for i, x in enumerate(arr):
    print(i, x)

# 길이
n = len(arr)

# 최대 / 최소 / 합
mx = max(arr)
mn = min(arr)
s = sum(arr)

# 특정 값 개수
cnt = arr.count(1)

# 뒤집기
arr.reverse()              # 원본 변경
rev = arr[::-1]            # 새 리스트 생성

# 슬라이싱
sub = arr[1:4]

# 리스트 복사
a = [1, 2, 3]
b = a[:]                   # 얕은 복사
c = list(a)

# 2차원 리스트
grid = [[0] * 3 for _ in range(4)]   # 올바른 방식
# grid = [[0] * 3] * 4               # 위험: 같은 행 참조

# 주의: 얕은 복사 문제
grid[0][0] = 9

# -------------------------------------------------
# 2) 문자열
# -------------------------------------------------

s = "abc 123"

# 길이
print(len(s))

# 문자 하나씩 순회
for ch in s:
    print(ch)

# 공백 기준 분리
parts = s.split()

# 특정 문자열로 합치기
joined = "-".join(parts)

# 대문자 / 소문자
print(s.upper())
print(s.lower())

# 숫자인지 / 알파벳인지
print("123".isdigit())     # True
print("abc".isalpha())     # True

# 문자 -> 아스키코드 / 아스키코드 -> 문자
print(ord('A'))            # 65
print(chr(65))             # 'A'

# 문자열 치환
t = s.replace("abc", "xyz")

# 문자열 뒤집기
rev_s = s[::-1]

# -------------------------------------------------
# 3) 정렬
# -------------------------------------------------

arr = [5, 2, 4, 1, 3]

# 오름차순
arr.sort()

# 내림차순
arr.sort(reverse=True)

# sorted는 새 리스트 반환
b = sorted(arr)

# 문자열 정렬
words = ["banana", "apple", "kiwi"]
words.sort()

# 길이 기준 정렬
words.sort(key=len)

# 튜플 정렬
pairs = [(2, 3), (1, 5), (2, 1)]
pairs.sort()   # 첫 번째 -> 두 번째 순으로 자동 정렬

# 여러 기준 정렬
pairs.sort(key=lambda x: (x[0], -x[1]))
# 첫 번째 오름차순, 두 번째 내림차순

# 문자열 길이 -> 사전순
words = ["word", "a", "abc", "ab"]
words.sort(key=lambda x: (len(x), x))

# -------------------------------------------------
# 4) 스택
# -------------------------------------------------

stack = []

# push
stack.append(10)
stack.append(20)

# top 확인
if stack:
    print(stack[-1])

# pop
if stack:
    x = stack.pop()

# 비어있는지 확인
if not stack:
    print("empty")

# -------------------------------------------------
# 5) 큐 / deque
# -------------------------------------------------

q = deque()

# 뒤에 넣기
q.append(1)
q.append(2)

# 앞에서 빼기
if q:
    x = q.popleft()

# 앞에 넣기
q.appendleft(10)

# 뒤에서 빼기
if q:
    y = q.pop()

# 회전
q.rotate(1)    # 오른쪽으로 1칸
q.rotate(-1)   # 왼쪽으로 1칸

# -------------------------------------------------
# 6) 해시: dict / set
# -------------------------------------------------

# dict: 개수 세기, 값 저장
d = {}

arr = [1, 2, 1, 3, 2, 1]
for x in arr:
    d[x] = d.get(x, 0) + 1

print(d)       # {1: 3, 2: 2, 3: 1}

# key 존재 여부
if 2 in d:
    print(d[2])

# set: 중복 제거, 빠른 포함 여부 확인
s = set(arr)
print(s)

if 3 in s:
    print("exists")

# 중복 제거 후 정렬
unique_sorted = sorted(set(arr))

# -------------------------------------------------
# 7) 자주 하는 실수
# -------------------------------------------------

# [1] 2차원 리스트를 * 로 만들기
# bad = [[0] * 3] * 4

# [2] dict에서 없는 key 바로 접근
# print(d[100])   # KeyError 가능

# [3] 큐를 list.pop(0)으로 구현
# 비효율적이므로 deque.popleft() 사용

# [4] 정렬 기준을 if문으로 직접 처리하다 꼬임
# 가능하면 key=lambda 사용

# [5] 문자열/숫자 형변환 실수
x = "123"
num = int(x)
s = str(num)
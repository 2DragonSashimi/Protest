import sys

input = sys.stdin.readline

n, s = map(int, input().split())
nums = list(map(int, input().split()))

ans = 0 
temp = []

def back(start):
    global ans
    
    if len(temp) > 0 and sum(temp) == 0:
        ans += 1
    
    for i in range(start, n):
        temp.append(nums[i])
        back(i + 1)
        temp.pop()

back(0)
print(ans)

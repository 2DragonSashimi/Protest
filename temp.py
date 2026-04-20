import sys
sys.setrecursionlimit(10000)

n = int(input().rstrip())
ans = 0
visited = [[False]*n for _ in range(n)]

def find(depth,temp):
    global ans
    if depth == n:
        ans += 1
        
    for i in range(n):
        for j in range(n):
            if not visited[i][j]:
                if depth == 0:
                    temp.append((i,j))
                    visited[x][y] = True
                for x,y in temp:
                    if not (i == x or j == y or (i + j) == x + y or j - i == y - x):
                        temp.append((i,j))
                        visited[x][y] = True
                        find(depth + 1, temp)
                        temp.pop()
                        visited[x][y] = False
def show(arr):
    for row in arr:
        print(row)

find(0, [])
print(ans)

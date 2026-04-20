import sys
sys.setrecursionlimit(100000)

n = int(input().rstrip())
ans = 0
visited = [[False]*n for _ in range(n)]
def find(depth,temp):
    global ans
    if depth == n:
        ans += 1
        return
    for i in range(n):    
        for j in range(n):
            ok = True
            if not visited[i][j]:
                for x,y in temp:
                    if (i == x or j == y or (i + j) == x + y or j - i == y - x):
                        ok = False
                        break
                if ok:    
                    temp.append((i,j))
                    visited[i][j] = True
                    find(depth + 1, temp)
                    visited[i][j] = False
                    temp.pop()

find(0, [])
print(ans)

# ============================================
# 05. BFS / DFS
# ============================================

# --------------------------------------------------
# [1. 왜 필요한가]
# --------------------------------------------------
# BFS와 DFS는 그래프/트리/격자에서
# "연결된 노드들을 탐색"하기 위한 가장 기본적인 알고리즘이다.
#
# 예:
# - 연결 요소 개수 세기
# - 특정 노드/상태에 도달 가능한지 확인
# - 최단거리 구하기 (BFS)
# - 모든 경우를 탐색하기
# - 트리 순회
# - 격자(미로, 섬, 지도) 문제
#
# 코테에서는 매우 자주 나오며,
# 그래프 문제가 아니더라도 "상태 공간 탐색" 문제로 자주 변형된다.


# --------------------------------------------------
# [2. 언제 떠올려야 하는가]
# --------------------------------------------------
# 문제를 읽다가 아래 신호가 보이면 BFS/DFS를 먼저 의심한다.
#
# - 노드와 간선이 있다
# - 연결 여부를 확인해야 한다
# - 방문 가능한 칸/상태를 탐색해야 한다
# - 최단 이동 횟수를 구해야 한다
# - 미로 / 지도 / 섬 / 영역 / 컴포넌트 문제다
# - 모든 경우를 훑어봐야 한다
#
# 대표 예시:
# - 연결 요소 개수
# - 미로 최단거리
# - 섬의 개수
# - 바이러스 전파
# - 트리 순회
# - 상태 전이 탐색


# --------------------------------------------------
# [3. 핵심 아이디어]
# --------------------------------------------------
# DFS와 BFS는 둘 다 탐색이지만 성격이 다르다.
#
# 1. DFS (Depth First Search)
#    - 한 방향으로 끝까지 깊게 들어간다
#    - 재귀 / 스택으로 구현 가능
#    - 연결 요소, 백트래킹, 트리 탐색에 자주 사용
#
# 2. BFS (Breadth First Search)
#    - 가까운 것부터 넓게 탐색한다
#    - 큐(deque)로 구현
#    - "최단 거리(간선 수 기준)" 문제에 매우 강하다
#
# 핵심은:
# - 방문 처리
# - 인접 노드 확장
# - 중복 방문 방지


from collections import deque


# --------------------------------------------------
# [4. 그래프 표현 - 인접 리스트]
# --------------------------------------------------
# 그래프는 보통 인접 리스트로 표현한다.

n = 5
graph = [[] for _ in range(n + 1)]

# 예시 간선: 1-2, 1-3, 2-4, 3-5
edges = [(1, 2), (1, 3), (2, 4), (3, 5)]
for a, b in edges:
    graph[a].append(b)
    graph[b].append(a)   # 무방향 그래프

# 결과:
# graph[1] = [2, 3]
# graph[2] = [1, 4]
# graph[3] = [1, 5]
# ...


# --------------------------------------------------
# [5. DFS - 재귀]
# --------------------------------------------------
# 가장 기본적인 DFS 구현.
# 한 노드에서 시작해서 갈 수 있는 곳을 끝까지 탐색한다.

visited = [False] * (n + 1)

def dfs_recursive(node):
    visited[node] = True

    for nxt in graph[node]:
        if not visited[nxt]:
            dfs_recursive(nxt)

# 사용 예시
# dfs_recursive(1)


# --------------------------------------------------
# [6. DFS - 반복문(스택)]
# --------------------------------------------------
# 재귀 깊이 문제가 걱정되면 스택으로 구현할 수 있다.

def dfs_iterative(start, graph):
    n = len(graph) - 1
    visited = [False] * (n + 1)
    stack = [start]
    visited[start] = True

    order = []

    while stack:
        node = stack.pop()
        order.append(node)

        for nxt in reversed(graph[node]):
            if not visited[nxt]:
                visited[nxt] = True
                stack.append(nxt)

    return order

dfs_order = dfs_iterative(1, graph)


# --------------------------------------------------
# [7. BFS - 큐]
# --------------------------------------------------
# 가까운 노드부터 차례대로 탐색한다.
# 최단 거리 문제의 기본형이다.

def bfs(start, graph):
    n = len(graph) - 1
    visited = [False] * (n + 1)
    q = deque([start])
    visited[start] = True

    order = []

    while q:
        node = q.popleft()
        order.append(node)

        for nxt in graph[node]:
            if not visited[nxt]:
                visited[nxt] = True
                q.append(nxt)

    return order

bfs_order = bfs(1, graph)


# --------------------------------------------------
# [8. DFS와 BFS 순서 차이]
# --------------------------------------------------
# 같은 그래프라도 순회 순서는 다를 수 있다.
#
# DFS:
# - 깊게 들어감
#
# BFS:
# - 가까운 것부터 탐색
#
# 문제에서 "방문 순서"가 중요하면
# 보통 인접 리스트를 정렬해두기도 한다.

for i in range(1, n + 1):
    graph[i].sort()


# --------------------------------------------------
# [9. 방문 처리의 중요성]
# --------------------------------------------------
# 방문 처리를 하지 않으면 같은 노드를 계속 방문해서
# 무한루프나 중복 탐색이 발생할 수 있다.

# 핵심 패턴:
# if not visited[nxt]:
#     visited[nxt] = True
#     q.append(nxt)

# BFS에서는 보통 "큐에 넣을 때" 방문 처리하는 것이 중요하다.
# 큐에서 꺼낼 때 처리하면 중복 삽입이 생길 수 있다.


# --------------------------------------------------
# [10. 연결 요소 개수 세기]
# --------------------------------------------------
# 그래프가 여러 덩어리로 나뉘어 있을 때,
# DFS/BFS를 여러 번 돌려 개수를 셀 수 있다.

def count_components(n, graph):
    visited = [False] * (n + 1)

    def dfs(node):
        visited[node] = True
        for nxt in graph[node]:
            if not visited[nxt]:
                dfs(nxt)

    count = 0
    for node in range(1, n + 1):
        if not visited[node]:
            count += 1
            dfs(node)

    return count


# --------------------------------------------------
# [11. BFS로 최단 거리 구하기]
# --------------------------------------------------
# 간선의 가중치가 모두 같으면
# BFS로 최단 거리를 구할 수 있다.

def bfs_distance(start, graph):
    n = len(graph) - 1
    dist = [-1] * (n + 1)
    q = deque([start])
    dist[start] = 0

    while q:
        node = q.popleft()

        for nxt in graph[node]:
            if dist[nxt] == -1:
                dist[nxt] = dist[node] + 1
                q.append(nxt)

    return dist

distance_from_1 = bfs_distance(1, graph)

# dist[x] = 시작점에서 x까지의 최단 간선 수


# --------------------------------------------------
# [12. 왜 최단 거리에는 BFS인가]
# --------------------------------------------------
# BFS는 거리가 1인 노드들을 먼저,
# 그 다음 거리가 2인 노드들을,
# 그 다음 거리가 3인 노드들을 탐색한다.
#
# 따라서 가중치 없는 그래프에서는
# 처음 도달한 순간이 최단 거리이다.
#
# 반면 DFS는 깊게 먼저 들어가므로
# 최단 거리를 보장하지 않는다.


# --------------------------------------------------
# [13. 2차원 격자 탐색]
# --------------------------------------------------
# BFS/DFS는 격자 문제에서 매우 자주 나온다.
#
# 예:
# - 미로
# - 섬 개수
# - 그림 영역
# - 토마토
# - 불 번짐
#
# 보통 상하좌우 이동 배열을 같이 사용한다.

grid = [
    [1, 1, 0],
    [0, 1, 0],
    [1, 0, 1]
]

rows = len(grid)
cols = len(grid[0])

dr = [-1, 1, 0, 0]
dc = [0, 0, -1, 1]


# --------------------------------------------------
# [14. 격자 DFS]
# --------------------------------------------------
def dfs_grid(r, c, grid, visited):
    rows = len(grid)
    cols = len(grid[0])

    visited[r][c] = True

    for k in range(4):
        nr = r + dr[k]
        nc = c + dc[k]

        if 0 <= nr < rows and 0 <= nc < cols:
            if grid[nr][nc] == 1 and not visited[nr][nc]:
                dfs_grid(nr, nc, grid, visited)


visited_grid = [[False] * cols for _ in range(rows)]


# --------------------------------------------------
# [15. 격자 BFS]
# --------------------------------------------------
def bfs_grid(sr, sc, grid):
    rows = len(grid)
    cols = len(grid[0])

    visited = [[False] * cols for _ in range(rows)]
    q = deque([(sr, sc)])
    visited[sr][sc] = True

    order = []

    while q:
        r, c = q.popleft()
        order.append((r, c))

        for k in range(4):
            nr = r + dr[k]
            nc = c + dc[k]

            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 1 and not visited[nr][nc]:
                    visited[nr][nc] = True
                    q.append((nr, nc))

    return order


# --------------------------------------------------
# [16. 격자에서 영역 개수 세기]
# --------------------------------------------------
# 섬 개수, 그림 개수, 연결된 1의 영역 개수 같은 문제.

def count_islands(grid):
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]

    def dfs(r, c):
        visited[r][c] = True

        for k in range(4):
            nr = r + dr[k]
            nc = c + dc[k]

            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 1 and not visited[nr][nc]:
                    dfs(nr, nc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not visited[r][c]:
                count += 1
                dfs(r, c)

    return count

island_count = count_islands(grid)


# --------------------------------------------------
# [17. 격자 최단 거리]
# --------------------------------------------------
# 미로 문제처럼 시작점에서 도착점까지 최소 이동 횟수를 구할 때 BFS를 쓴다.

maze = [
    [1, 1, 1, 0],
    [0, 1, 0, 1],
    [1, 1, 1, 1]
]

def shortest_path_grid(grid, sr, sc, tr, tc):
    rows = len(grid)
    cols = len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]

    q = deque([(sr, sc)])
    dist[sr][sc] = 0

    while q:
        r, c = q.popleft()

        if (r, c) == (tr, tc):
            return dist[r][c]

        for k in range(4):
            nr = r + dr[k]
            nc = c + dc[k]

            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 1 and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))

    return -1

maze_dist = shortest_path_grid(maze, 0, 0, 2, 3)


# --------------------------------------------------
# [18. 트리에서도 DFS/BFS를 쓴다]
# --------------------------------------------------
# 트리는 사이클 없는 그래프이므로 DFS/BFS를 그대로 사용할 수 있다.
#
# 자주 하는 것:
# - 부모 찾기
# - 깊이(depth) 구하기
# - 서브트리 탐색
# - 순회
#
# 예: 부모와 깊이 구하기

tree_n = 5
tree = [[] for _ in range(tree_n + 1)]
tree_edges = [(1, 2), (1, 3), (2, 4), (2, 5)]

for a, b in tree_edges:
    tree[a].append(b)
    tree[b].append(a)

parent = [0] * (tree_n + 1)
depth = [-1] * (tree_n + 1)

def bfs_tree(root, tree):
    q = deque([root])
    depth[root] = 0

    while q:
        node = q.popleft()

        for nxt in tree[node]:
            if depth[nxt] == -1:
                parent[nxt] = node
                depth[nxt] = depth[node] + 1
                q.append(nxt)

bfs_tree(1, tree)


# --------------------------------------------------
# [19. DFS는 "모든 경우 탐색"에도 자주 쓰인다]
# --------------------------------------------------
# DFS는 단순 그래프 탐색뿐 아니라
# 백트래킹/브루트포스와도 자주 연결된다.
#
# 예:
# - 부분수열
# - 순열/조합
# - 선택/비선택
# - 상태 재귀 탐색
#
# 즉, DFS = 그래프 전용이라고 생각하면 안 된다.


# --------------------------------------------------
# [20. 시간복잡도]
# --------------------------------------------------
# 그래프에서 DFS/BFS는 보통
# O(V + E)
#
# V = 정점 수
# E = 간선 수
#
# 격자에서는 보통
# O(R * C)
#
# 각 노드/칸을 많아야 한 번씩만 방문하기 때문이다.


# --------------------------------------------------
# [21. 대표 문제 유형]
# --------------------------------------------------
# BFS/DFS는 아래 유형으로 자주 나온다.
#
# 1) 연결 요소
#    - 컴포넌트 개수
#    - 섬의 개수
#
# 2) 도달 가능 여부
#    - 시작점에서 목표점에 갈 수 있는가?
#
# 3) 최단 거리
#    - 가중치 없는 그래프
#    - 격자 최단 이동
#
# 4) 영역 탐색
#    - 상하좌우 / 8방향 탐색
#
# 5) 트리 탐색
#    - 부모, 깊이, 서브트리
#
# 6) 상태 탐색
#    - 문자열 변환
#    - 버튼 누르기
#    - 게임 상태 이동
#
# 7) 백트래킹/완전탐색
#    - DFS 재귀 구조 응용


# --------------------------------------------------
# [22. 자주 하는 실수]
# --------------------------------------------------
# 1) 방문 처리를 빼먹음
#    -> 무한루프 / 중복 탐색
#
# 2) BFS에서 큐에 넣을 때가 아니라 꺼낼 때 방문 처리
#    -> 중복 삽입 가능
#
# 3) 격자 범위 체크 실수
#    -> 인덱스 에러
#
# 4) 상하좌우 배열(dr, dc) 실수
#
# 5) DFS 재귀 깊이 초과
#    -> 필요하면 sys.setrecursionlimit 사용
#    -> 또는 반복문 DFS 사용
#
# 6) 그래프가 무방향인지 방향인지 헷갈림
#    -> 간선 추가 방식 확인 필요
#
# 7) BFS로 풀어야 할 최단거리 문제를 DFS로 접근
#
# 8) dist 배열과 visited 배열 역할 혼동
#    -> dist == -1 자체가 방문 체크 역할을 할 수도 있다


# --------------------------------------------------
# [23. 문제를 보고 BFS/DFS를 떠올리는 체크리스트]
# --------------------------------------------------
# 아래 질문 중 하나라도 "예"면 BFS/DFS 후보일 가능성이 높다.
#
# - 연결 여부를 확인해야 하는가?
# - 갈 수 있는 상태들을 모두 탐색해야 하는가?
# - 격자에서 상하좌우 이동하는가?
# - 가중치 없는 최단 거리를 구해야 하는가?
# - 영역/컴포넌트 개수를 세야 하는가?
# - 트리/그래프 순회가 필요한가?


# --------------------------------------------------
# [24. 실전 템플릿 1 - 그래프 DFS]
# --------------------------------------------------
def dfs_graph(start, graph):
    n = len(graph) - 1
    visited = [False] * (n + 1)
    order = []

    def dfs(node):
        visited[node] = True
        order.append(node)

        for nxt in graph[node]:
            if not visited[nxt]:
                dfs(nxt)

    dfs(start)
    return order


# --------------------------------------------------
# [25. 실전 템플릿 2 - 그래프 BFS]
# --------------------------------------------------
def bfs_graph(start, graph):
    n = len(graph) - 1
    visited = [False] * (n + 1)
    q = deque([start])
    visited[start] = True

    order = []

    while q:
        node = q.popleft()
        order.append(node)

        for nxt in graph[node]:
            if not visited[nxt]:
                visited[nxt] = True
                q.append(nxt)

    return order


# --------------------------------------------------
# [26. 실전 템플릿 3 - 연결 요소 개수]
# --------------------------------------------------
def count_components_template(n, graph):
    visited = [False] * (n + 1)

    def dfs(node):
        visited[node] = True
        for nxt in graph[node]:
            if not visited[nxt]:
                dfs(nxt)

    count = 0
    for node in range(1, n + 1):
        if not visited[node]:
            count += 1
            dfs(node)

    return count


# --------------------------------------------------
# [27. 실전 템플릿 4 - 격자 BFS 최단 거리]
# --------------------------------------------------
def grid_bfs_shortest(grid, sr, sc, tr, tc):
    rows = len(grid)
    cols = len(grid[0])
    dr = [-1, 1, 0, 0]
    dc = [0, 0, -1, 1]

    dist = [[-1] * cols for _ in range(rows)]
    q = deque([(sr, sc)])
    dist[sr][sc] = 0

    while q:
        r, c = q.popleft()

        if (r, c) == (tr, tc):
            return dist[r][c]

        for k in range(4):
            nr = r + dr[k]
            nc = c + dc[k]

            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 1 and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))

    return -1


# --------------------------------------------------
# [28. 실전 템플릿 5 - 격자 영역 개수]
# --------------------------------------------------
def count_regions(grid):
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    dr = [-1, 1, 0, 0]
    dc = [0, 0, -1, 1]

    def dfs(r, c):
        visited[r][c] = True

        for k in range(4):
            nr = r + dr[k]
            nc = c + dc[k]

            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 1 and not visited[nr][nc]:
                    dfs(nr, nc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not visited[r][c]:
                count += 1
                dfs(r, c)

    return count


# --------------------------------------------------
# [29. 예제 문제 감각]
# --------------------------------------------------
# 예제 1)
# 그래프가 몇 개의 연결 요소로 나뉘어 있는가?
# -> DFS/BFS
#
# 예제 2)
# 시작점에서 목표점까지 갈 수 있는가?
# -> DFS/BFS
#
# 예제 3)
# 미로에서 최소 몇 칸 이동해야 하는가?
# -> BFS
#
# 예제 4)
# 격자에서 1로 이루어진 영역은 몇 개인가?
# -> DFS/BFS
#
# 예제 5)
# 트리에서 각 노드의 부모를 구하라
# -> BFS/DFS
#
# 예제 6)
# 가중치 없는 그래프에서 최단 거리 구하기
# -> BFS


# --------------------------------------------------
# [30. BFS/DFS와 다른 주제의 연결]
# --------------------------------------------------
# - Union-Find:
#   연결 요소 문제를 다른 방식으로 풀 수 있다
#
# - Shortest Path:
#   가중치 없는 경우는 BFS, 가중치 있으면 다익스트라 등으로 확장
#
# - Tree / LCA:
#   깊이/부모 계산에 DFS/BFS가 기본
#
# - String / 구현:
#   문자열 상태 변환 문제를 BFS로 푸는 경우가 있다
#
# - 백트래킹:
#   DFS 구조가 그대로 연결된다


# --------------------------------------------------
# [31. 한 줄 요약]
# --------------------------------------------------
# BFS / DFS = 그래프, 트리, 격자, 상태공간을 탐색하는 기본 도구
# BFS는 최단 거리, DFS는 깊은 탐색/구조 파악에 강하다


# --------------------------------------------------
# [32. 최소 암기 포인트]
# --------------------------------------------------
# 1) DFS:
#    재귀 또는 스택
#
# 2) BFS:
#    deque 사용
#
# 3) 방문 처리:
#    visited 배열 필수
#
# 4) 격자 탐색:
#    dr, dc
#
# 5) 최단 거리:
#    가중치 없으면 BFS
#
# 6) 연결 요소:
#    방문 안 한 노드에서 DFS/BFS 시작


# --------------------------------------------------
# [33. 다음 주제]
# --------------------------------------------------
# 다음 파일은 06_union_find.py 로 이어진다.
# Union-Find에서는
# 집합 병합, 같은 집합 판별, 연결 요소 관리, 사이클 판별 등을 정리한다.


# --------------------------------------------------
# [참고]
# --------------------------------------------------
# 이 파일은 개념 정리용이다.
# 필요한 부분만 복붙해서 템플릿처럼 사용하면 된다.
# BFS/DFS는 코테에서 가장 기본이 되는 탐색 도구이므로,
# 그래프와 격자 양쪽 템플릿을 모두 손에 익히는 것이 중요하다.

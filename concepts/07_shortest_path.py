# ============================================
# 07. Shortest Path
# ============================================

# --------------------------------------------------
# [1. 왜 필요한가]
# --------------------------------------------------
# Shortest Path(최단경로)는
# "한 지점에서 다른 지점까지 가는 최소 비용/최소 거리/최소 시간"을 구하는 문제다.
#
# 그래프 문제에서 매우 자주 등장하며,
# 상황에 따라 사용하는 알고리즘이 달라진다.
#
# 대표적으로:
# - 가중치가 없는 그래프 -> BFS
# - 가중치가 모두 0 이상 -> Dijkstra
# - 음수 간선이 있을 수 있음 -> Bellman-Ford
# - 모든 정점 쌍 최단거리 -> Floyd-Warshall
#
# 핵심은
# "그래프의 간선 가중치 조건에 따라 알고리즘을 올바르게 고르는 것"이다.


# --------------------------------------------------
# [2. 언제 떠올려야 하는가]
# --------------------------------------------------
# 문제를 읽다가 아래 신호가 보이면 최단경로를 먼저 의심한다.
#
# - A에서 B까지 최소 비용 / 최소 시간 / 최소 거리
# - 이동 비용이 존재한다
# - 여러 도시/노드/정점이 간선으로 연결되어 있다
# - 가장 빠른 경로 / 가장 싼 경로 / 최소 이동 횟수
# - 모든 정점 간 거리 또는 특정 시작점 기준 최소 거리
#
# 대표 예시:
# - 도시 간 버스 비용 최소화
# - 특정 위치까지 최소 시간
# - 네트워크 지연 시간
# - 지하철/도로/물류 경로
# - 미로 최단거리
# - 음수 간선 포함 그래프


# --------------------------------------------------
# [3. 핵심 아이디어]
# --------------------------------------------------
# 최단경로는 보통 아래처럼 구분해서 생각하면 된다.
#
# 1. 가중치 없는 그래프
#    -> BFS
#
# 2. 가중치가 모두 0 이상
#    -> Dijkstra
#
# 3. 음수 간선 가능
#    -> Bellman-Ford
#
# 4. 모든 정점 쌍의 최단거리
#    -> Floyd-Warshall
#
# 즉, "문제의 그래프 조건"을 먼저 봐야 한다.


from collections import deque
import heapq


INF = 10**18


# --------------------------------------------------
# [4. 그래프 표현]
# --------------------------------------------------
# 최단경로 문제는 보통 인접 리스트로 그래프를 표현한다.
#
# graph[u] = [(v, cost), ...]
#
# 즉, u에서 v로 가는 비용이 cost라는 뜻이다.

n = 5
graph = [[] for _ in range(n + 1)]

edges = [
    (1, 2, 2),
    (1, 3, 5),
    (2, 3, 1),
    (2, 4, 2),
    (3, 5, 3),
    (4, 5, 1),
]

for a, b, cost in edges:
    graph[a].append((b, cost))


# --------------------------------------------------
# [5. 가중치 없는 그래프 -> BFS]
# --------------------------------------------------
# 간선 가중치가 모두 동일(보통 1)이라면 BFS로 최단거리를 구할 수 있다.

unweighted_graph = [[] for _ in range(6)]
unweighted_edges = [(1, 2), (1, 3), (2, 4), (3, 5), (4, 5)]

for a, b in unweighted_edges:
    unweighted_graph[a].append(b)
    unweighted_graph[b].append(a)

def bfs_shortest(start, graph):
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

bfs_dist = bfs_shortest(1, unweighted_graph)

# dist[x] = 시작점에서 x까지의 최소 간선 수


# --------------------------------------------------
# [6. 왜 가중치 없는 그래프는 BFS인가]
# --------------------------------------------------
# BFS는 거리 1인 노드들을 먼저,
# 그 다음 거리 2인 노드들,
# 그 다음 거리 3인 노드들을 방문한다.
#
# 따라서 처음 방문한 순간이 최단 거리이다.
#
# 단, 이건 "모든 간선의 가중치가 같을 때"만 성립한다.
# 가중치가 다르면 BFS는 최단거리를 보장하지 않는다.


# --------------------------------------------------
# [7. 가중치가 0 이상 -> Dijkstra]
# --------------------------------------------------
# 가장 자주 쓰는 최단경로 알고리즘.
# 시작점 하나에서 모든 정점까지의 최단거리를 구할 수 있다.
#
# 핵심:
# "현재까지 가장 거리가 짧은 정점부터 처리"

def dijkstra(start, graph):
    n = len(graph) - 1
    dist = [INF] * (n + 1)
    dist[start] = 0

    pq = []
    heapq.heappush(pq, (0, start))   # (현재까지 거리, 노드)

    while pq:
        cur_dist, node = heapq.heappop(pq)

        # 이미 더 좋은 값이 dist에 있으면 버림
        if cur_dist > dist[node]:
            continue

        for nxt, cost in graph[node]:
            new_dist = cur_dist + cost
            if new_dist < dist[nxt]:
                dist[nxt] = new_dist
                heapq.heappush(pq, (new_dist, nxt))

    return dist

dijkstra_dist = dijkstra(1, graph)


# --------------------------------------------------
# [8. 다익스트라의 핵심 감각]
# --------------------------------------------------
# 우선순위 큐에서 "가장 짧은 거리 후보"를 먼저 꺼낸다.
#
# 그리고 그 노드에서 갈 수 있는 이웃들의 거리 값을 갱신(relaxation)한다.
#
# 핵심 패턴:
# - dist[start] = 0
# - pq에 (거리, 노드)
# - 꺼냈는데 이미 더 긴 거리면 skip
# - 더 짧아지면 dist 갱신 + pq push
#
# 이 알고리즘은 "간선 가중치가 음수가 없을 때"만 안전하다.


# --------------------------------------------------
# [9. relaxation(완화)]
# --------------------------------------------------
# 최단경로 알고리즘의 핵심 연산.
#
# 현재 node까지 거리 = cur_dist
# node -> nxt 비용 = cost
# 그러면 nxt까지 새 후보 거리 = cur_dist + cost
#
# 만약 이 값이 현재 dist[nxt]보다 작으면 갱신한다.

# if cur_dist + cost < dist[nxt]:
#     dist[nxt] = cur_dist + cost


# --------------------------------------------------
# [10. 다익스트라에서 자주 하는 실수]
# --------------------------------------------------
# 1) visited 배열을 잘못 섞어서 사용
#    -> dist 배열만으로 충분한 경우가 많다
#
# 2) 우선순위 큐에서 꺼낸 값이 오래된 값인지 체크 안 함
#    -> if cur_dist > dist[node]: continue
#
# 3) 음수 간선이 있는데 다익스트라 사용
#
# 4) 무방향 그래프인데 간선을 한쪽만 추가
#
# 5) INF를 너무 작게 잡음


# --------------------------------------------------
# [11. 경로 복원]
# --------------------------------------------------
# 최단거리 값뿐 아니라 실제 경로를 복원하고 싶다면
# prev 배열(이전 노드)을 저장하면 된다.

def dijkstra_with_path(start, graph):
    n = len(graph) - 1
    dist = [INF] * (n + 1)
    prev = [-1] * (n + 1)
    dist[start] = 0

    pq = [(0, start)]

    while pq:
        cur_dist, node = heapq.heappop(pq)

        if cur_dist > dist[node]:
            continue

        for nxt, cost in graph[node]:
            new_dist = cur_dist + cost
            if new_dist < dist[nxt]:
                dist[nxt] = new_dist
                prev[nxt] = node
                heapq.heappush(pq, (new_dist, nxt))

    return dist, prev

dist_path, prev_path = dijkstra_with_path(1, graph)

def restore_path(target, prev):
    path = []
    cur = target

    while cur != -1:
        path.append(cur)
        cur = prev[cur]

    path.reverse()
    return path

path_to_5 = restore_path(5, prev_path)


# --------------------------------------------------
# [12. 음수 간선 가능 -> Bellman-Ford]
# --------------------------------------------------
# 음수 간선이 있으면 다익스트라를 쓰면 안 된다.
# 이때 Bellman-Ford를 고려한다.
#
# 특징:
# - 음수 간선 처리 가능
# - 음수 사이클 감지 가능
# - 시간복잡도는 느림: O(VE)

def bellman_ford(start, n, edges):
    dist = [INF] * (n + 1)
    dist[start] = 0

    # V-1번 완화
    for _ in range(n - 1):
        updated = False
        for a, b, cost in edges:
            if dist[a] != INF and dist[a] + cost < dist[b]:
                dist[b] = dist[a] + cost
                updated = True
        if not updated:
            break

    # 음수 사이클 확인
    has_negative_cycle = False
    for a, b, cost in edges:
        if dist[a] != INF and dist[a] + cost < dist[b]:
            has_negative_cycle = True
            break

    return dist, has_negative_cycle

bf_dist, bf_neg_cycle = bellman_ford(1, n, edges)


# --------------------------------------------------
# [13. Bellman-Ford의 핵심 감각]
# --------------------------------------------------
# 최단경로는 최대 V-1개의 간선을 사용하는 단순 경로로 표현 가능하므로
# 모든 간선을 V-1번 완화하면 최단거리 계산이 가능하다.
#
# 만약 한 번 더 완화가 가능하다면
# 음수 사이클이 있다는 뜻이다.


# --------------------------------------------------
# [14. 모든 정점 쌍 -> Floyd-Warshall]
# --------------------------------------------------
# 모든 정점 쌍 (i, j)에 대한 최단거리를 구할 때 사용한다.
#
# 특징:
# - 구현은 간단한 편
# - O(N^3) 이라서 정점 수가 작을 때만 가능
# - 음수 간선은 가능하지만 음수 사이클은 주의

def floyd_warshall(n, edges):
    dist = [[INF] * (n + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dist[i][i] = 0

    for a, b, cost in edges:
        if cost < dist[a][b]:
            dist[a][b] = cost

    for k in range(1, n + 1):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist

fw_dist = floyd_warshall(n, edges)


# --------------------------------------------------
# [15. Floyd-Warshall의 핵심 감각]
# --------------------------------------------------
# dist[i][j] = i에서 j로 가는 최단거리
#
# 중간에 k를 거쳐 가는 경우를 허용하면서
# 점점 더 좋은 경로를 찾는다.
#
# 점화식:
# dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])


# --------------------------------------------------
# [16. 어떤 알고리즘을 선택해야 하는가]
# --------------------------------------------------
# 아래처럼 정리하면 된다.
#
# 1) 가중치 없음 / 모두 1
#    -> BFS
#
# 2) 가중치 0 이상, 시작점 하나
#    -> Dijkstra
#
# 3) 음수 간선 있음
#    -> Bellman-Ford
#
# 4) 모든 정점 쌍
#    -> Floyd-Warshall
#
# 5) 정점 수가 아주 작다
#    -> Floyd-Warshall도 고려 가능
#
# 6) 정점 수가 크다
#    -> 보통 Dijkstra


# --------------------------------------------------
# [17. 시간복잡도]
# --------------------------------------------------
# BFS:
# - O(V + E)
#
# Dijkstra (heapq):
# - O((V + E) log V)
#
# Bellman-Ford:
# - O(VE)
#
# Floyd-Warshall:
# - O(V^3)
#
# 문제 크기를 보고 적절히 선택해야 한다.


# --------------------------------------------------
# [18. 대표 문제 유형]
# --------------------------------------------------
# Shortest Path는 아래 유형으로 자주 나온다.
#
# 1) 시작점 하나 -> 모든 정점
#    - Dijkstra
#
# 2) 시작점 -> 도착점 하나
#    - Dijkstra / BFS
#
# 3) 가중치 없는 그래프 최단거리
#    - BFS
#
# 4) 음수 간선
#    - Bellman-Ford
#
# 5) 모든 정점 쌍 거리
#    - Floyd-Warshall
#
# 6) 최소 비용/최소 시간/최소 거리
#    - 거의 전형적인 최단경로 신호


# --------------------------------------------------
# [19. 자주 하는 실수]
# --------------------------------------------------
# 1) 가중치가 있는데 BFS 사용
#
# 2) 음수 간선이 있는데 Dijkstra 사용
#
# 3) 무방향 그래프인데 간선을 한쪽만 추가
#
# 4) dist 초기값을 너무 작게 둠
#
# 5) 도달 불가능한 정점을 처리 안 함
#    -> INF 상태 유지 확인 필요
#
# 6) pq에서 나온 오래된 상태를 걸러내지 않음
#
# 7) Floyd-Warshall에서 자기 자신 dist[i][i] = 0 초기화 누락
#
# 8) 중복 간선 있을 때 더 작은 비용만 남기는 처리 누락
#
# 9) 1-index / 0-index 혼동


# --------------------------------------------------
# [20. 문제를 보고 Shortest Path를 떠올리는 체크리스트]
# --------------------------------------------------
# 아래 질문 중 하나라도 "예"면 최단경로 후보일 가능성이 높다.
#
# - 최소 비용 / 최소 시간 / 최소 거리인가?
# - 도시/노드/정점 간 이동인가?
# - 간선 가중치가 있는가?
# - 가중치가 모두 같은가?
# - 음수 간선이 있는가?
# - 모든 정점 쌍이 필요한가?


# --------------------------------------------------
# [21. 실전 템플릿 1 - BFS 최단거리]
# --------------------------------------------------
def shortest_unweighted(start, graph):
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


# --------------------------------------------------
# [22. 실전 템플릿 2 - 다익스트라]
# --------------------------------------------------
def dijkstra_template(start, graph):
    n = len(graph) - 1
    dist = [INF] * (n + 1)
    dist[start] = 0

    pq = [(0, start)]

    while pq:
        cur_dist, node = heapq.heappop(pq)

        if cur_dist > dist[node]:
            continue

        for nxt, cost in graph[node]:
            new_dist = cur_dist + cost
            if new_dist < dist[nxt]:
                dist[nxt] = new_dist
                heapq.heappush(pq, (new_dist, nxt))

    return dist


# --------------------------------------------------
# [23. 실전 템플릿 3 - 벨만포드]
# --------------------------------------------------
def bellman_ford_template(start, n, edges):
    dist = [INF] * (n + 1)
    dist[start] = 0

    for _ in range(n - 1):
        updated = False
        for a, b, cost in edges:
            if dist[a] != INF and dist[a] + cost < dist[b]:
                dist[b] = dist[a] + cost
                updated = True
        if not updated:
            break

    for a, b, cost in edges:
        if dist[a] != INF and dist[a] + cost < dist[b]:
            return dist, True   # negative cycle exists

    return dist, False


# --------------------------------------------------
# [24. 실전 템플릿 4 - 플로이드워셜]
# --------------------------------------------------
def floyd_warshall_template(n, edges):
    dist = [[INF] * (n + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dist[i][i] = 0

    for a, b, cost in edges:
        dist[a][b] = min(dist[a][b], cost)

    for k in range(1, n + 1):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


# --------------------------------------------------
# [25. 실전 템플릿 5 - 경로 복원 다익스트라]
# --------------------------------------------------
def dijkstra_path_template(start, graph):
    n = len(graph) - 1
    dist = [INF] * (n + 1)
    prev = [-1] * (n + 1)
    dist[start] = 0

    pq = [(0, start)]

    while pq:
        cur_dist, node = heapq.heappop(pq)

        if cur_dist > dist[node]:
            continue

        for nxt, cost in graph[node]:
            new_dist = cur_dist + cost
            if new_dist < dist[nxt]:
                dist[nxt] = new_dist
                prev[nxt] = node
                heapq.heappush(pq, (new_dist, nxt))

    return dist, prev


def restore_path_template(target, prev):
    path = []
    cur = target
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


# --------------------------------------------------
# [26. 예제 문제 감각]
# --------------------------------------------------
# 예제 1)
# 미로에서 출발점에서 도착점까지 최소 칸 수
# -> BFS
#
# 예제 2)
# 도시 간 버스 비용 최소화
# -> Dijkstra
#
# 예제 3)
# 음수 간선이 있는 환율/보상 문제
# -> Bellman-Ford
#
# 예제 4)
# 모든 도시 사이 최단거리 표 만들기
# -> Floyd-Warshall
#
# 예제 5)
# 최단거리뿐 아니라 실제 경로도 출력
# -> Dijkstra + prev 배열


# --------------------------------------------------
# [27. Shortest Path와 다른 주제의 연결]
# --------------------------------------------------
# - BFS/DFS:
#   가중치 없는 최단거리는 BFS와 바로 연결된다
#
# - Priority Queue:
#   Dijkstra의 핵심 도구이다
#
# - Graph:
#   최단경로는 그래프 문제의 대표 유형이다
#
# - Binary Search:
#   간혹 "특정 비용 이하로 가능한가?" 식으로 결합되기도 한다
#
# - Implementation:
#   그래프 입력 처리, 경로 복원, 다중 테스트케이스 관리가 중요하다


# --------------------------------------------------
# [28. 한 줄 요약]
# --------------------------------------------------
# Shortest Path = 그래프에서 최소 비용/최소 거리/최소 시간을 구하는 문제이며
# 조건에 따라 BFS, Dijkstra, Bellman-Ford, Floyd-Warshall을 선택한다


# --------------------------------------------------
# [29. 최소 암기 포인트]
# --------------------------------------------------
# 1) 가중치 없음:
#    BFS
#
# 2) 가중치 0 이상:
#    Dijkstra
#
# 3) 음수 간선:
#    Bellman-Ford
#
# 4) 모든 정점 쌍:
#    Floyd-Warshall
#
# 5) 다익스트라 핵심:
#    if cur_dist > dist[node]: continue
#
# 6) 경로 복원:
#    prev 배열 저장


# --------------------------------------------------
# [30. 다음 주제]
# --------------------------------------------------
# 다음 파일은 08_tree_lca.py 로 이어진다.
# Tree / LCA에서는
# 트리의 기본 성질, 부모/깊이, 공통 조상, binary lifting 등을 정리한다.


# --------------------------------------------------
# [참고]
# --------------------------------------------------
# 이 파일은 개념 정리용이다.
# 필요한 부분만 복붙해서 템플릿처럼 사용하면 된다.
# 최단경로 문제는 "가중치 조건"을 먼저 보고
# 알고리즘을 고르는 습관이 가장 중요하다.

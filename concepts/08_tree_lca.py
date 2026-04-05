# ============================================
# 08. Tree / LCA
# ============================================

# --------------------------------------------------
# [1. 왜 필요한가]
# --------------------------------------------------
# 트리(Tree)는 코테에서 매우 자주 나오는 그래프의 특수한 형태다.
#
# 트리의 핵심 특징:
# - 정점이 N개면 간선은 N-1개
# - 연결되어 있음
# - 사이클이 없음
#
# 트리 문제에서는 보통 아래를 자주 구한다.
# - 부모(parent)
# - 깊이(depth)
# - 서브트리(subtree)
# - 두 노드의 공통 조상
# - 두 노드 사이 거리
#
# 특히 LCA(Lowest Common Ancestor)는
# "두 노드의 가장 가까운 공통 조상"을 구하는 대표적인 트리 문제다.


# --------------------------------------------------
# [2. 언제 떠올려야 하는가]
# --------------------------------------------------
# 문제를 읽다가 아래 신호가 보이면 Tree / LCA를 먼저 의심한다.
#
# - 그래프인데 사이클이 없고 연결되어 있다
# - 부모/자식 관계가 중요하다
# - 루트 기준으로 깊이가 필요하다
# - 두 노드의 공통 조상을 구해야 한다
# - 두 노드 사이 거리나 경로를 계산해야 한다
# - 여러 번의 공통 조상 질의가 들어온다
#
# 대표 예시:
# - 트리의 부모 찾기
# - 트리 순회
# - 서브트리 크기
# - 두 노드의 거리
# - 공통 조상 찾기
# - LCA 쿼리


# --------------------------------------------------
# [3. 핵심 아이디어]
# --------------------------------------------------
# 트리 문제의 기본은 아래 4개다.
#
# 1. 루트 정하기
#    - 보통 1번 노드를 루트로 잡는다
#
# 2. parent / depth 구하기
#    - DFS/BFS로 계산
#
# 3. 공통 조상 찾기
#    - 단순히 부모를 타고 올라가도 가능
#
# 4. LCA 최적화
#    - binary lifting(희소 테이블) 사용
#
# 즉, 트리 문제는 결국
# "부모 관계와 깊이"를 얼마나 잘 관리하느냐가 핵심이다.


from collections import deque


# --------------------------------------------------
# [4. 트리 표현]
# --------------------------------------------------
# 트리는 보통 인접 리스트로 표현한다.

n = 7
tree = [[] for _ in range(n + 1)]

edges = [
    (1, 2),
    (1, 3),
    (2, 4),
    (2, 5),
    (3, 6),
    (3, 7),
]

for a, b in edges:
    tree[a].append(b)
    tree[b].append(a)

# 루트를 1로 두고 생각해보면:
#
#        1
#      /   \
#     2     3
#    / \   / \
#   4  5  6  7


# --------------------------------------------------
# [5. parent / depth 구하기 - DFS]
# --------------------------------------------------
# 트리에서는 부모와 깊이를 구하는 것이 매우 중요하다.

parent = [0] * (n + 1)
depth = [-1] * (n + 1)

def dfs_tree(node, par):
    parent[node] = par

    for nxt in tree[node]:
        if nxt == par:
            continue
        depth[nxt] = depth[node] + 1
        dfs_tree(nxt, node)

depth[1] = 0
dfs_tree(1, 0)

# 결과 예시:
# parent[2] = 1
# parent[4] = 2
# depth[1] = 0
# depth[4] = 2


# --------------------------------------------------
# [6. parent / depth 구하기 - BFS]
# --------------------------------------------------
# BFS로도 쉽게 구할 수 있다.

def bfs_tree(root, tree):
    n = len(tree) - 1
    parent = [0] * (n + 1)
    depth = [-1] * (n + 1)

    q = deque([root])
    depth[root] = 0

    while q:
        node = q.popleft()

        for nxt in tree[node]:
            if depth[nxt] == -1:
                parent[nxt] = node
                depth[nxt] = depth[node] + 1
                q.append(nxt)

    return parent, depth

parent_bfs, depth_bfs = bfs_tree(1, tree)


# --------------------------------------------------
# [7. 트리 순회]
# --------------------------------------------------
# 트리는 DFS/BFS로 순회할 수 있다.
# 루트가 있는 트리라면 부모를 다시 타고 올라가지 않도록 주의해야 한다.

def preorder(node, par, tree, result):
    result.append(node)
    for nxt in tree[node]:
        if nxt != par:
            preorder(nxt, node, tree, result)

preorder_result = []
preorder(1, 0, tree, preorder_result)


# --------------------------------------------------
# [8. 서브트리 크기]
# --------------------------------------------------
# 어떤 노드를 루트로 하는 서브트리에 몇 개의 노드가 있는지 구하는 문제.

subtree_size = [0] * (n + 1)

def compute_subtree_size(node, par):
    subtree_size[node] = 1

    for nxt in tree[node]:
        if nxt == par:
            continue
        compute_subtree_size(nxt, node)
        subtree_size[node] += subtree_size[nxt]

compute_subtree_size(1, 0)

# 예:
# subtree_size[2] = 3 (2,4,5)
# subtree_size[1] = 7


# --------------------------------------------------
# [9. 두 노드의 공통 조상]
# --------------------------------------------------
# 공통 조상 = 두 노드의 조상 중 공통인 노드
# LCA = 그 중 가장 깊은(가장 가까운) 공통 조상
#
# 예:
# LCA(4, 5) = 2
# LCA(4, 6) = 1


# --------------------------------------------------
# [10. LCA - 단순 구현]
# --------------------------------------------------
# 가장 쉬운 방법:
# 1) 깊이를 맞춘다
# 2) 둘이 같아질 때까지 같이 위로 올린다

def lca_basic(a, b, parent, depth):
    # depth 맞추기
    while depth[a] > depth[b]:
        a = parent[a]
    while depth[b] > depth[a]:
        b = parent[b]

    # 동시에 올리기
    while a != b:
        a = parent[a]
        b = parent[b]

    return a

lca_4_5 = lca_basic(4, 5, parent, depth)   # 2
lca_4_6 = lca_basic(4, 6, parent, depth)   # 1

# 이 방식은 한 번 질의하는 데 O(height) 정도가 걸린다.


# --------------------------------------------------
# [11. 왜 LCA가 필요한가]
# --------------------------------------------------
# LCA는 아래 문제들로 자주 연결된다.
#
# - 두 노드 사이 거리
# - 트리 경로 문제
# - 공통 조상 찾기
# - 여러 쿼리 처리
#
# 예를 들어 두 노드 u, v 사이 거리:
# distance(u, v) = depth[u] + depth[v] - 2 * depth[lca(u, v)]


# --------------------------------------------------
# [12. 두 노드 사이 거리]
# --------------------------------------------------
def tree_distance(a, b, parent, depth):
    ancestor = lca_basic(a, b, parent, depth)
    return depth[a] + depth[b] - 2 * depth[ancestor]

dist_4_5 = tree_distance(4, 5, parent, depth)   # 2
dist_4_6 = tree_distance(4, 6, parent, depth)   # 4


# --------------------------------------------------
# [13. LCA 질의가 많으면 느려진다]
# --------------------------------------------------
# lca_basic은 쿼리 1개마다 O(N)까지 갈 수 있다.
# 질의가 많으면 비효율적이다.
#
# 그래서 binary lifting을 사용한다.


# --------------------------------------------------
# [14. Binary Lifting 개념]
# --------------------------------------------------
# parent[node]만 저장하지 않고
# up[k][node] = node의 2^k번째 조상
# 을 저장한다.
#
# 예:
# up[0][node] = 1칸 위 부모
# up[1][node] = 2칸 위 조상
# up[2][node] = 4칸 위 조상
# up[3][node] = 8칸 위 조상
#
# 이렇게 하면 노드를 빠르게 위로 점프할 수 있다.


# --------------------------------------------------
# [15. Binary Lifting 전처리]
# --------------------------------------------------
LOG = (n + 1).bit_length()

up = [[0] * (n + 1) for _ in range(LOG)]
depth2 = [-1] * (n + 1)

def dfs_lca(node, par):
    up[0][node] = par

    for k in range(1, LOG):
        up[k][node] = up[k - 1][up[k - 1][node]]

    for nxt in tree[node]:
        if nxt == par:
            continue
        depth2[nxt] = depth2[node] + 1
        dfs_lca(nxt, node)

depth2[1] = 0
dfs_lca(1, 0)


# --------------------------------------------------
# [16. 노드를 위로 올리기]
# --------------------------------------------------
# node를 dist만큼 위로 올린다.

def lift(node, dist):
    for k in range(LOG):
        if dist & (1 << k):
            node = up[k][node]
    return node

lift_example = lift(5, 2)   # 5 -> 2 -> 1


# --------------------------------------------------
# [17. LCA - Binary Lifting]
# --------------------------------------------------
def lca(a, b):
    # depth 맞추기
    if depth2[a] < depth2[b]:
        a, b = b, a

    diff = depth2[a] - depth2[b]
    a = lift(a, diff)

    if a == b:
        return a

    # 큰 점프부터 내려오며 공통 조상 바로 아래까지 맞춤
    for k in range(LOG - 1, -1, -1):
        if up[k][a] != up[k][b]:
            a = up[k][a]
            b = up[k][b]

    return up[0][a]

lca_fast_4_5 = lca(4, 5)   # 2
lca_fast_4_6 = lca(4, 6)   # 1


# --------------------------------------------------
# [18. Binary Lifting의 시간복잡도]
# --------------------------------------------------
# 전처리:
# O(N log N)
#
# LCA 한 번:
# O(log N)
#
# 질의가 많으면 매우 유리하다.


# --------------------------------------------------
# [19. k번째 조상]
# --------------------------------------------------
# Binary Lifting이 있으면 k번째 조상도 쉽게 구할 수 있다.

def kth_ancestor(node, k):
    return lift(node, k)

ancestor_of_5_1 = kth_ancestor(5, 1)   # 2
ancestor_of_5_2 = kth_ancestor(5, 2)   # 1


# --------------------------------------------------
# [20. LCA로 거리 구하기]
# --------------------------------------------------
def tree_distance_fast(a, b):
    ancestor = lca(a, b)
    return depth2[a] + depth2[b] - 2 * depth2[ancestor]

dist_fast_4_7 = tree_distance_fast(4, 7)   # 4


# --------------------------------------------------
# [21. 대표 문제 유형]
# --------------------------------------------------
# Tree / LCA는 아래 유형으로 자주 나온다.
#
# 1) 부모 찾기
#    - 각 노드의 부모
#
# 2) 깊이 구하기
#    - 루트 기준 depth
#
# 3) 서브트리 크기
#    - 하위 노드 수
#
# 4) 공통 조상
#    - LCA
#
# 5) 두 노드 사이 거리
#    - depth + LCA
#
# 6) k번째 조상
#    - binary lifting
#
# 7) 여러 개의 LCA 쿼리
#    - 전처리 후 빠른 응답


# --------------------------------------------------
# [22. 자주 하는 실수]
# --------------------------------------------------
# 1) 트리에서 부모로 다시 올라가는 간선을 막지 않음
#    -> 무한 재귀 / 중복 탐색
#
# 2) depth 초기화 누락
#
# 3) 루트의 parent를 어떻게 둘지 혼동
#    -> 보통 0 또는 자기 자신
#
# 4) LCA에서 depth를 먼저 맞추지 않음
#
# 5) binary lifting 전처리 인덱스 실수
#
# 6) up[k-1][up[k-1][node]] 계산 시 0 처리 주의
#
# 7) 1-index / 0-index 혼동
#
# 8) 트리인데 무방향 그래프처럼 부모 체크 없이 탐색
#
# 9) 질의 수가 많은데 lca_basic만 써서 시간초과


# --------------------------------------------------
# [23. 문제를 보고 Tree / LCA를 떠올리는 체크리스트]
# --------------------------------------------------
# 아래 질문 중 하나라도 "예"면 Tree / LCA 후보일 가능성이 높다.
#
# - 그래프가 트리인가?
# - 부모/자식 관계가 중요한가?
# - 깊이(depth)가 필요한가?
# - 두 노드의 공통 조상을 구해야 하는가?
# - 두 노드 사이 거리를 여러 번 구해야 하는가?
# - LCA 질의가 많아서 빠른 처리가 필요한가?


# --------------------------------------------------
# [24. 실전 템플릿 1 - parent / depth 구하기]
# --------------------------------------------------
def build_parent_depth(n, tree, root=1):
    parent = [0] * (n + 1)
    depth = [-1] * (n + 1)

    def dfs(node, par):
        parent[node] = par
        for nxt in tree[node]:
            if nxt == par:
                continue
            depth[nxt] = depth[node] + 1
            dfs(nxt, node)

    depth[root] = 0
    dfs(root, 0)
    return parent, depth


# --------------------------------------------------
# [25. 실전 템플릿 2 - LCA 기본]
# --------------------------------------------------
def lca_basic_template(a, b, parent, depth):
    while depth[a] > depth[b]:
        a = parent[a]
    while depth[b] > depth[a]:
        b = parent[b]

    while a != b:
        a = parent[a]
        b = parent[b]

    return a


# --------------------------------------------------
# [26. 실전 템플릿 3 - Binary Lifting 준비]
# --------------------------------------------------
def build_lca(n, tree, root=1):
    LOG = (n + 1).bit_length()
    up = [[0] * (n + 1) for _ in range(LOG)]
    depth = [-1] * (n + 1)

    def dfs(node, par):
        up[0][node] = par

        for k in range(1, LOG):
            up[k][node] = up[k - 1][up[k - 1][node]]

        for nxt in tree[node]:
            if nxt == par:
                continue
            depth[nxt] = depth[node] + 1
            dfs(nxt, node)

    depth[root] = 0
    dfs(root, 0)

    return up, depth, LOG


# --------------------------------------------------
# [27. 실전 템플릿 4 - Binary Lifting LCA]
# --------------------------------------------------
def lift_template(node, dist, up, LOG):
    for k in range(LOG):
        if dist & (1 << k):
            node = up[k][node]
    return node

def lca_template(a, b, up, depth, LOG):
    if depth[a] < depth[b]:
        a, b = b, a

    a = lift_template(a, depth[a] - depth[b], up, LOG)

    if a == b:
        return a

    for k in range(LOG - 1, -1, -1):
        if up[k][a] != up[k][b]:
            a = up[k][a]
            b = up[k][b]

    return up[0][a]


# --------------------------------------------------
# [28. 실전 템플릿 5 - 거리 계산]
# --------------------------------------------------
def tree_distance_template(a, b, up, depth, LOG):
    ancestor = lca_template(a, b, up, depth, LOG)
    return depth[a] + depth[b] - 2 * depth[ancestor]


# --------------------------------------------------
# [29. 예제 문제 감각]
# --------------------------------------------------
# 예제 1)
# 각 노드의 부모를 구하라
# -> DFS/BFS
#
# 예제 2)
# 특정 노드의 서브트리 크기를 구하라
# -> DFS
#
# 예제 3)
# 두 노드의 가장 가까운 공통 조상을 구하라
# -> LCA
#
# 예제 4)
# 두 노드 사이의 거리를 구하라
# -> depth + LCA
#
# 예제 5)
# 여러 개의 LCA 질의를 빠르게 처리하라
# -> binary lifting


# --------------------------------------------------
# [30. Tree / LCA와 다른 주제의 연결]
# --------------------------------------------------
# - BFS/DFS:
#   트리 탐색의 기본 도구
#
# - Shortest Path:
#   트리는 경로가 유일하므로 거리 계산이 단순해진다
#
# - Binary Search:
#   직접 연결은 적지만 depth 기반 조건 탐색 문제와 섞일 수 있다
#
# - Union-Find:
#   MST/트리 구성 이후 트리 질의 문제로 이어질 수 있다
#
# - 구현:
#   parent/depth 테이블 관리가 중요하다


# --------------------------------------------------
# [31. 한 줄 요약]
# --------------------------------------------------
# Tree / LCA = 트리에서 부모와 깊이를 관리하고,
# 두 노드의 공통 조상과 거리 등을 효율적으로 구하는 문제 유형


# --------------------------------------------------
# [32. 최소 암기 포인트]
# --------------------------------------------------
# 1) 트리:
#    연결 + 사이클 없음
#
# 2) 기본:
#    parent, depth
#
# 3) LCA 기본:
#    depth 맞추고 같이 올리기
#
# 4) 질의 많음:
#    binary lifting
#
# 5) 거리:
#    depth[a] + depth[b] - 2 * depth[lca]
#
# 6) 서브트리:
#    DFS로 크기 누적


# --------------------------------------------------
# [33. 다음 주제]
# --------------------------------------------------
# 다음 파일은 09_sqrt_bucket.py 로 이어진다.
# Square Root Decomposition / Bucket에서는
# 구간을 블록으로 나누는 아이디어, 쿼리 최적화,
# 버킷 기반 처리 등을 정리한다.


# --------------------------------------------------
# [참고]
# --------------------------------------------------
# 이 파일은 개념 정리용이다.
# 필요한 부분만 복붙해서 템플릿처럼 사용하면 된다.
# Tree 문제의 핵심은 결국 parent / depth를 정확히 잡고,
# 질의 수가 많으면 LCA를 최적화하는 것이다.

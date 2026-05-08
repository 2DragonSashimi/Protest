# 빙하 시뮬레이션 문제 정리

## 1. 문제를 보는 핵심 관점

이 문제는 처음부터 “빙하 객체” 중심으로 보면 복잡해진다.

가장 직관적인 관점은 다음이다.

```text
height grid가 실제 상태다.

gid, groups는 현재 height grid를 해석해서 붙인 라벨이다.
```

즉:

```python
height[y][x]
```

는 실제 바다/얼음 상태이고,

```python
gid[y][x]
groups[gid]
```

는 현재 얼음들이 어떤 빙하로 묶여 있는지를 설명하는 보조 정보이다.

빙하가 녹거나 이동하면 `height`가 바뀐다.  
그러면 기존 `gid`, `groups`는 더 이상 정확하지 않을 수 있다.

따라서 상태가 크게 바뀐 뒤에는 BFS로 다시 연결 컴포넌트를 찾아서 `gid`, `groups`를 새로 만든다.

---

## 2. 좌표계와 방향

문제의 좌표는 `(Y, X)` 순서이다.

```text
(0, 0): 좌측 상단
Y 증가: 아래쪽
X 증가: 오른쪽
```

방향은 다음과 같다.

```python
# 0: ↑, 1: →, 2: ↓, 3: ←
DY = [-1, 0, 1, 0]
DX = [0, 1, 0, -1]
```

예를 들어 어떤 얼음이 `(y, x)`에 있고 방향이 `d`라면, 이동 후 위치는 다음과 같다.

```python
ny = (y + DY[d]) % N
nx = (x + DX[d]) % N
```

`% N`을 쓰는 이유는 바다가 토러스 구조이기 때문이다.

즉:

```text
왼쪽 끝과 오른쪽 끝이 연결됨
위쪽 끝과 아래쪽 끝이 연결됨
```

---

## 3. 전체 변수 설명

### 3.1 `N_SIZE`

```python
N_SIZE = 0
```

전체 바다 크기이다.

보드는 `N_SIZE x N_SIZE`이다.

---

### 3.2 `height`

```python
height = []
```

현재 보드의 얼음 높이 정보이다.

```python
height[y][x]
```

의미:

```text
0이면 바다
1 이상이면 얼음 높이
```

이 문제에서 가장 중요한 실제 상태이다.

예를 들어:

```python
height[2][3] = 5
```

라면 `(2, 3)` 좌표에 높이 5짜리 얼음덩어리가 있다는 뜻이다.

---

### 3.3 `gid`

```python
gid = []
```

각 얼음 칸이 현재 어느 빙하 그룹에 속하는지 저장하는 grid이다.

```python
gid[y][x]
```

의미:

```text
height[y][x] == 0이면 -1
height[y][x] > 0이면 해당 칸이 속한 group id
```

예를 들어:

```python
gid[2][3] = 4
```

라면 `(2, 3)` 좌표의 얼음은 4번 빙하에 속한다는 뜻이다.

주의할 점:

```text
gid는 height를 보고 만든 라벨이다.
융해나 이동 후에는 다시 만들어야 한다.
```

---

### 3.4 `groups`

```python
groups = {}
```

각 빙하 group의 정보를 저장하는 딕셔너리이다.

구조는 다음과 같다.

```python
groups[g] = {
    "dir": direction,
    "area": area,
    "volume": volume,
    "pos": (pos_y, pos_x),
}
```

각 항목의 의미는 다음과 같다.

| key | 의미 |
|---|---|
| `"dir"` | 해당 빙하의 이동 방향 |
| `"area"` | 빙하를 구성하는 얼음 칸 개수 |
| `"volume"` | 빙하를 구성하는 얼음 높이의 합 |
| `"pos"` | 빙하의 위치. 가장 위쪽 행, 그중 가장 왼쪽 열 |

예를 들어:

```python
groups[2] = {
    "dir": 1,
    "area": 5,
    "volume": 17,
    "pos": (0, 3),
}
```

이면:

```text
2번 빙하는 오른쪽으로 이동하고,
면적은 5,
부피는 17,
위치는 (0, 3)
```

이라는 뜻이다.

---

### 3.5 `DY`, `DX`

```python
DY = [-1, 0, 1, 0]
DX = [0, 1, 0, -1]
```

방향 이동 배열이다.

| 방향 값 | 의미 | DY | DX |
|---|---|---|---|
| 0 | 위 | -1 | 0 |
| 1 | 오른쪽 | 0 | 1 |
| 2 | 아래 | 1 | 0 |
| 3 | 왼쪽 | 0 | -1 |

---

## 4. 전체 흐름

한 해가 지나면 다음 순서로 처리한다.

```text
1. 융해 전 상태 저장
2. 융해
3. 융해 후 빙하 재구성
4. 이동 전 group 정보 저장
5. 이동
6. 이동 후 병합 재구성
7. 결과 반환
```

코드 흐름은 다음과 같다.

```python
def oneYearLater():
    old_gid = copy(gid)
    old_groups = copy(groups)

    melt()

    gid, groups = rebuild_after_melt(old_gid, old_groups)

    pre_info = make_pre_info(groups)

    moved_height, moved_sources = move_only(height, gid, groups)

    height = moved_height

    gid, groups = rebuild_after_move(height, moved_sources, pre_info)

    return RESULT(height)
```

---

## 5. 공통 BFS 함수: `collect_components`

### 5.1 역할

```python
def collect_components(cur_height, source_grid=None):
```

이 함수는 현재 `cur_height` grid를 보고 연결된 얼음 덩어리들을 찾는다.

즉, 현재 상태에서 빙하들을 다시 찾는 함수이다.

이 함수의 핵심 역할은 다음과 같다.

```text
1. 현재 height에서 연결된 얼음 component를 찾는다.
2. 각 component의 area, volume, pos를 계산한다.
3. 각 cell에 새 gid를 붙인다.
4. source_grid가 있으면 component가 어디서 왔는지 sources에 모은다.
```

---

### 5.2 반환값

```python
return components, new_gid
```

#### `components`

각 빙하 component 정보를 담은 리스트이다.

```python
components = [
    {
        "area": area,
        "volume": volume,
        "pos": (pos_y, pos_x),
        "sources": sources,
    },
    ...
]
```

#### `new_gid`

새롭게 만들어진 group id grid이다.

```python
new_gid[y][x]
```

는 해당 칸이 새로 몇 번 group에 속하는지 나타낸다.

---

### 5.3 `source_grid`의 의미

`collect_components()`가 약간 어려워 보이는 이유는 `source_grid` 때문이다.

```python
source_grid=None
```

일 수도 있고, 상황에 따라 다른 정보를 담은 grid가 들어올 수도 있다.

#### init 단계

초기화 때는 `dir_grid`가 들어간다.

```python
dir_grid[y][x] = 방향
```

단, 모든 칸에 방향이 있는 것은 아니고, `mIceGroup`에서 주어진 대표 좌표에만 방향이 들어 있다.

이때 `sources`에는 해당 component의 초기 방향이 들어간다.

---

#### 융해 후

융해 후에는 `old_gid`가 들어간다.

```python
old_gid[y][x]
```

의미:

```text
이 cell은 융해 전 어떤 group이었는가?
```

융해로 빙하가 쪼개졌더라도, 새 조각은 원래 group의 방향을 상속해야 한다.

그래서 `old_gid`를 source로 사용한다.

---

#### 이동 후

이동 후에는 `moved_sources`가 들어간다.

```python
moved_sources[y][x] = {이 좌표에 도착한 이전 group id들}
```

의미:

```text
이 cell은 어떤 기존 빙하들이 이동해 온 결과인가?
```

이 정보는 병합 후 방향을 결정할 때 사용된다.

---

### 5.4 `sources`가 필요한 이유

각 component에는 다음 정보가 들어간다.

```python
"sources": sources
```

상황에 따라 의미가 다르다.

| 상황 | sources 의미 |
|---|---|
| init | 초기 대표 좌표에서 가져온 방향 |
| 융해 후 | 이 component가 융해 전 어떤 group에서 왔는지 |
| 이동 후 | 이 component에 병합된 이전 group들 |

즉, BFS 자체는 단순히 component를 찾지만,  
그 component의 방향을 어떻게 정할지는 `sources`를 이용해 나중에 결정한다.

---

## 6. 초기화: `init`

```python
def init(N, M, mIceBlock, mIceGroup):
```

### 6.1 역할

초기 상태를 설정한다.

```text
1. height 초기화
2. mIceGroup 정보를 dir_grid에 저장
3. collect_components()로 초기 빙하 찾기
4. groups 생성
```

---

### 6.2 `mIceBlock`

```python
height = [row[:] for row in mIceBlock]
```

`mIceBlock`은 초기 얼음 높이 grid이다.

그대로 `height`에 복사한다.

---

### 6.3 `mIceGroup`

문제에서 `mIceGroup`은 다음 순서로 주어진다.

```text
X, Y, 방향
```

주의해야 한다.

```python
x = mIceGroup[i][0]
y = mIceGroup[i][1]
d = mIceGroup[i][2]
```

grid 접근은 항상:

```python
height[y][x]
```

이다.

---

### 6.4 `dir_grid`

```python
dir_grid = [[-1] * N for _ in range(N)]
```

초기 빙하의 방향을 대표 좌표에만 표시하기 위한 grid이다.

```python
dir_grid[y][x] = d
```

이후 `collect_components(height, dir_grid)`를 호출하면, 각 초기 component 안에서 이 방향 정보를 찾을 수 있다.

---

## 7. 융해: `melt`

```python
def melt():
```

### 7.1 역할

상하좌우 중 하나라도 바다와 인접한 얼음의 높이를 1 감소시킨다.

높이가 0이 되면 자연스럽게 바다가 된다.

---

### 7.2 동시 처리

융해는 동시에 일어나야 한다.

따라서 바로바로 높이를 줄이면 안 된다.

잘못된 방식:

```python
for y in range(N):
    for x in range(N):
        if 바다와 인접:
            height[y][x] -= 1
```

이렇게 하면 앞에서 녹아서 0이 된 칸이 뒤쪽 칸의 융해 조건에 영향을 줄 수 있다.

올바른 방식:

```text
1. 먼저 녹을 칸들을 melt_cells에 저장
2. 모든 탐색이 끝난 뒤 한 번에 높이 감소
```

코드:

```python
melt_cells = []

for y in range(N_SIZE):
    for x in range(N_SIZE):
        if height[y][x] == 0:
            continue

        for d in range(4):
            ny = (y + DY[d]) % N_SIZE
            nx = (x + DX[d]) % N_SIZE

            if height[ny][nx] == 0:
                melt_cells.append((y, x))
                break

for y, x in melt_cells:
    height[y][x] -= 1
```

---

## 8. 융해 후 재구성: `rebuild_after_melt`

```python
def rebuild_after_melt(old_gid, old_groups):
```

### 8.1 왜 필요한가?

융해 후에는 하나의 빙하가 여러 개로 쪼개질 수 있다.

예를 들어:

```text
1 1 1
0 1 0
1 1 1
```

가운데 연결부가 녹으면 위쪽과 아래쪽이 분리될 수 있다.

그래서 융해 후에는 현재 `height`를 보고 BFS로 다시 빙하를 찾아야 한다.

---

### 8.2 방향 상속

문제 조건:

```text
빙하가 나누어지더라도 각 빙하의 이동 방향은 변하지 않는다.
```

따라서 새로 나뉜 component는 원래 group의 방향을 그대로 가져간다.

이를 위해 융해 전 `old_gid`와 `old_groups`를 저장해둔다.

```python
components, new_gid = collect_components(height, old_gid)
```

각 새 component의 `sources`에는 융해 전 group id가 들어 있다.

```python
old_group_id = next(iter(comp["sources"]))
direction = old_groups[old_group_id]["dir"]
```

---

## 9. 이동 전 정보 저장: `make_pre_info`

```python
def make_pre_info(cur_groups):
```

### 9.1 왜 필요한가?

이동 후 여러 빙하가 병합될 수 있다.

병합 후 방향은 다음 기준으로 정한다.

```text
1. 부피가 큰 빙하
2. 부피가 같으면 면적이 작은 빙하
3. 면적도 같으면 위치 Y가 작은 빙하
4. Y도 같으면 위치 X가 작은 빙하
```

중요한 점:

```text
비교 기준은 이동 후 상태가 아니라 이동 전 상태이다.
```

따라서 이동하기 전에 현재 group 정보를 저장해야 한다.

```python
pre_info[g] = {
    "dir": info["dir"],
    "area": info["area"],
    "volume": info["volume"],
    "pos": info["pos"],
}
```

---

## 10. 이동: `move_only`

```python
def move_only(cur_height, cur_gid, cur_groups):
```

### 10.1 역할

현재 모든 얼음 칸을 자신이 속한 group의 방향으로 한 칸 이동시킨다.

---

### 10.2 전체 grid를 훑는 이유

이 버전은 직관을 우선한 코드이므로 `groups[g]["cells"]`를 들고 다니지 않는다.

대신 전체 grid를 훑는다.

```python
for y in range(N):
    for x in range(N):
        if cur_height[y][x] == 0:
            continue

        g = cur_gid[y][x]
        d = cur_groups[g]["dir"]
```

이렇게 하면 각 얼음 칸이 어느 group에 속하는지 `gid`로 확인하고,  
그 group의 방향을 `groups`에서 가져올 수 있다.

---

### 10.3 이동 결과

이동 결과로 두 가지 grid를 만든다.

```python
moved_height
moved_sources
```

#### `moved_height`

```python
moved_height[ny][nx]
```

이동 후 해당 좌표에 실제로 남은 얼음 높이이다.

겹쳤을 경우 높이가 큰 얼음만 남는다.

```python
if h > moved_height[ny][nx]:
    moved_height[ny][nx] = h
```

#### `moved_sources`

```python
moved_sources[ny][nx]
```

해당 좌표에 도착한 기존 group id들의 set이다.

```python
moved_sources[ny][nx].add(g)
```

겹쳐서 낮은 얼음이 사라졌더라도, 그 group은 충돌에 참여한 것이므로 기록해야 한다.

---

## 11. 이동 후 재구성: `rebuild_after_move`

```python
def rebuild_after_move(moved_height, moved_sources, pre_info):
```

### 11.1 왜 필요한가?

이동 후에는 서로 다른 빙하가 다음 이유로 합쳐질 수 있다.

```text
1. 같은 좌표에 겹침
2. 상하좌우로 인접
```

따라서 이동 후 `moved_height`를 기준으로 다시 BFS를 돌려야 한다.

```python
components, new_gid = collect_components(moved_height, moved_sources)
```

---

### 11.2 병합 source

이때 각 component의 `sources`에는 병합에 참여한 이전 group id들이 들어 있다.

예를 들어:

```python
sources = {2, 5, 7}
```

이면 새 빙하는 이동 전 2번, 5번, 7번 빙하가 합쳐진 결과이다.

---

### 11.3 병합 후 방향 결정

방향은 `pre_info` 기준으로 정한다.

```python
best_src = min(
    sources,
    key=lambda src: (
        -pre_info[src]["volume"],
        pre_info[src]["area"],
        pre_info[src]["pos"][0],
        pre_info[src]["pos"][1],
    )
)
```

비교 기준 해석:

```text
-volume : 부피가 큰 것이 우선이므로 음수 사용
area    : 면적이 작은 것이 우선
pos_y   : Y가 작은 것이 우선
pos_x   : X가 작은 것이 우선
```

선택된 group의 방향을 새 group의 방향으로 사용한다.

```python
direction = pre_info[best_src]["dir"]
```

---

## 12. 1년 처리: `oneYearLater`

```python
def oneYearLater():
```

전체 흐름은 다음과 같다.

```text
1. 융해 전 gid/groups 저장
2. melt()
3. rebuild_after_melt()
4. 이동 전 pre_info 저장
5. move_only()
6. height = moved_height
7. rebuild_after_move()
8. 결과 반환
```

---

## 13. 전체 코드

```python
from typing import List
from collections import deque


class RESULT:
    def __init__(self, mHeights: List[List[int]]):
        self.heights = mHeights


N_SIZE = 0
height = []
gid = []
groups = {}

# 0: ↑, 1: →, 2: ↓, 3: ←
DY = [-1, 0, 1, 0]
DX = [0, 1, 0, -1]


def collect_components(cur_height, source_grid=None):
    """
    현재 height grid 기준으로 빙하 component들을 찾는다.

    반환:
        components: 각 빙하 정보 list
        new_gid: 각 cell의 새 group id

    component 정보:
        area
        volume
        pos
        sources

    source_grid 의미:
        init:
            dir_grid[y][x] = 방향
        융해 후:
            old_gid[y][x] = 융해 전 group id
        이동 후:
            moved_sources[y][x] = 이 좌표에 도착한 이전 group id set
    """
    N = len(cur_height)

    visited = [[False] * N for _ in range(N)]
    new_gid = [[-1] * N for _ in range(N)]
    components = []

    comp_id = 0

    for sy in range(N):
        for sx in range(N):
            if cur_height[sy][sx] == 0:
                continue

            if visited[sy][sx]:
                continue

            q = deque()
            q.append((sy, sx))
            visited[sy][sx] = True

            area = 0
            volume = 0
            pos_y, pos_x = sy, sx
            sources = set()

            while q:
                y, x = q.popleft()

                new_gid[y][x] = comp_id
                area += 1
                volume += cur_height[y][x]

                if y < pos_y or (y == pos_y and x < pos_x):
                    pos_y, pos_x = y, x

                if source_grid is not None:
                    src = source_grid[y][x]

                    if isinstance(src, set):
                        sources.update(src)
                    elif src != -1:
                        sources.add(src)

                for d in range(4):
                    ny = (y + DY[d]) % N
                    nx = (x + DX[d]) % N

                    if visited[ny][nx]:
                        continue

                    if cur_height[ny][nx] == 0:
                        continue

                    visited[ny][nx] = True
                    q.append((ny, nx))

            components.append({
                "area": area,
                "volume": volume,
                "pos": (pos_y, pos_x),
                "sources": sources,
            })

            comp_id += 1

    return components, new_gid


def init(N, M, mIceBlock, mIceGroup):
    global N_SIZE, height, gid, groups

    N_SIZE = N
    height = [row[:] for row in mIceBlock]

    # mIceGroup은 X, Y, 방향 순서
    dir_grid = [[-1] * N for _ in range(N)]

    for i in range(M):
        x = mIceGroup[i][0]
        y = mIceGroup[i][1]
        d = mIceGroup[i][2]

        dir_grid[y][x] = d

    components, gid = collect_components(height, dir_grid)

    groups = {}

    for g, comp in enumerate(components):
        direction = next(iter(comp["sources"]))

        groups[g] = {
            "dir": direction,
            "area": comp["area"],
            "volume": comp["volume"],
            "pos": comp["pos"],
        }


def melt():
    global height

    melt_cells = []

    for y in range(N_SIZE):
        for x in range(N_SIZE):
            if height[y][x] == 0:
                continue

            for d in range(4):
                ny = (y + DY[d]) % N_SIZE
                nx = (x + DX[d]) % N_SIZE

                if height[ny][nx] == 0:
                    melt_cells.append((y, x))
                    break

    for y, x in melt_cells:
        height[y][x] -= 1


def rebuild_after_melt(old_gid, old_groups):
    components, new_gid = collect_components(height, old_gid)

    new_groups = {}

    for g, comp in enumerate(components):
        old_group_id = next(iter(comp["sources"]))
        direction = old_groups[old_group_id]["dir"]

        new_groups[g] = {
            "dir": direction,
            "area": comp["area"],
            "volume": comp["volume"],
            "pos": comp["pos"],
        }

    return new_gid, new_groups


def make_pre_info(cur_groups):
    pre_info = {}

    for g, info in cur_groups.items():
        pre_info[g] = {
            "dir": info["dir"],
            "area": info["area"],
            "volume": info["volume"],
            "pos": info["pos"],
        }

    return pre_info


def move_only(cur_height, cur_gid, cur_groups):
    N = len(cur_height)

    moved_height = [[0] * N for _ in range(N)]
    moved_sources = [[set() for _ in range(N)] for _ in range(N)]

    for y in range(N):
        for x in range(N):
            if cur_height[y][x] == 0:
                continue

            g = cur_gid[y][x]
            d = cur_groups[g]["dir"]

            ny = (y + DY[d]) % N
            nx = (x + DX[d]) % N

            h = cur_height[y][x]

            if h > moved_height[ny][nx]:
                moved_height[ny][nx] = h

            moved_sources[ny][nx].add(g)

    return moved_height, moved_sources


def rebuild_after_move(moved_height, moved_sources, pre_info):
    components, new_gid = collect_components(moved_height, moved_sources)

    new_groups = {}

    for g, comp in enumerate(components):
        sources = comp["sources"]

        best_src = min(
            sources,
            key=lambda src: (
                -pre_info[src]["volume"],
                pre_info[src]["area"],
                pre_info[src]["pos"][0],
                pre_info[src]["pos"][1],
            )
        )

        direction = pre_info[best_src]["dir"]

        new_groups[g] = {
            "dir": direction,
            "area": comp["area"],
            "volume": comp["volume"],
            "pos": comp["pos"],
        }

    return new_gid, new_groups


def oneYearLater():
    global height, gid, groups

    old_gid = [row[:] for row in gid]
    old_groups = {}

    for g, info in groups.items():
        old_groups[g] = {
            "dir": info["dir"],
            "area": info["area"],
            "volume": info["volume"],
            "pos": info["pos"],
        }

    # a. 융해
    melt()

    # 융해 후 분리된 빙하 재구성
    gid, groups = rebuild_after_melt(old_gid, old_groups)

    # 이동 전 상태 저장
    pre_info = make_pre_info(groups)

    # b. 이동
    moved_height, moved_sources = move_only(height, gid, groups)

    # 이동 결과 반영
    height = moved_height

    # c. 병합
    gid, groups = rebuild_after_move(height, moved_sources, pre_info)

    return RESULT([row[:] for row in height])
```

---

## 14. 실수하기 쉬운 포인트

### 14.1 `mIceGroup` 좌표 순서

문제에서는 `X, Y, 방향` 순서로 준다.

```python
x = mIceGroup[i][0]
y = mIceGroup[i][1]
d = mIceGroup[i][2]
```

하지만 grid 접근은:

```python
height[y][x]
```

이다.

---

### 14.2 융해는 동시에 처리

녹을 칸을 먼저 모두 찾고, 그 다음 높이를 줄여야 한다.

---

### 14.3 융해 후 방향은 old_gid로 상속

새 component의 좌상단 좌표로 방향을 찾으면 안 된다.

융해 전에 어떤 group이었는지를 `old_gid`로 확인해야 한다.

---

### 14.4 이동 후 방향은 이동 전 상태 기준

병합 후 방향 결정은 이동 후 새 빙하의 부피/면적 기준이 아니다.

반드시 이동 전 `pre_info` 기준이다.

---

### 14.5 겹쳐서 사라진 얼음도 병합 source에 포함

같은 좌표로 여러 얼음이 이동했을 때, 높이가 낮은 얼음은 사라진다.

하지만 그 빙하는 충돌에 참여했으므로 `moved_sources`에는 반드시 기록해야 한다.

---

## 15. 핵심 결론

이 문제는 다음 관점으로 이해하면 된다.

```text
height는 실제 상태이다.
gid와 groups는 height를 보고 만든 라벨이다.
```

따라서 상태가 바뀌면 BFS로 라벨을 다시 붙인다.

```text
융해 후:
    쪼개질 수 있으므로 BFS
    방향은 old_gid로 상속

이동 후:
    합쳐질 수 있으므로 BFS
    방향은 moved_sources와 pre_info로 결정
```

처음에는 최적화보다 이 구조를 정확히 이해하는 것이 중요하다.

이 버전은 `cells`를 들고 다니지 않고 전체 grid를 훑기 때문에 직관적이다.

나중에 최적화가 필요하면 각 group에 `cells`를 저장해서 이동할 때 전체 grid를 훑지 않도록 바꿀 수 있다.
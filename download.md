# 빙하 시뮬레이션 문제 정리

## 1. 핵심 관점

이 문제는 처음부터 “빙하 객체” 중심으로 생각하면 복잡해진다.

가장 중요한 관점은 다음이다.

```text
height가 실제 상태다.

group_id_grid와 glacier_info는
현재 height를 보고 붙인 라벨이다.
```

즉:

```python
height[y][x]
```

는 실제 바다/얼음 상태이고,

```python
group_id_grid[y][x]
glacier_info[group_id]
```

는 현재 얼음들이 어떤 빙하로 묶여 있는지를 설명하는 보조 정보이다.

빙하가 녹거나 이동하면 `height`가 바뀐다.  
그러면 기존 `group_id_grid`, `glacier_info`는 더 이상 정확하지 않을 수 있다.

따라서 상태가 크게 바뀐 뒤에는 BFS로 다시 연결 컴포넌트를 찾아서 라벨을 다시 붙인다.

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

예를 들어 어떤 얼음이 `(y, x)`에 있고 이동 방향이 `move_dir`라면, 이동 후 위치는 다음과 같다.

```python
ny = (y + DY[move_dir]) % N
nx = (x + DX[move_dir]) % N
```

`% N`을 쓰는 이유는 바다가 토러스 구조이기 때문이다.

```text
왼쪽 끝과 오른쪽 끝이 연결됨
위쪽 끝과 아래쪽 끝이 연결됨
```

---

## 3. 주요 변수 설명

### 3.1 `N_SIZE`

```python
N_SIZE = 0
```

전체 바다 크기이다.

보드는 `N_SIZE x N_SIZE` 크기이다.

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

---

### 3.3 `group_id_grid`

```python
group_id_grid = []
```

각 얼음 칸이 현재 어느 빙하 그룹에 속하는지 저장하는 grid이다.

```python
group_id_grid[y][x]
```

의미:

```text
height[y][x] == 0이면 -1
height[y][x] > 0이면 해당 칸이 속한 group id
```

예를 들어:

```python
group_id_grid[2][3] = 4
```

이면 `(2, 3)` 좌표의 얼음은 4번 빙하에 속한다는 뜻이다.

주의:

```text
group_id_grid는 height를 보고 만든 라벨이다.
융해나 이동 후에는 다시 만들어야 한다.
```

---

### 3.4 `glacier_info`

```python
glacier_info = {}
```

각 빙하 group의 정보를 저장하는 딕셔너리이다.

구조는 다음과 같다.

```python
glacier_info[group_id] = {
    "move_dir": move_dir,
    "area": area,
    "volume": volume,
    "pos": (pos_y, pos_x),
}
```

각 항목의 의미는 다음과 같다.

| key | 의미 |
|---|---|
| `"move_dir"` | 해당 빙하의 이동 방향 |
| `"area"` | 빙하를 구성하는 얼음 칸 개수 |
| `"volume"` | 빙하를 구성하는 얼음 높이의 합 |
| `"pos"` | 빙하의 위치. 가장 위쪽 행, 그중 가장 왼쪽 열 |

예를 들어:

```python
glacier_info[2] = {
    "move_dir": 1,
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

## 4. 왜 BFS가 필요한가?

빙하는 “상하좌우로 연결된 얼음덩어리 묶음”이다.

따라서 현재 `height`를 보고:

```text
어떤 얼음들이 하나의 빙하인가?
```

를 찾으려면 BFS 또는 DFS가 필요하다.

이 코드에서는 BFS 역할을 명확하게 제한한다.

```text
BFS는 현재 height에서 연결된 component만 찾는다.
방향 결정은 BFS 밖에서 한다.
```

이렇게 하면 코드가 훨씬 직관적이다.

---

## 5. 순수 BFS 함수: `find_components`

### 5.1 역할

```python
def find_components(cur_height):
```

이 함수는 현재 `cur_height`를 보고 연결된 얼음 component들을 찾는다.

반환값은 다음 두 개이다.

```python
components, new_group_id_grid
```

### 5.2 `components`

각 빙하 component 정보를 담은 리스트이다.

```python
components = [
    {
        "cells": cells,
        "area": area,
        "volume": volume,
        "pos": (pos_y, pos_x),
    },
    ...
]
```

각 항목 의미:

| key | 의미 |
|---|---|
| `"cells"` | 이 component에 속한 좌표 목록 |
| `"area"` | 얼음 칸 개수 |
| `"volume"` | 얼음 높이 합 |
| `"pos"` | 가장 위쪽 행, 그중 가장 왼쪽 열 |

### 5.3 `new_group_id_grid`

새롭게 만들어진 group id grid이다.

```python
new_group_id_grid[y][x]
```

는 해당 칸이 새로 몇 번 group에 속하는지 나타낸다.

---

## 6. 전체 1년 흐름

한 해가 지나면 다음 순서로 처리한다.

```text
1. 융해 전 group_id_grid, glacier_info 저장
2. 융해
3. 융해 후 빙하 재구성
4. 이동 전 glacier_info 저장
5. 이동
6. 이동 후 병합 재구성
7. 결과 반환
```

코드 흐름은 다음과 같다.

```python
def oneYearLater():
    old_group_id_grid = copy(group_id_grid)
    old_glacier_info = copy(glacier_info)

    melt()

    group_id_grid, glacier_info = rebuild_after_melt(
        old_group_id_grid,
        old_glacier_info
    )

    before_move_info = copy(glacier_info)

    moved_height, moved_from = move_only(
        height,
        group_id_grid,
        glacier_info
    )

    height = moved_height

    group_id_grid, glacier_info = rebuild_after_move(
        height,
        moved_from,
        before_move_info
    )

    return RESULT(height)
```

---

## 7. 단계별 설명

## 7.1 초기화

초기 입력에는 두 가지가 있다.

```python
mIceBlock
mIceGroup
```

### `mIceBlock`

초기 얼음 높이 grid이다.

```python
height = [row[:] for row in mIceBlock]
```

---

### `mIceGroup`

각 빙하의 대표 좌표와 이동 방향을 알려준다.

주의할 점:

```text
mIceGroup은 X, Y, 방향 순서이다.
```

따라서 다음처럼 읽어야 한다.

```python
x = mIceGroup[i][0]
y = mIceGroup[i][1]
move_dir = mIceGroup[i][2]
```

하지만 grid 접근은 항상:

```python
height[y][x]
```

이다.

---

### `initial_dir_at`

초기 방향 정보를 대표 좌표에만 표시하기 위한 grid이다.

```python
initial_dir_at[y][x] = move_dir
```

초기 BFS로 component를 찾은 뒤, component 내부 cell 중 `initial_dir_at[y][x] != -1`인 좌표를 찾아 그 방향을 해당 빙하의 방향으로 사용한다.

---

## 7.2 융해: `melt`

융해 규칙:

```text
상하좌우 중 하나라도 바다와 인접한 얼음은 높이가 1 감소한다.
높이가 0이 되면 사라진다.
```

중요한 점은 융해가 동시에 일어난다는 것이다.

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
2. 탐색이 끝난 뒤 한 번에 높이 감소
```

---

## 7.3 융해 후 재구성: `rebuild_after_melt`

융해 후에는 하나의 빙하가 여러 조각으로 나뉠 수 있다.

예를 들어:

```text
1 1 1
0 1 0
1 1 1
```

가운데 연결부가 녹으면 위쪽과 아래쪽이 분리될 수 있다.

따라서 융해 후 현재 `height`를 보고 BFS로 다시 component를 찾아야 한다.

방향은 문제 조건에 따라 원래 방향을 상속한다.

```text
빙하가 나누어지더라도 각 빙하의 이동 방향은 변하지 않는다.
```

이를 위해 융해 전 상태를 저장한다.

```python
old_group_id_grid = [row[:] for row in group_id_grid]
old_glacier_info = copy_glacier_info(glacier_info)
```

융해 후 새 component의 아무 cell을 하나 본다.

```python
y, x = comp["cells"][0]
old_group_id = old_group_id_grid[y][x]
move_dir = old_glacier_info[old_group_id]["move_dir"]
```

왜 아무 cell이나 봐도 되나?

```text
융해로 나뉜 component는 원래 하나의 빙하에서 나온 조각이다.
따라서 같은 component 안의 cell들은 같은 old_group_id를 가진다.
```

---

## 7.4 이동 전 정보 저장: `before_move_info`

이동 후 여러 빙하가 병합될 수 있다.

병합 후 이동 방향은 다음 기준으로 정한다.

```text
1. 부피가 큰 빙하
2. 부피가 같으면 면적이 작은 빙하
3. 면적도 같으면 위치 Y가 작은 빙하
4. Y도 같으면 위치 X가 작은 빙하
```

중요한 점:

```text
이 비교는 이동 후 상태 기준이 아니라 이동 전 상태 기준이다.
```

따라서 이동하기 전에 현재 `glacier_info`를 저장한다.

```python
before_move_info = copy_glacier_info(glacier_info)
```

---

## 7.5 이동: `move_only`

이동은 현재 모든 얼음 cell을 훑으면서 처리한다.

```python
for y in range(N):
    for x in range(N):
        if cur_height[y][x] == 0:
            continue

        group_id = cur_group_id_grid[y][x]
        move_dir = cur_glacier_info[group_id]["move_dir"]

        ny = (y + DY[move_dir]) % N
        nx = (x + DX[move_dir]) % N
```

즉:

```text
이 칸이 속한 빙하 ID를 확인한다.
그 빙하의 move_dir을 가져온다.
그 방향으로 한 칸 이동한다.
```

---

### 이동 결과로 필요한 두 가지 grid

이동 후에는 두 가지 정보를 만든다.

```python
moved_height
moved_from
```

---

### `moved_height`

```python
moved_height[ny][nx]
```

이동 후 실제로 남은 얼음 높이이다.

여러 얼음이 같은 좌표로 이동하면 높이가 큰 얼음만 남는다.

```python
if ice_height > moved_height[ny][nx]:
    moved_height[ny][nx] = ice_height
```

---

### `moved_from`

```python
moved_from[ny][nx]
```

해당 좌표에 도착한 기존 group id들의 set이다.

```python
moved_from[ny][nx].add(group_id)
```

주의:

```text
겹쳐서 낮은 얼음이 사라졌더라도,
그 빙하는 충돌에 참여한 것이다.
따라서 moved_from에는 반드시 기록해야 한다.
```

이 정보는 병합 후 방향을 결정할 때 사용된다.

---

## 7.6 이동 후 재구성: `rebuild_after_move`

이동 후에는 서로 다른 빙하가 합쳐질 수 있다.

합쳐지는 조건:

```text
1. 같은 좌표에 겹침
2. 상하좌우로 인접
```

따라서 이동 후 `moved_height` 기준으로 BFS를 다시 돌려야 한다.

```python
components, new_group_id_grid = find_components(moved_height)
```

이후 각 새 component에 대해, 그 component가 어떤 이전 빙하들에서 왔는지 모은다.

```python
merged_from = set()

for y, x in comp["cells"]:
    merged_from.update(moved_from[y][x])
```

예를 들어:

```python
merged_from = {2, 5, 7}
```

이면 새 빙하는 이동 전 2번, 5번, 7번 빙하가 합쳐진 결과이다.

---

### 병합 후 방향 결정

병합 후 방향은 `before_move_info` 기준으로 정한다.

```python
best_old_group = min(
    merged_from,
    key=lambda old_group_id: (
        -before_move_info[old_group_id]["volume"],
        before_move_info[old_group_id]["area"],
        before_move_info[old_group_id]["pos"][0],
        before_move_info[old_group_id]["pos"][1],
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

선택된 group의 이동 방향을 새 빙하의 방향으로 사용한다.

```python
move_dir = before_move_info[best_old_group]["move_dir"]
```

---

## 8. 전체 코드

```python
from typing import List
from collections import deque


class RESULT:
    def __init__(self, mHeights: List[List[int]]):
        self.heights = mHeights


N_SIZE = 0
height = []
group_id_grid = []
glacier_info = {}

# 0: ↑, 1: →, 2: ↓, 3: ←
DY = [-1, 0, 1, 0]
DX = [0, 1, 0, -1]


def copy_glacier_info(src_info):
    copied = {}

    for group_id, info in src_info.items():
        copied[group_id] = {
            "move_dir": info["move_dir"],
            "area": info["area"],
            "volume": info["volume"],
            "pos": info["pos"],
        }

    return copied


def find_components(cur_height):
    """
    현재 height grid 기준으로 연결된 얼음 component들을 찾는다.

    이 함수는 방향을 결정하지 않는다.
    오직 현재 얼음 덩어리들의 cells, area, volume, pos만 찾는다.
    """
    N = len(cur_height)

    visited = [[False] * N for _ in range(N)]
    new_group_id_grid = [[-1] * N for _ in range(N)]
    components = []

    group_id = 0

    for sy in range(N):
        for sx in range(N):
            if cur_height[sy][sx] == 0:
                continue

            if visited[sy][sx]:
                continue

            q = deque()
            q.append((sy, sx))
            visited[sy][sx] = True

            cells = []
            area = 0
            volume = 0
            pos_y, pos_x = sy, sx

            while q:
                y, x = q.popleft()

                new_group_id_grid[y][x] = group_id
                cells.append((y, x))

                area += 1
                volume += cur_height[y][x]

                if y < pos_y or (y == pos_y and x < pos_x):
                    pos_y, pos_x = y, x

                for move_dir in range(4):
                    ny = (y + DY[move_dir]) % N
                    nx = (x + DX[move_dir]) % N

                    if visited[ny][nx]:
                        continue

                    if cur_height[ny][nx] == 0:
                        continue

                    visited[ny][nx] = True
                    q.append((ny, nx))

            components.append({
                "cells": cells,
                "area": area,
                "volume": volume,
                "pos": (pos_y, pos_x),
            })

            group_id += 1

    return components, new_group_id_grid


def init(N, M, mIceBlock, mIceGroup):
    global N_SIZE, height, group_id_grid, glacier_info

    N_SIZE = N
    height = [row[:] for row in mIceBlock]

    # mIceGroup은 X, Y, 방향 순서
    initial_dir_at = [[-1] * N for _ in range(N)]

    for i in range(M):
        x = mIceGroup[i][0]
        y = mIceGroup[i][1]
        move_dir = mIceGroup[i][2]

        initial_dir_at[y][x] = move_dir

    components, group_id_grid = find_components(height)

    glacier_info = {}

    for group_id, comp in enumerate(components):
        move_dir = -1

        for y, x in comp["cells"]:
            if initial_dir_at[y][x] != -1:
                move_dir = initial_dir_at[y][x]
                break

        glacier_info[group_id] = {
            "move_dir": move_dir,
            "area": comp["area"],
            "volume": comp["volume"],
            "pos": comp["pos"],
        }


def melt():
    """
    융해 처리.

    현재 height 기준으로 바다와 인접한 얼음들을 먼저 모두 찾고,
    그 뒤 한 번에 높이를 1 감소시킨다.
    """
    global height

    melt_cells = []

    for y in range(N_SIZE):
        for x in range(N_SIZE):
            if height[y][x] == 0:
                continue

            for move_dir in range(4):
                ny = (y + DY[move_dir]) % N_SIZE
                nx = (x + DX[move_dir]) % N_SIZE

                if height[ny][nx] == 0:
                    melt_cells.append((y, x))
                    break

    for y, x in melt_cells:
        height[y][x] -= 1


def rebuild_after_melt(old_group_id_grid, old_glacier_info):
    """
    융해 후 빙하를 다시 찾는다.

    융해로 나뉜 빙하는 원래 빙하의 방향을 그대로 상속한다.
    """
    components, new_group_id_grid = find_components(height)

    new_glacier_info = {}

    for group_id, comp in enumerate(components):
        y, x = comp["cells"][0]

        old_group_id = old_group_id_grid[y][x]
        move_dir = old_glacier_info[old_group_id]["move_dir"]

        new_glacier_info[group_id] = {
            "move_dir": move_dir,
            "area": comp["area"],
            "volume": comp["volume"],
            "pos": comp["pos"],
        }

    return new_group_id_grid, new_glacier_info


def move_only(cur_height, cur_group_id_grid, cur_glacier_info):
    """
    이동만 수행한다.

    각 얼음 cell은 자신이 속한 빙하의 move_dir 방향으로 한 칸 이동한다.
    """
    N = len(cur_height)

    moved_height = [[0] * N for _ in range(N)]
    moved_from = [[set() for _ in range(N)] for _ in range(N)]

    for y in range(N):
        for x in range(N):
            if cur_height[y][x] == 0:
                continue

            group_id = cur_group_id_grid[y][x]
            move_dir = cur_glacier_info[group_id]["move_dir"]

            ny = (y + DY[move_dir]) % N
            nx = (x + DX[move_dir]) % N

            ice_height = cur_height[y][x]

            if ice_height > moved_height[ny][nx]:
                moved_height[ny][nx] = ice_height

            moved_from[ny][nx].add(group_id)

    return moved_height, moved_from


def rebuild_after_move(moved_height, moved_from, before_move_info):
    """
    이동 후 병합된 빙하를 다시 찾는다.

    병합 후 방향은 이동 전 before_move_info 기준으로 결정한다.
    """
    components, new_group_id_grid = find_components(moved_height)

    new_glacier_info = {}

    for group_id, comp in enumerate(components):
        merged_from = set()

        for y, x in comp["cells"]:
            merged_from.update(moved_from[y][x])

        best_old_group = min(
            merged_from,
            key=lambda old_group_id: (
                -before_move_info[old_group_id]["volume"],
                before_move_info[old_group_id]["area"],
                before_move_info[old_group_id]["pos"][0],
                before_move_info[old_group_id]["pos"][1],
            )
        )

        move_dir = before_move_info[best_old_group]["move_dir"]

        new_glacier_info[group_id] = {
            "move_dir": move_dir,
            "area": comp["area"],
            "volume": comp["volume"],
            "pos": comp["pos"],
        }

    return new_group_id_grid, new_glacier_info


def oneYearLater():
    global height, group_id_grid, glacier_info

    # 1. 융해 전 상태 저장
    old_group_id_grid = [row[:] for row in group_id_grid]
    old_glacier_info = copy_glacier_info(glacier_info)

    # 2. 융해
    melt()

    # 3. 융해 후 분리된 빙하 재구성
    group_id_grid, glacier_info = rebuild_after_melt(
        old_group_id_grid,
        old_glacier_info
    )

    # 4. 이동 전 상태 저장
    before_move_info = copy_glacier_info(glacier_info)

    # 5. 이동
    moved_height, moved_from = move_only(
        height,
        group_id_grid,
        glacier_info
    )

    # 6. 이동 결과 반영
    height = moved_height

    # 7. 이동 후 병합된 빙하 재구성
    group_id_grid, glacier_info = rebuild_after_move(
        height,
        moved_from,
        before_move_info
    )

    return RESULT([row[:] for row in height])
```

---

## 9. 실수하기 쉬운 포인트

### 9.1 `mIceGroup` 좌표 순서

문제에서는 `X, Y, 방향` 순서로 준다.

```python
x = mIceGroup[i][0]
y = mIceGroup[i][1]
move_dir = mIceGroup[i][2]
```

하지만 grid 접근은:

```python
height[y][x]
```

이다.

---

### 9.2 융해는 동시에 처리

녹을 칸을 먼저 모두 찾고, 그 다음 높이를 줄여야 한다.

---

### 9.3 융해 후 방향은 old group에서 상속

새 component의 위치나 좌상단 좌표로 방향을 찾으면 안 된다.

융해 전에 어떤 group이었는지를 `old_group_id_grid`로 확인해야 한다.

---

### 9.4 이동 후 방향은 이동 전 상태 기준

병합 후 방향 결정은 이동 후 새 빙하의 부피/면적 기준이 아니다.

반드시 이동 전 `before_move_info` 기준이다.

---

### 9.5 겹쳐서 사라진 얼음도 병합에 참여

같은 좌표로 여러 얼음이 이동했을 때, 높이가 낮은 얼음은 사라진다.

하지만 그 빙하는 충돌에 참여했으므로 `moved_from`에는 반드시 기록해야 한다.

---

### 9.6 BFS는 방향을 결정하지 않는다

이 코드에서 `find_components()`는 순수하게 component만 찾는다.

```text
cells
area
volume
pos
```

만 계산한다.

방향 결정은 다음 함수들이 담당한다.

```text
init:
    initial_dir_at에서 방향 결정

rebuild_after_melt:
    old_group_id_grid로 방향 상속

rebuild_after_move:
    moved_from과 before_move_info로 병합 방향 결정
```

---

## 10. 핵심 결론

이 문제는 다음 관점으로 이해하면 된다.

```text
height는 실제 상태이다.
group_id_grid와 glacier_info는 height를 보고 만든 라벨이다.
```

상태가 바뀌면 BFS로 라벨을 다시 붙인다.

```text
융해 후:
    쪼개질 수 있으므로 BFS
    방향은 old_group_id_grid로 상속

이동 후:
    합쳐질 수 있으므로 BFS
    방향은 moved_from과 before_move_info로 결정
```

처음에는 최적화보다 이 구조를 정확히 이해하는 것이 중요하다.

이 버전은 이동할 때 전체 grid를 훑기 때문에 직관적이다.

나중에 최적화가 필요하면 각 group에 `cells`를 저장해서 이동할 때 전체 grid를 훑지 않도록 바꿀 수 있다.
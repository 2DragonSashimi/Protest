# Glacier Simulation 문제 정리

## 1. 문제 개요

`N x N` 크기의 바다가 주어진다.

각 좌표에는 최대 1개의 얼음덩어리가 존재할 수 있고, 각 얼음덩어리는 `높이`를 가진다.

상하좌우로 인접한 얼음덩어리들의 연결 컴포넌트를 **빙하**라고 한다.

빙하의 주요 정보는 다음과 같다.

| 항목 | 의미 |
|---|---|
| 면적 | 빙하를 구성하는 얼음덩어리 개수 |
| 부피 | 빙하를 구성하는 얼음덩어리 높이의 합 |
| 위치 | 빙하에서 가장 위쪽 행, 그중 가장 왼쪽 열에 있는 얼음덩어리 좌표 |
| 이동 방향 | 0: 위, 1: 오른쪽, 2: 아래, 3: 왼쪽 |

좌표는 `(Y, X)` 순서로 표현한다.

단, `mIceGroup`에서 주어지는 좌표는 `(X, Y, 방향)` 순서이므로 주의해야 한다.

바다는 토러스 구조이다.

즉, 왼쪽 끝과 오른쪽 끝이 연결되어 있고, 위쪽 끝과 아래쪽 끝도 연결되어 있다.

예를 들어:

```text
(0, 0)의 왼쪽 = (0, N-1)
(0, 0)의 위쪽 = (N-1, 0)
```

---

## 2. 매년 일어나는 과정

빙하는 매년 다음 3단계를 순서대로 거친다.

```text
1. 융해
2. 이동
3. 병합
```

---

## 3. 융해

빙하를 구성하는 얼음덩어리 중, 상하좌우 중 하나라도 바다와 인접한 얼음덩어리는 높이가 1 감소한다.

높이가 0이 되면 해당 얼음덩어리는 사라진다.

중요한 점은 **융해는 동시에 일어난다**는 것이다.

잘못된 방식:

```python
for y in range(N):
    for x in range(N):
        if 바다와 인접:
            height[y][x] -= 1
```

이렇게 하면 앞에서 녹아 사라진 얼음이 뒤쪽 얼음의 융해 조건에 영향을 줄 수 있다.

올바른 방식:

```text
1. 현재 상태 기준으로 녹을 얼음들을 먼저 전부 찾는다.
2. 찾은 얼음들의 높이를 한 번에 감소시킨다.
3. 높이가 0이 된 얼음은 제거한다.
```

---

## 4. 융해 후 빙하 분리

융해에 의해 하나의 빙하가 여러 개의 빙하로 나뉠 수 있다.

예를 들어 하나의 빙하가 다음과 같다고 하자.

```text
1 1 1
0 1 0
1 1 1
```

가운데 연결부가 녹아 사라지면 위쪽과 아래쪽이 분리될 수 있다.

따라서 융해 후에는 반드시 BFS/DFS로 다시 연결 컴포넌트를 찾아야 한다.

문제에서 중요한 조건은 다음과 같다.

```text
빙하가 나누어지더라도 각 빙하의 이동 방향은 변하지 않는다.
```

즉, 융해로 하나의 빙하가 여러 조각으로 나뉘어도, 새로 생긴 조각들은 원래 빙하의 방향을 그대로 상속한다.

이를 위해 융해 전에 각 cell의 `old_gid`를 저장해두고, 융해 후 살아남은 cell의 `old_gid`를 이용해 방향을 상속한다.

---

## 5. 이동

모든 빙하는 동시에 한 칸 이동한다.

방향은 다음과 같다.

```python
# 0: 위, 1: 오른쪽, 2: 아래, 3: 왼쪽
DY = [-1, 0, 1, 0]
DX = [0, 1, 0, -1]
```

토러스 구조이므로 좌표 이동은 modulo 연산으로 처리한다.

```python
ny = (y + DY[d]) % N
nx = (x + DX[d]) % N
```

이동도 동시에 일어나야 하므로 기존 grid를 직접 수정하면 안 된다.

반드시 새로운 배열을 만들어 이동 결과를 저장해야 한다.

---

## 6. 이동 후 겹침 처리

서로 다른 얼음덩어리가 같은 좌표로 이동할 수 있다.

이 경우 해당 좌표에는 높이가 더 큰 얼음덩어리만 남는다.

```text
같은 좌표로 여러 얼음이 이동
→ 가장 높은 얼음만 남김
```

하지만 높이가 낮아서 사라진 얼음도 충돌에는 참여한 것이다.

병합 후 이동 방향은 충돌/인접에 참여한 빙하들의 이동 전 상태를 기준으로 결정되므로, 해당 좌표에 도착한 모든 빙하 ID를 기록해야 한다.

따라서 이동 후에는 두 가지 정보를 관리한다.

```python
moved_height[y][x]   # 해당 좌표에 남은 얼음 높이
moved_sources[y][x]  # 해당 좌표에 도착한 빙하 ID 목록
```

---

## 7. 병합

이동 후 서로 다른 빙하가 다음 중 하나를 만족하면 하나의 빙하가 된다.

```text
1. 같은 좌표에 겹침
2. 상하좌우로 인접
```

구현에서는 이동 후 `moved_height` 기준으로 다시 BFS를 수행하면 된다.

BFS로 하나의 연결 컴포넌트를 찾고, 그 컴포넌트 안에 포함된 `moved_sources`들을 모두 모으면 병합에 참여한 빙하들을 알 수 있다.

---

## 8. 병합 후 이동 방향 결정

병합된 빙하의 이동 방향은 병합에 참여한 빙하들의 **이동 전 상태**를 비교하여 결정한다.

비교 기준은 다음 순서이다.

```text
1. 부피가 큰 빙하
2. 부피가 같으면 면적이 작은 빙하
3. 면적이 같으면 위치의 Y 좌표가 작은 빙하
4. Y 좌표도 같으면 위치의 X 좌표가 작은 빙하
```

주의할 점은, 병합 후 새로 만들어진 빙하의 부피/면적/위치를 기준으로 방향을 정하는 것이 아니라는 것이다.

반드시 **이동 직전의 각 빙하 상태**를 저장해두고 비교해야 한다.

```python
pre_info[gid] = (
    volume,
    area,
    pos_y,
    pos_x,
    direction
)
```

비교 key는 다음과 같이 만들 수 있다.

```python
key = (-volume, area, pos_y, pos_x)
```

`volume`은 클수록 우선순위가 높기 때문에 `-volume`을 사용한다.

---

## 9. 왜 grid 중심으로 구현하는가?

처음에는 `IceBlock` 또는 `Glacier` 객체를 만들고, 각 빙하의 member cell들을 계속 들고 가는 방식을 생각할 수 있다.

하지만 이 문제에서는 매년 다음 일이 반복된다.

```text
1. 융해로 빙하가 분리됨
2. 이동으로 모든 좌표가 바뀜
3. 충돌/인접으로 빙하가 병합됨
```

따라서 객체 중심으로 관리하더라도, 분리와 병합을 판정하려면 결국 grid 위에서 BFS를 해야 한다.

그래서 이 문제는 grid 중심으로 관리하는 것이 가장 안전하다.

사용한 상태는 다음과 같다.

```python
height[y][x]  # 현재 얼음 높이
gid[y][x]     # 현재 해당 칸이 속한 빙하 ID
groups[gid]   # 해당 빙하의 방향, 면적, 부피, 위치, cell 목록
```

---

## 10. 전체 알고리즘 흐름

`oneYearLater()`는 다음 순서로 동작한다.

```text
1. 현재 gid와 group 방향을 저장한다.
2. 융해를 수행한다.
3. 융해 후 BFS로 빙하를 재구성한다.
   - 방향은 old_gid를 통해 상속한다.
4. 이동 전 group 정보를 저장한다.
   - 병합 후 방향 결정에 사용한다.
5. 모든 빙하를 동시에 이동한다.
   - 같은 좌표에 겹치면 높이가 큰 얼음만 남긴다.
   - 해당 좌표에 도착한 모든 source group id를 기록한다.
6. 이동 후 BFS로 병합된 빙하를 재구성한다.
   - component 안의 source group id들을 모은다.
   - pre_info 기준으로 새 방향을 결정한다.
7. 최종 height grid를 RESULT로 반환한다.
```

---

## 11. 최종 코드

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


def _collect_component(sy, sx, visited, new_gid, comp_id):
    global N_SIZE, height

    q = deque()
    q.append((sy, sx))
    visited[sy][sx] = True

    cells = []
    area = 0
    volume = 0
    pos_y, pos_x = sy, sx

    while q:
        y, x = q.popleft()

        new_gid[y][x] = comp_id
        cells.append((y, x))

        area += 1
        volume += height[y][x]

        if y < pos_y or (y == pos_y and x < pos_x):
            pos_y, pos_x = y, x

        for k in range(4):
            ny = (y + DY[k]) % N_SIZE
            nx = (x + DX[k]) % N_SIZE

            if visited[ny][nx]:
                continue

            if height[ny][nx] == 0:
                continue

            visited[ny][nx] = True
            q.append((ny, nx))

    return cells, area, volume, pos_y, pos_x


def init(N, M, mIceBlock, mIceGroup):
    global N_SIZE, height, gid, groups

    N_SIZE = N
    height = [mIceBlock[y][:] for y in range(N)]
    gid = [[-1] * N for _ in range(N)]
    groups = {}

    visited = [[False] * N for _ in range(N)]
    comp_id = 0

    for i in range(M):
        # mIceGroup은 X, Y, 방향 순서로 주어진다.
        x = mIceGroup[i][0]
        y = mIceGroup[i][1]
        d = mIceGroup[i][2]

        if height[y][x] == 0:
            continue

        if visited[y][x]:
            continue

        cells, area, volume, py, px = _collect_component(
            y, x, visited, gid, comp_id
        )

        groups[comp_id] = {
            "dir": d,
            "area": area,
            "volume": volume,
            "pos": (py, px),
            "cells": cells,
        }

        comp_id += 1


def _melt():
    global N_SIZE, height, gid

    melt_cells = []

    # 동시 융해 처리를 위해 먼저 녹을 칸을 전부 찾는다.
    for y in range(N_SIZE):
        for x in range(N_SIZE):
            if height[y][x] == 0:
                continue

            for k in range(4):
                ny = (y + DY[k]) % N_SIZE
                nx = (x + DX[k]) % N_SIZE

                if height[ny][nx] == 0:
                    melt_cells.append((y, x))
                    break

    # 찾은 칸들을 한 번에 감소시킨다.
    for y, x in melt_cells:
        height[y][x] -= 1

        if height[y][x] == 0:
            gid[y][x] = -1


def _rebuild_after_melt(old_gid, old_dir):
    global N_SIZE, height

    new_gid = [[-1] * N_SIZE for _ in range(N_SIZE)]
    new_groups = {}
    visited = [[False] * N_SIZE for _ in range(N_SIZE)]

    comp_id = 0

    for y in range(N_SIZE):
        for x in range(N_SIZE):
            if height[y][x] == 0:
                continue

            if visited[y][x]:
                continue

            # 융해 후 살아남은 cell은 융해 전 어떤 빙하에 속했는지 알고 있다.
            # 분리된 조각은 원래 빙하의 방향을 그대로 상속한다.
            src_gid = old_gid[y][x]
            d = old_dir[src_gid]

            cells, area, volume, py, px = _collect_component(
                y, x, visited, new_gid, comp_id
            )

            new_groups[comp_id] = {
                "dir": d,
                "area": area,
                "volume": volume,
                "pos": (py, px),
                "cells": cells,
            }

            comp_id += 1

    return new_gid, new_groups


def _move_and_merge():
    global N_SIZE, height, gid, groups

    # 병합 후 방향 결정은 이동 전 상태 기준이므로 미리 저장한다.
    pre_info = {}

    for g, info in groups.items():
        pre_info[g] = (
            info["volume"],
            info["area"],
            info["pos"][0],
            info["pos"][1],
            info["dir"],
        )

    moved_height = [[0] * N_SIZE for _ in range(N_SIZE)]
    moved_sources = [[[] for _ in range(N_SIZE)] for _ in range(N_SIZE)]

    # 모든 빙하를 동시에 이동시킨다.
    for g, info in groups.items():
        d = info["dir"]

        for y, x in info["cells"]:
            ny = (y + DY[d]) % N_SIZE
            nx = (x + DX[d]) % N_SIZE

            h = height[y][x]

            # 같은 좌표로 겹치면 높이가 큰 얼음만 남긴다.
            if h > moved_height[ny][nx]:
                moved_height[ny][nx] = h

            # 해당 좌표에 도착한 모든 빙하를 기록한다.
            # 낮은 얼음이 사라져도 충돌에 참여했으므로 source로 남겨야 한다.
            moved_sources[ny][nx].append(g)

    height = moved_height

    # 이동 후 겹침/인접에 의해 병합된 빙하를 BFS로 다시 찾는다.
    new_gid = [[-1] * N_SIZE for _ in range(N_SIZE)]
    new_groups = {}
    visited = [[False] * N_SIZE for _ in range(N_SIZE)]

    comp_id = 0

    for sy in range(N_SIZE):
        for sx in range(N_SIZE):
            if height[sy][sx] == 0:
                continue

            if visited[sy][sx]:
                continue

            q = deque()
            q.append((sy, sx))
            visited[sy][sx] = True

            cells = []
            sources = set()

            area = 0
            volume = 0
            pos_y, pos_x = sy, sx

            while q:
                y, x = q.popleft()

                new_gid[y][x] = comp_id
                cells.append((y, x))

                area += 1
                volume += height[y][x]

                sources.update(moved_sources[y][x])

                if y < pos_y or (y == pos_y and x < pos_x):
                    pos_y, pos_x = y, x

                for k in range(4):
                    ny = (y + DY[k]) % N_SIZE
                    nx = (x + DX[k]) % N_SIZE

                    if visited[ny][nx]:
                        continue

                    if height[ny][nx] == 0:
                        continue

                    visited[ny][nx] = True
                    q.append((ny, nx))

            # 병합 후 방향 결정:
            # 1. 부피가 큰 빙하
            # 2. 부피가 같으면 면적이 작은 빙하
            # 3. 면적이 같으면 위치 Y가 작은 빙하
            # 4. Y가 같으면 위치 X가 작은 빙하
            best_src = min(
                sources,
                key=lambda src: (
                    -pre_info[src][0],
                    pre_info[src][1],
                    pre_info[src][2],
                    pre_info[src][3],
                ),
            )

            new_dir = pre_info[best_src][4]

            new_groups[comp_id] = {
                "dir": new_dir,
                "area": area,
                "volume": volume,
                "pos": (pos_y, pos_x),
                "cells": cells,
            }

            comp_id += 1

    gid = new_gid
    groups = new_groups


def oneYearLater():
    global height, gid, groups

    # 융해 후 분리된 빙하의 방향 상속을 위해 이전 상태를 저장한다.
    old_gid = [row[:] for row in gid]
    old_dir = {}

    for g, info in groups.items():
        old_dir[g] = info["dir"]

    # 1. 융해
    _melt()

    # 2. 융해 후 분리된 빙하 재구성
    gid, groups = _rebuild_after_melt(old_gid, old_dir)

    # 3. 이동 + 병합
    _move_and_merge()

    return RESULT([row[:] for row in height])
```

---

## 12. 실수하기 쉬운 포인트

### 12.1 `mIceGroup` 좌표 순서

문제에서 `mIceGroup`은 다음 순서이다.

```text
X, Y, 방향
```

하지만 grid 접근은 다음 순서로 한다.

```python
height[y][x]
```

따라서 init에서는 반드시 다음처럼 받아야 한다.

```python
x = mIceGroup[i][0]
y = mIceGroup[i][1]
d = mIceGroup[i][2]
```

---

### 12.2 융해는 동시 처리

융해 도중 바로바로 height를 줄이면 안 된다.

반드시 먼저 녹을 cell 목록을 만들고, 그 다음에 한 번에 감소시켜야 한다.

---

### 12.3 융해 후 방향은 좌상단 좌표로 찾으면 안 됨

융해 후 빙하가 분리되면 새 빙하의 좌상단 좌표는 기존 빙하의 좌상단 좌표와 달라질 수 있다.

따라서 방향은 좌상단 좌표가 아니라 살아남은 cell의 `old_gid`를 통해 상속해야 한다.

---

### 12.4 병합 후 방향은 이동 후 상태 기준이 아님

병합 후 방향 결정은 반드시 이동 전 상태 기준이다.

이동 후 합쳐진 빙하의 부피/면적/위치로 방향을 정하면 틀린다.

반드시 이동 직전의 `pre_info`를 저장해야 한다.

---

### 12.5 겹쳐서 사라진 빙하도 병합 방향 후보에 포함해야 함

같은 좌표에 여러 얼음이 도착했을 때, 높이가 작은 얼음은 사라진다.

하지만 그 빙하는 충돌에 참여한 것이므로 병합 방향 결정 후보에는 포함되어야 한다.

그래서 `moved_sources[y][x]`에 해당 좌표로 도착한 모든 빙하 ID를 기록한다.

---

## 13. 시간복잡도

`N <= 100`이므로 전체 grid 크기는 최대 10,000이다.

1년 처리에서 grid 전체 순회와 BFS가 몇 번 수행된다.

따라서 1년 처리의 시간복잡도는 대략 다음과 같다.

```text
O(N^2)
```

빙하 개수 `M`이 최대 5,000이어도, 결국 실제 cell 수는 최대 10,000이므로 grid 중심 구현이 충분히 가능하다.

---

## 14. 핵심 결론

이 문제는 빙하 객체 중심으로 member를 계속 들고 가기보다, grid 중심으로 매년 상태를 재구성하는 편이 안전하다.

핵심은 다음 두 가지이다.

```text
1. 융해 후 분리된 빙하는 old_gid를 통해 방향을 상속한다.
2. 이동 후 병합된 빙하는 pre_info, 즉 이동 전 상태 기준으로 방향을 결정한다.
```

이 두 가지를 지키면 전체 시뮬레이션 구조가 안정적으로 정리된다.

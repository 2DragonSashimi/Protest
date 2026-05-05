# 8x8 보석 교환 게임 시뮬레이션 문제 정리

## 1. 문제 개요

`8 x 8` 크기의 보드가 있다.

좌표계는 다음과 같다.

```text
좌측 하단 = (0, 0)
좌표 표기 = (Y, X)
```

즉, `Y`가 커질수록 위쪽이고, `X`가 커질수록 오른쪽이다.

플레이어는 매 턴 하나의 기준 좌표를 선택하고, 그 좌표의 보석을 다음 중 하나와 교환한다.

```text
1. 오른쪽 인접 보석
2. 위쪽 인접 보석
```

교환 후 가로나 세로 방향으로 같은 보석이 3개 이상 연속되면 해당 보석들이 삭제되고 점수를 얻는다.

삭제 후 빈 공간은 위에서 내려오는 예비 보석으로 채운다.

보석을 채운 뒤 다시 3개 이상 연속되는 보석이 생기면 삭제되고 추가 점수를 얻는다.

이 과정은 더 이상 삭제될 보석이 없을 때까지 반복된다.

---

## 2. 보석과 예비 보석

보석 종류는 6가지이다.

```text
1 ~ 6
```

초기 보드는 비어 있다.

`init(N, mJewels)`에서 예비 보석이 `N`줄 주어진다.

각 줄에는 8개의 보석이 있다.

예비 보석은 index가 낮은 순서부터 차례대로 보드에 공급된다.

구현에서는 column별 공급 포인터를 둔다.

```python
supply_idx[x]
```

`x`열에 다음으로 들어올 예비 보석의 row index이다.

예를 들어 `x`열의 빈칸을 채울 때:

```python
board[y][x] = supply[supply_idx[x]][x]
supply_idx[x] += 1
```

처럼 사용한다.

---

## 3. 점수 규칙

같은 보석이 연속된 길이에 따라 점수가 정해진다.

| 연속 길이 | 점수 |
|---|---|
| 3개 | 1점 |
| 4개 | 4점 |
| 5개 이상 | 9점 |

가로와 세로에서 동시에 삭제되는 줄이 여러 개 있으면 점수를 모두 합산한다.

주의할 점:

```text
겹치는 cell은 한 번만 삭제된다.
하지만 점수는 줄 단위로 각각 합산된다.
```

예를 들어 십자 모양으로 가로 3개와 세로 3개가 동시에 만들어졌다면:

```text
가로 3개 = 1점
세로 3개 = 1점
총점 = 2점
```

겹치는 가운데 보석은 한 번만 삭제된다.

---

## 4. 매 턴 진행 과정

매 턴은 다음 3단계로 진행된다.

```text
1. 보드를 준비 상태로 만든다.
2. 최적의 교환 위치를 선택하고 교환한다.
3. 삭제, 보충, 연쇄 삭제를 처리한다.
```

---

## 5. 준비 상태

보드가 준비 상태가 되려면 다음 3가지 조건을 만족해야 한다.

```text
1. 보드 내 빈 공간이 없어야 한다.
2. 같은 보석이 3개 이상 연속되는 경우가 없어야 한다.
3. 인접한 2개의 보석을 교환하여 점수를 얻을 수 있는 방법이 최소 1가지 있어야 한다.
```

준비 상태를 만드는 과정은 다음과 같다.

```text
1. 빈칸을 예비 보석으로 채운다.
2. 3개 이상 연속된 보석이 있으면 삭제한다.
3. 다시 빈칸을 채운다.
4. 더 이상 삭제되는 보석이 없을 때까지 반복한다.
5. 가능한 교환이 있는지 검사한다.
6. 가능한 교환이 하나도 없으면 전체 보드를 삭제하고 다시 준비 과정을 반복한다.
```

주의:

```text
준비 상태를 만드는 과정에서 삭제되는 보석은 점수에 포함하지 않는다.
```

점수는 플레이어가 실제 교환을 수행한 뒤부터 계산한다.

---

## 6. 빈칸 채우기

빈칸은 위에서 내려오는 보석들로 채워진다.

좌표계상 `y=0`이 아래쪽이고 `y=7`이 위쪽이다.

따라서 각 열마다 다음 순서로 처리한다.

```text
1. 현재 열의 기존 보석들을 아래에서 위로 모은다.
2. 아래쪽부터 기존 보석들을 다시 배치한다.
3. 남은 위쪽 빈칸을 예비 보석으로 채운다.
```

구현 예:

```python
def _fill_empty():
    for x in range(8):
        remain = []

        for y in range(8):
            if board[y][x] != 0:
                remain.append(board[y][x])

        y = 0

        for jewel in remain:
            board[y][x] = jewel
            y += 1

        while y < 8:
            idx = supply_idx[x]
            board[y][x] = supply[idx][x]
            supply_idx[x] += 1
            y += 1
```

---

## 7. 삭제 대상 찾기

현재 보드에서 가로/세로 방향으로 3개 이상 연속된 보석을 찾는다.

가로 검사:

```text
각 행 y에 대해 x를 증가시키며 같은 보석 구간 길이 확인
```

세로 검사:

```text
각 열 x에 대해 y를 증가시키며 같은 보석 구간 길이 확인
```

삭제 대상은 `set`으로 관리한다.

```python
remove_cells = set()
```

이렇게 해야 가로와 세로가 겹치는 cell도 한 번만 삭제된다.

하지만 점수는 가로 줄과 세로 줄을 각각 계산해서 더한다.

---

## 8. 교환 후보 평가

플레이어가 선택할 수 있는 교환은 다음 두 종류뿐이다.

```text
1. 기준 좌표와 오른쪽 좌표 교환
2. 기준 좌표와 위쪽 좌표 교환
```

보드 범위를 벗어나는 교환은 불가능하다.

같은 보석끼리 교환해도 보드가 변하지 않으므로 점수를 얻을 수 없다.

따라서 후보에서 제외해도 된다.

각 후보는 다음 방식으로 평가한다.

```text
1. 두 보석을 임시로 교환한다.
2. 교환 직후 3개 이상 연속된 보석을 찾는다.
3. 그 즉시 삭제 점수만 계산한다.
4. 보드를 원상복구한다.
```

중요:

```text
후보 선택 기준 점수는 교환 직후 삭제 점수만 의미한다.
빈칸을 채운 뒤 발생하는 연쇄 삭제 점수는 후보 선택 기준에 포함하지 않는다.
```

---

## 9. 최적 교환 선택 우선순위

교환 가능한 후보가 여러 개라면 다음 우선순위로 선택한다.

```text
1. 교환 직후 얻을 수 있는 점수가 가장 높은 후보
2. 기준 좌표의 Y가 작은 후보
3. 기준 좌표의 X가 작은 후보
4. 오른쪽 교환 우선
```

구현에서는 y, x를 작은 순서로 순회하고, 같은 좌표에서는 오른쪽을 먼저 검사하면 된다.

```python
for y in range(8):
    for x in range(8):
        for direction in (RIGHT, UP):
            ...
```

단, 점수가 더 높은 후보가 나오면 갱신한다.

같은 점수의 후보는 먼저 발견된 것이 우선순위가 더 높으므로 갱신하지 않는다.

---

## 10. 실제 교환 후 점수 계산

최적 후보를 찾으면 실제로 교환을 수행한다.

그 후 다음 순서로 처리한다.

```text
1. 교환 직후 삭제 대상 찾기
2. 삭제하고 점수 추가
3. 빈칸 채우기
4. 다시 삭제 대상 찾기
5. 삭제할 대상이 있으면 점수 추가
6. 3~5 반복
7. 더 이상 삭제 대상이 없으면 턴 종료
```

이때는 후보 평가와 다르게 연쇄 삭제 점수까지 모두 포함한다.

즉, `takeTurn()`의 반환 점수는 다음이다.

```text
교환 직후 삭제 점수 + 이후 연쇄 삭제 점수
```

---

## 11. 주요 상태 변수

```python
BOARD_SIZE = 8
board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
supply = []
supply_idx = [0] * BOARD_SIZE
```

각 변수의 의미는 다음과 같다.

| 변수 | 의미 |
|---|---|
| `board[y][x]` | 현재 보드의 보석. 0이면 빈칸 |
| `supply[i][x]` | x열에 i번째로 내려올 예비 보석 |
| `supply_idx[x]` | x열에서 다음으로 사용할 예비 보석 index |

---

## 12. 전체 코드

```python
from typing import List


BOARD_SIZE = 8

board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
supply = []
supply_idx = [0] * BOARD_SIZE
N_SUPPLY = 0

RIGHT = 0
UP = 1

DY = [0, 1]
DX = [1, 0]


class Ret:
    def __init__(self, score: int, y: int, x: int, ny: int, nx: int):
        self.score = score
        self.y = y
        self.x = x
        self.ny = ny
        self.nx = nx


def init(N: int, mJewels: List[List[int]]) -> None:
    global board, supply, supply_idx, N_SUPPLY

    N_SUPPLY = N
    supply = [row[:] for row in mJewels]
    supply_idx = [0] * BOARD_SIZE

    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def _score_by_len(length: int) -> int:
    if length == 3:
        return 1
    if length == 4:
        return 4
    return 9


def _fill_empty() -> None:
    """
    빈칸을 위에서 내려오는 예비 보석으로 채운다.

    좌표는 y=0이 아래쪽, y=7이 위쪽이다.
    각 column은 독립적으로 예비 보석을 소비한다.
    """
    global board, supply_idx

    for x in range(BOARD_SIZE):
        remain = []

        # 아래에서 위로 보면서 기존 보석만 남긴다.
        for y in range(BOARD_SIZE):
            if board[y][x] != 0:
                remain.append(board[y][x])

        # 아래쪽부터 기존 보석을 채운다.
        y = 0
        for jewel in remain:
            board[y][x] = jewel
            y += 1

        # 남은 빈칸은 예비 보석으로 채운다.
        while y < BOARD_SIZE:
            idx = supply_idx[x]
            board[y][x] = supply[idx][x]
            supply_idx[x] += 1
            y += 1


def _find_matches():
    """
    현재 board에서 가로/세로 3개 이상 연속된 보석을 찾는다.

    반환:
    - total_score: 이번 삭제로 얻는 점수
    - remove_cells: 삭제될 좌표 set

    겹치는 cell은 한 번만 삭제하지만,
    점수는 가로 줄, 세로 줄 각각 합산한다.
    """
    total_score = 0
    remove_cells = set()

    # 가로 검사
    for y in range(BOARD_SIZE):
        x = 0

        while x < BOARD_SIZE:
            jewel = board[y][x]

            if jewel == 0:
                x += 1
                continue

            start = x

            while x < BOARD_SIZE and board[y][x] == jewel:
                x += 1

            length = x - start

            if length >= 3:
                total_score += _score_by_len(length)

                for cx in range(start, x):
                    remove_cells.add((y, cx))

    # 세로 검사
    for x in range(BOARD_SIZE):
        y = 0

        while y < BOARD_SIZE:
            jewel = board[y][x]

            if jewel == 0:
                y += 1
                continue

            start = y

            while y < BOARD_SIZE and board[y][x] == jewel:
                y += 1

            length = y - start

            if length >= 3:
                total_score += _score_by_len(length)

                for cy in range(start, y):
                    remove_cells.add((cy, x))

    return total_score, remove_cells


def _remove_cells(cells) -> None:
    for y, x in cells:
        board[y][x] = 0


def _resolve_board_without_score() -> None:
    """
    준비 상태를 만들 때 사용한다.

    빈칸을 채우고,
    3개 이상 연속된 보석이 있으면 삭제한다.

    준비 과정에서 발생하는 삭제는 플레이어 점수로 계산하지 않는다.
    """
    while True:
        _fill_empty()

        score, cells = _find_matches()

        if not cells:
            break

        _remove_cells(cells)


def _is_valid_coord(y: int, x: int) -> bool:
    return 0 <= y < BOARD_SIZE and 0 <= x < BOARD_SIZE


def _immediate_score_after_swap(y: int, x: int, direction: int) -> int:
    """
    특정 좌표에서 오른쪽 또는 위쪽 보석과 교환했을 때,
    교환 직후 바로 삭제되는 보석의 점수만 계산한다.

    cascade 점수는 여기서 고려하지 않는다.
    """
    ny = y + DY[direction]
    nx = x + DX[direction]

    if not _is_valid_coord(ny, nx):
        return 0

    if board[y][x] == board[ny][nx]:
        return 0

    board[y][x], board[ny][nx] = board[ny][nx], board[y][x]

    score, cells = _find_matches()

    board[y][x], board[ny][nx] = board[ny][nx], board[y][x]

    if not cells:
        return 0

    return score


def _find_best_move():
    """
    가능한 모든 교환 후보 중 최적 후보를 찾는다.

    우선순위:
    1. 교환 직후 얻는 점수가 큰 것
    2. 기준 좌표 y가 작은 것
    3. 기준 좌표 x가 작은 것
    4. 오른쪽 교환 우선
    """
    best_score = 0
    best = None

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            # 같은 y, x에서는 오른쪽을 먼저 검사한다.
            for direction in (RIGHT, UP):
                score = _immediate_score_after_swap(y, x, direction)

                if score == 0:
                    continue

                if score > best_score:
                    ny = y + DY[direction]
                    nx = x + DX[direction]

                    best_score = score
                    best = (y, x, ny, nx, direction)

    return best_score, best


def _prepare_board() -> None:
    """
    매 턴 시작 전 준비 상태를 만든다.

    준비 상태 조건:
    1. 빈칸이 없어야 한다.
    2. 3개 이상 연속된 보석이 없어야 한다.
    3. 점수를 얻을 수 있는 교환이 최소 1개 있어야 한다.

    가능한 교환이 없으면 전체 보석을 삭제하고 다시 준비한다.
    """
    global board

    while True:
        _resolve_board_without_score()

        best_score, best = _find_best_move()

        if best is not None:
            return

        # 가능한 교환이 없으면 전체 보석 삭제
        board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def _play_after_swap(y: int, x: int, ny: int, nx: int) -> int:
    """
    실제 교환을 수행하고,
    삭제 + 중력 + 연쇄 삭제를 더 이상 삭제될 게 없을 때까지 반복한다.

    반환값은 이번 턴 총 점수이다.
    """
    total_score = 0

    board[y][x], board[ny][nx] = board[ny][nx], board[y][x]

    # 교환 직후 삭제
    score, cells = _find_matches()

    if cells:
        total_score += score
        _remove_cells(cells)

    # 이후 cascade 처리
    while True:
        _fill_empty()

        score, cells = _find_matches()

        if not cells:
            break

        total_score += score
        _remove_cells(cells)

    return total_score


def takeTurn() -> Ret:
    """
    매 턴 과정:
    1. 준비 상태 만들기
    2. 최적 교환 선택
    3. 교환 후 삭제 및 cascade 처리
    """
    _prepare_board()

    _, best = _find_best_move()

    y, x, ny, nx, direction = best

    total_score = _play_after_swap(y, x, ny, nx)

    return Ret(total_score, y, x, ny, nx)
```

---

## 13. 실수하기 쉬운 포인트

### 13.1 좌표계

문제의 좌표는 `(Y, X)`이고, 좌측 하단이 `(0, 0)`이다.

따라서 위쪽은 `Y + 1`, 오른쪽은 `X + 1`이다.

```python
RIGHT = 0
UP = 1

DY = [0, 1]
DX = [1, 0]
```

---

### 13.2 보충 방향

빈칸은 위에서 내려오므로 기존 보석은 아래로 떨어진다.

따라서 각 열을 `y=0`부터 보면서 기존 보석을 아래쪽부터 다시 배치한다.

---

### 13.3 후보 선택 점수와 실제 획득 점수가 다르다

후보 선택 시에는 교환 직후 바로 삭제되는 점수만 본다.

하지만 실제 턴 점수는 연쇄 삭제 점수까지 포함한다.

```text
후보 선택 기준 = immediate score
반환 점수 = immediate score + cascade score
```

---

### 13.4 준비 상태에서 발생한 삭제는 점수에 포함하지 않는다

준비 상태를 만들기 위해 보석이 삭제될 수 있다.

이 삭제는 플레이어의 교환으로 발생한 것이 아니므로 점수에 포함하지 않는다.

---

### 13.5 가능한 교환이 없으면 전체 삭제 후 재준비

준비 상태 조건에는 가능한 교환이 최소 1개 존재해야 한다는 조건이 있다.

가능한 교환이 없으면 보드 전체를 삭제하고, 예비 보석으로 다시 채운다.

---

### 13.6 같은 좌표 우선순위에서는 오른쪽 교환 우선

같은 점수, 같은 기준 좌표라면 오른쪽 교환이 위쪽 교환보다 우선이다.

따라서 후보 탐색 시 방향 순서를 `(RIGHT, UP)`으로 둔다.

---

### 13.7 같은 점수 후보가 나왔을 때 갱신하지 않는다

y, x, direction을 우선순위 순서대로 순회하고 있으므로, 같은 점수 후보가 나오면 기존 후보를 유지해야 한다.

따라서 갱신 조건은 다음처럼 둔다.

```python
if score > best_score:
    update
```

`>=`를 쓰면 우선순위가 깨질 수 있다.

---

## 14. 시간복잡도

보드 크기는 항상 `8 x 8`로 고정이다.

가능한 교환 후보는 최대 다음 정도이다.

```text
오른쪽 교환: 8 * 7 = 56개
위쪽 교환: 7 * 8 = 56개
총 112개
```

각 후보마다 전체 보드에서 매치를 검사해도 64칸뿐이다.

따라서 한 턴의 계산량은 매우 작다.

```text
O(1)
```

실제로는 고정 크기 보드 시뮬레이션이다.

---

## 15. 핵심 결론

이 문제는 최적화보다 규칙 분리가 중요하다.

핵심은 다음 네 가지이다.

```text
1. 준비 상태 과정은 점수에 포함하지 않는다.
2. 후보 선택은 교환 직후 점수만 기준으로 한다.
3. 실제 턴 점수는 연쇄 삭제까지 포함한다.
4. 가능한 교환이 없으면 전체 보드를 삭제하고 다시 준비한다.
```

이 네 가지를 지키면 시뮬레이션 흐름을 안정적으로 구현할 수 있다.

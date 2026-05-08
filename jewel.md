# 8x8 보석 교환 게임 시뮬레이션 문제 정리

## 1. 문제 핵심

`8 x 8` 보드에서 보석을 교환하고, 같은 보석이 가로 또는 세로로 3개 이상 연속되면 삭제하여 점수를 얻는 문제이다.

좌표계는 다음과 같다.

```text
좌측 하단 = (0, 0)
좌표 표기 = (Y, X)
```

즉:

```text
y = 0 아래쪽
y = 7 위쪽
x = 0 왼쪽
x = 7 오른쪽
```

플레이어는 매 턴 기준 좌표 하나를 고르고, 그 오른쪽 또는 위쪽 인접 보석과 교환한다.

```text
오른쪽 교환: (y, x) ↔ (y, x + 1)
위쪽 교환:   (y, x) ↔ (y + 1, x)
```

---

## 2. 점수 규칙

같은 보석이 연속된 길이에 따라 점수가 정해진다.

| 연속 길이 | 점수 |
|---|---|
| 3개 | 1점 |
| 4개 | 4점 |
| 5개 이상 | 9점 |

가로와 세로에서 동시에 삭제되는 줄이 여러 개 있으면 점수는 모두 합산한다.

주의:

```text
같은 cell이 가로/세로 매치에 동시에 포함되면 삭제는 한 번만 한다.
하지만 점수는 가로 줄, 세로 줄 각각 계산해서 합산한다.
```

예를 들어 십자 모양으로 가로 3개, 세로 3개가 동시에 만들어지면:

```text
가로 3개 = 1점
세로 3개 = 1점
총점 = 2점
```

---

## 3. 턴 진행 과정

한 턴은 다음 순서로 진행된다.

```text
1. 보드를 준비 상태로 만든다.
2. 가능한 교환 중 최적 교환을 선택한다.
3. 실제 교환 후 삭제, 보충, 연쇄 삭제를 처리한다.
```

---

## 4. 준비 상태

턴 시작 전 보드는 반드시 준비 상태가 되어야 한다.

준비 상태 조건은 다음과 같다.

```text
1. 빈칸이 없어야 한다.
2. 현재 3개 이상 연속된 보석이 없어야 한다.
3. 교환해서 점수를 얻을 수 있는 방법이 최소 1개 있어야 한다.
```

준비 과정은 다음과 같다.

```text
빈칸 채우기
→ 매치 검사
→ 매치가 있으면 삭제
→ 다시 빈칸 채우기
→ 매치가 없을 때까지 반복
→ 가능한 교환이 있는지 확인
→ 가능한 교환이 없으면 보드 전체 삭제 후 다시 준비
```

주의:

```text
준비 상태를 만들면서 삭제되는 보석의 점수는 반환 점수에 포함하지 않는다.
```

---

## 5. 핵심 상태

```python
BOARD = 8
EMPTY = 0

board[y][x]
```

현재 보드 상태이다.

```text
0이면 빈칸
1~6이면 보석
```

예비 보석은 다음처럼 관리한다.

```python
jewels[row][x]
jewel_idx[x]
```

의미:

```text
jewel_idx[x] = x열에서 다음으로 사용할 예비 보석 row index
```

빈칸을 채울 때:

```python
board[y][x] = jewels[jewel_idx[x]][x]
jewel_idx[x] += 1
```

---

## 6. 중력 / 보충 처리

이 문제에서 `y=0`은 아래쪽이다.

따라서 보석이 아래로 떨어진다는 것은:

```text
각 열마다 살아있는 보석들을 y=0부터 다시 쌓는다.
남은 위쪽 칸은 예비 보석으로 채운다.
```

예를 들어 한 열이 아래에서 위로 다음과 같다고 하자.

```text
[2, 0, 3, 0, 4, 0, 1, 0]
```

중력 적용 후 기존 보석은 아래로 모인다.

```text
[2, 3, 4, 1, ?, ?, ?, ?]
```

`?` 위치는 예비 보석으로 채운다.

---

## 7. write pointer 방식

중력 처리는 `write pointer`로 구현할 수 있다.

```python
def _fill_board():
    for x in range(BOARD):
        write = 0

        for y in range(BOARD):
            if board[y][x] != EMPTY:
                board[write][x] = board[y][x]
                write += 1

        while write < BOARD:
            board[write][x] = jewels[jewel_idx[x]][x]
            jewel_idx[x] += 1
            write += 1
```

여기서 `write`는:

```text
다음 보석이 떨어져야 하는 위치
```

를 의미한다.

아래에서 위로 보면서 살아있는 보석을 만나면 `board[write][x]`에 넣고 `write`를 증가시킨다.

이후 `write`부터 위쪽까지는 예비 보석으로 덮어쓴다.

기존 값이 남아 있어도 어차피 덮어쓰기 때문에 따로 0으로 초기화할 필요는 없다.

---

## 8. 전체 매치 검사

전체 보드에서 삭제될 보석을 찾는 함수가 필요하다.

이 함수는 다음 상황에서 사용한다.

```text
1. 준비 상태 만들기
2. 연쇄 삭제 cascade 처리
```

전체 매치 검사에서는 가로 8줄, 세로 8줄을 모두 검사한다.

```python
def _find_matches_full():
    total_score = 0
    mark = [[False] * BOARD for _ in range(BOARD)]

    # 가로 검사
    for y in range(BOARD):
        x = 0
        while x < BOARD:
            v = board[y][x]

            if v == EMPTY:
                x += 1
                continue

            start = x

            while x < BOARD and board[y][x] == v:
                x += 1

            length = x - start

            if length >= 3:
                total_score += _score(length)
                for cx in range(start, x):
                    mark[y][cx] = True

    # 세로 검사
    for x in range(BOARD):
        y = 0
        while y < BOARD:
            v = board[y][x]

            if v == EMPTY:
                y += 1
                continue

            start = y

            while y < BOARD and board[y][x] == v:
                y += 1

            length = y - start

            if length >= 3:
                total_score += _score(length)
                for cy in range(start, y):
                    mark[cy][x] = True

    cells = []

    for y in range(BOARD):
        for x in range(BOARD):
            if mark[y][x]:
                cells.append((y, x))

    return total_score, cells
```

`mark`를 쓰는 이유:

```text
가로/세로가 겹치는 cell도 삭제는 한 번만 하기 위해서
```

점수는 줄 단위로 더하고, 삭제 좌표는 중복 없이 표시한다.

---

## 9. 후보 교환 평가 최적화

처음에는 후보 교환마다 전체 보드를 검사할 수 있다.

```text
후보 최대 112개
각 후보마다 전체 보드 매치 검사
```

하지만 이러면 타임아웃이 날 수 있다.

최적화 핵심:

```text
준비 상태에서는 이미 3개 이상 연속이 없다.
따라서 두 보석을 교환했을 때 새로 생기는 매치는 반드시 교환된 두 좌표 중 하나를 포함한다.
```

즉 후보 평가 시 전체 보드를 볼 필요가 없다.

다음 네 줄만 보면 된다.

```text
교환된 첫 번째 좌표의 가로줄
교환된 첫 번째 좌표의 세로줄
교환된 두 번째 좌표의 가로줄
교환된 두 번째 좌표의 세로줄
```

---

## 10. 특정 좌표 주변 매치 검사

특정 좌표를 포함하는 가로 또는 세로 연속 구간을 찾는다.

```python
def _line_run(y: int, x: int, horizontal: bool):
    v = board[y][x]

    if v == EMPTY:
        return 0, [], None

    cells = [(y, x)]

    if horizontal:
        cx = x - 1
        while cx >= 0 and board[y][cx] == v:
            cells.append((y, cx))
            cx -= 1

        cx = x + 1
        while cx < BOARD and board[y][cx] == v:
            cells.append((y, cx))
            cx += 1

        xs = [c[1] for c in cells]
        key = ("H", y, min(xs), max(xs))

    else:
        cy = y - 1
        while cy >= 0 and board[cy][x] == v:
            cells.append((cy, x))
            cy -= 1

        cy = y + 1
        while cy < BOARD and board[cy][x] == v:
            cells.append((cy, x))
            cy += 1

        ys = [c[0] for c in cells]
        key = ("V", x, min(ys), max(ys))

    return len(cells), cells, key
```

`key`는 같은 라인을 중복 계산하지 않기 위해 사용한다.

예를 들어 가로 매치가 `y=3`, `x=2~4`라면:

```python
("H", 3, 2, 4)
```

세로 매치가 `x=5`, `y=1~3`라면:

```python
("V", 5, 1, 3)
```

---

## 11. 교환 좌표 주변만 검사

```python
def _matches_around(points, need_cells: bool):
    total_score = 0
    seen_lines = set()
    remove_mark = [[False] * BOARD for _ in range(BOARD)] if need_cells else None

    for y, x in points:
        for horizontal in (True, False):
            length, cells, key = _line_run(y, x, horizontal)

            if length < 3:
                continue

            if key in seen_lines:
                continue

            seen_lines.add(key)
            total_score += _score(length)

            if need_cells:
                for cy, cx in cells:
                    remove_mark[cy][cx] = True

    if not need_cells:
        return total_score, []

    remove_cells = []

    for y in range(BOARD):
        for x in range(BOARD):
            if remove_mark[y][x]:
                remove_cells.append((y, x))

    return total_score, remove_cells
```

사용 방식:

```python
# 후보 평가용: 점수만 필요
score, _ = _matches_around([(y1, x1), (y2, x2)], False)

# 실제 삭제용: 삭제 좌표도 필요
score, cells = _matches_around([(y1, x1), (y2, x2)], True)
```

---

## 12. 최적 교환 선택

후보 우선순위는 다음과 같다.

```text
1. 교환 직후 점수가 가장 큰 것
2. 기준 좌표 y가 작은 것
3. 기준 좌표 x가 작은 것
4. 오른쪽 교환 우선
```

이를 자연스럽게 구현하려면 순회를 다음 순서로 한다.

```text
y 작은 순서
x 작은 순서
오른쪽 먼저
위쪽 나중
```

그리고 점수가 같을 때는 갱신하지 않는다.

```python
if score > best_score:
    update
```

`>=`를 쓰면 우선순위가 깨질 수 있다.

```python
def _find_best_move():
    best_score = 0
    best_move = None

    for y in range(BOARD):
        for x in range(BOARD):
            # 오른쪽
            if x + 1 < BOARD:
                score = _immediate_score_after_swap(y, x, y, x + 1)

                if score > best_score:
                    best_score = score
                    best_move = (y, x, y, x + 1)

            # 위쪽
            if y + 1 < BOARD:
                score = _immediate_score_after_swap(y, x, y + 1, x)

                if score > best_score:
                    best_score = score
                    best_move = (y, x, y + 1, x)

    return best_score, best_move
```

---

## 13. 후보 평가

후보 평가에서는 cascade 점수를 고려하면 안 된다.

문제에서 후보 선택 기준은:

```text
교환 직후 바로 삭제되는 보석들의 점수
```

라고 되어 있다.

따라서 임시 교환 후 주변 매치 점수만 계산하고 원상복구한다.

```python
def _immediate_score_after_swap(y1: int, x1: int, y2: int, x2: int) -> int:
    if board[y1][x1] == board[y2][x2]:
        return 0

    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

    score, _ = _matches_around([(y1, x1), (y2, x2)], False)

    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

    return score
```

---

## 14. 실제 교환과 cascade

최적 교환을 찾으면 실제로 교환한다.

첫 삭제는 교환 때문에 생긴 것이므로 교환 좌표 주변만 보면 된다.

하지만 그 이후에는 보석이 새로 내려오므로 어디서든 매치가 생길 수 있다.

따라서 cascade 단계에서는 전체 보드를 검사해야 한다.

```python
def _play_swap_and_cascade(y1: int, x1: int, y2: int, x2: int) -> int:
    total_score = 0

    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

    # 교환 직후 삭제: 주변만 검사
    score, cells = _matches_around([(y1, x1), (y2, x2)], True)

    if cells:
        total_score += score
        _remove_cells(cells)

    # cascade: 보충 후에는 어디서든 매치가 생길 수 있음
    while True:
        _fill_board()

        score, cells = _find_matches_full()

        if not cells:
            break

        total_score += score
        _remove_cells(cells)

    return total_score
```

---

## 15. 전체 코드

```python
from typing import List

BOARD = 8
EMPTY = 0

board = [[0] * BOARD for _ in range(BOARD)]
jewels = []
jewel_idx = [0] * BOARD


def init(N, mJewels) -> None:
    global board, jewels, jewel_idx

    board = [[0] * BOARD for _ in range(BOARD)]
    jewels = [row[:] for row in mJewels]
    jewel_idx = [0] * BOARD


def _score(length: int) -> int:
    if length == 3:
        return 1
    if length == 4:
        return 4
    return 9


def _fill_board() -> None:
    for x in range(BOARD):
        write = 0

        for y in range(BOARD):
            if board[y][x] != EMPTY:
                board[write][x] = board[y][x]
                write += 1

        while write < BOARD:
            board[write][x] = jewels[jewel_idx[x]][x]
            jewel_idx[x] += 1
            write += 1


def _find_matches_full():
    total_score = 0
    mark = [[False] * BOARD for _ in range(BOARD)]

    # 가로 검사
    for y in range(BOARD):
        x = 0

        while x < BOARD:
            v = board[y][x]

            if v == EMPTY:
                x += 1
                continue

            start = x

            while x < BOARD and board[y][x] == v:
                x += 1

            length = x - start

            if length >= 3:
                total_score += _score(length)

                for cx in range(start, x):
                    mark[y][cx] = True

    # 세로 검사
    for x in range(BOARD):
        y = 0

        while y < BOARD:
            v = board[y][x]

            if v == EMPTY:
                y += 1
                continue

            start = y

            while y < BOARD and board[y][x] == v:
                y += 1

            length = y - start

            if length >= 3:
                total_score += _score(length)

                for cy in range(start, y):
                    mark[cy][x] = True

    cells = []

    for y in range(BOARD):
        for x in range(BOARD):
            if mark[y][x]:
                cells.append((y, x))

    return total_score, cells


def _remove_cells(cells) -> None:
    for y, x in cells:
        board[y][x] = EMPTY


def _line_run(y: int, x: int, horizontal: bool):
    v = board[y][x]

    if v == EMPTY:
        return 0, [], None

    cells = [(y, x)]

    if horizontal:
        cx = x - 1
        while cx >= 0 and board[y][cx] == v:
            cells.append((y, cx))
            cx -= 1

        cx = x + 1
        while cx < BOARD and board[y][cx] == v:
            cells.append((y, cx))
            cx += 1

        xs = [c[1] for c in cells]
        key = ("H", y, min(xs), max(xs))

    else:
        cy = y - 1
        while cy >= 0 and board[cy][x] == v:
            cells.append((cy, x))
            cy -= 1

        cy = y + 1
        while cy < BOARD and board[cy][x] == v:
            cells.append((cy, x))
            cy += 1

        ys = [c[0] for c in cells]
        key = ("V", x, min(ys), max(ys))

    return len(cells), cells, key


def _matches_around(points, need_cells: bool):
    total_score = 0
    seen_lines = set()
    remove_mark = [[False] * BOARD for _ in range(BOARD)] if need_cells else None

    for y, x in points:
        for horizontal in (True, False):
            length, cells, key = _line_run(y, x, horizontal)

            if length < 3:
                continue

            if key in seen_lines:
                continue

            seen_lines.add(key)
            total_score += _score(length)

            if need_cells:
                for cy, cx in cells:
                    remove_mark[cy][cx] = True

    if not need_cells:
        return total_score, []

    remove_cells = []

    for y in range(BOARD):
        for x in range(BOARD):
            if remove_mark[y][x]:
                remove_cells.append((y, x))

    return total_score, remove_cells


def _resolve_without_score() -> None:
    while True:
        _fill_board()

        _, cells = _find_matches_full()

        if not cells:
            break

        _remove_cells(cells)


def _immediate_score_after_swap(y1: int, x1: int, y2: int, x2: int) -> int:
    if board[y1][x1] == board[y2][x2]:
        return 0

    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

    score, _ = _matches_around([(y1, x1), (y2, x2)], False)

    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

    return score


def _find_best_move():
    best_score = 0
    best_move = None

    for y in range(BOARD):
        for x in range(BOARD):
            # 오른쪽 교환
            if x + 1 < BOARD:
                score = _immediate_score_after_swap(y, x, y, x + 1)

                if score > best_score:
                    best_score = score
                    best_move = (y, x, y, x + 1)

            # 위쪽 교환
            if y + 1 < BOARD:
                score = _immediate_score_after_swap(y, x, y + 1, x)

                if score > best_score:
                    best_score = score
                    best_move = (y, x, y + 1, x)

    return best_score, best_move


def _prepare_board() -> None:
    global board

    while True:
        _resolve_without_score()

        _, move = _find_best_move()

        if move is not None:
            return

        board = [[EMPTY] * BOARD for _ in range(BOARD)]


def _play_swap_and_cascade(y1: int, x1: int, y2: int, x2: int) -> int:
    total_score = 0

    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

    score, cells = _matches_around([(y1, x1), (y2, x2)], True)

    if cells:
        total_score += score
        _remove_cells(cells)

    while True:
        _fill_board()

        score, cells = _find_matches_full()

        if not cells:
            break

        total_score += score
        _remove_cells(cells)

    return total_score


def takeTurn() -> List[int]:
    _prepare_board()

    _, move = _find_best_move()

    y1, x1, y2, x2 = move

    total_score = _play_swap_and_cascade(y1, x1, y2, x2)

    return [total_score, y1, x1, y2, x2]
```

---

## 16. 실수하기 쉬운 포인트

### 16.1 후보 선택은 immediate score만 본다

연쇄 삭제 점수는 후보 선택 기준에 포함하지 않는다.

---

### 16.2 실제 점수는 cascade까지 포함한다

`takeTurn()` 반환 점수는 교환 직후 삭제 점수와 이후 연쇄 삭제 점수를 모두 포함한다.

---

### 16.3 준비 상태에서 발생한 삭제는 점수에 포함하지 않는다

준비 과정은 게임 시작 전 보드를 안정화하는 과정일 뿐이다.

---

### 16.4 같은 점수 후보는 갱신하지 않는다

우선순위 순서대로 순회하므로:

```python
if score > best_score:
```

만 사용해야 한다.

---

### 16.5 첫 교환 후 삭제는 주변 검사 가능

준비 상태에는 기존 매치가 없으므로 첫 삭제는 교환된 두 좌표 주변만 검사하면 된다.

---

### 16.6 cascade는 전체 검사 필요

보충 후에는 새 보석이 여러 위치에 들어오므로 어디서든 매치가 생길 수 있다.

따라서 cascade는 full scan이 필요하다.

---

## 17. 핵심 결론

이 문제는 다음 네 가지를 분리하면 된다.

```text
1. fill_board
   중력 + 예비 보석 보충

2. find_matches_full
   전체 보드 매치 검사

3. matches_around
   후보 평가 및 첫 삭제 최적화

4. play_swap_and_cascade
   실제 교환 후 연쇄 삭제 처리
```

최적화의 핵심은 다음이다.

```text
준비 상태에서는 기존 매치가 없으므로,
교환 후 새로 생기는 매치는 반드시 교환된 두 좌표 중 하나를 포함한다.
```

따라서 후보 평가는 전체 보드가 아니라 교환된 두 좌표 주변만 검사하면 된다.
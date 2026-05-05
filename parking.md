# 주차장 / 장기 주차 견인 / 차량 검색 문제 정리

## 1. 문제 개요

`N`개의 구역이 있고, 각 구역마다 `M`개의 슬롯이 있는 주차장이 있다.

구역은 영어 대문자로 구분된다.

```text
N = 3 → A, B, C
```

각 구역의 슬롯은 3자리 숫자로 구분된다.

```text
M = 4 → 000, 001, 002, 003
```

주차 위치는 구역 문자와 슬롯 번호를 이어 붙여 표현한다.

```text
A002
B015
C999
```

한 슬롯에는 차량 1대만 주차할 수 있다.

---

## 2. 입차 규칙

차량이 입차하면 다음 규칙에 따라 주차 위치가 정해진다.

```text
1. 빈 슬롯이 가장 많은 구역을 선택한다.
2. 빈 슬롯 수가 같으면 알파벳 순서가 빠른 구역을 선택한다.
3. 선택된 구역에서 번호가 가장 작은 빈 슬롯을 선택한다.
4. 모든 구역에 빈 슬롯이 없으면 주차 실패이다.
```

예를 들어 `A`, `B`, `C` 구역의 빈 슬롯 수가 다음과 같다면:

```text
A: 3개
B: 5개
C: 5개
```

`B`와 `C`가 가장 많지만, 알파벳이 빠른 `B` 구역이 선택된다.

---

## 3. 출차 규칙

차량이 주차 중이면 출차할 수 있다.

출차하면 해당 슬롯은 다시 빈 슬롯이 된다.

반환값은 다음과 같다.

```text
주차 중인 차량 출차 → 주차 기간 반환
```

주차 기간은 다음과 같다.

```python
mTime - enter_time
```

---

## 4. 장기 주차 견인

차량이 주차한 지 `L` 시간이 지나면 장기 주차 차량으로 간주되어 바로 견인된다.

예를 들어:

```text
L = 10
시각 5에 입차
→ 시각 15에 견인
```

견인되는 순간 해당 슬롯은 빈 슬롯이 된다.

견인된 차량은 주차 중 차량에서는 제거되지만, 시스템에는 “견인 기록”으로 남는다.

---

## 5. 견인 기록

견인된 차량은 `towed` 상태로 기록된다.

견인 기록은 다음 경우에 삭제된다.

```text
1. 견인된 차량에 대해 pullout 요청이 들어온 경우
2. 견인된 차량이 다시 enter 하는 경우
```

중요한 조건:

```text
견인된 차량이 재입차할 경우,
주차 성공 여부와 관계없이 견인 기록은 삭제된다.
```

즉, 주차장이 꽉 차서 재입차에 실패하더라도 견인 기록은 사라진다.

---

## 6. pullout 반환값

`pullout(mTime, mCarNo)`의 반환값은 차량 상태에 따라 다르다.

### 6.1 주차 중인 경우

```text
주차 기간 반환
```

```python
return mTime - enter_time
```

### 6.2 견인 기록이 있는 경우

```text
(주차된 기간 + 견인된 기간 * 5) * (-1)
```

주차된 기간:

```python
tow_time - enter_time
```

견인된 기간:

```python
mTime - tow_time
```

반환값:

```python
return -1 * (parking_period + towed_period * 5)
```

### 6.3 주차 중도 아니고 견인 기록도 없는 경우

```python
return -1
```

---

## 7. search 규칙

`search(mTime, mStr)`는 주차된 차량 또는 견인된 차량 중 차량 번호의 뒷 4자리가 `mStr`과 일치하는 차량을 최대 5대 검색한다.

차량 번호 형식은 다음과 같다.

```text
XXYZZZZ
```

- `XX`: 숫자 2자리
- `Y`: 영어 대문자 1글자
- `ZZZZ`: 숫자 4자리

예를 들어:

```text
mStr = "5870"
carNo = "24Z5870"
```

이면 검색 조건에 일치한다.

검색 우선순위는 다음과 같다.

```text
1. 주차된 차량이 견인된 차량보다 우선순위가 높다.
2. 같은 상태라면 XX를 숫자로 보았을 때 작은 차량이 우선이다.
3. XX도 같으면 Y의 알파벳 순서가 빠른 차량이 우선이다.
```

따라서 검색용 key는 다음과 같이 만들 수 있다.

```python
key = (int(car[0:2]), car[2], car)
```

---

## 8. 핵심 상태 관리

이 문제에서는 주차 중 차량과 견인 기록을 분리해서 관리한다.

```python
parked = {}
towed = {}
```

각 상태의 의미는 다음과 같다.

| 변수 | 의미 |
|---|---|
| `parked` | 현재 주차 중인 차량 정보 |
| `towed` | 견인 기록이 남아 있는 차량 정보 |

---

## 9. 주요 자료구조

### 9.1 구역별 빈 슬롯 수

```python
free_cnt[zone]
```

각 구역에 빈 슬롯이 몇 개 있는지 저장한다.

입차 시 가장 큰 `free_cnt`를 가진 구역을 찾는다.

구역 수 `N`은 최대 26이므로 매번 전체 구역을 스캔해도 충분하다.

```python
best_zone = -1
best_cnt = -1

for z in range(N_ZONE):
    if free_cnt[z] > best_cnt:
        best_cnt = free_cnt[z]
        best_zone = z
```

동률이면 알파벳이 빠른 구역을 선택해야 하므로, `0`번 구역부터 순회하고 `>`일 때만 갱신한다.

---

### 9.2 구역별 빈 슬롯 heap

```python
free_slots[zone]
```

각 구역의 빈 슬롯 번호를 min heap으로 관리한다.

입차 시 가장 작은 슬롯 번호를 꺼낸다.

```python
slot = heapq.heappop(free_slots[zone])
```

출차 또는 견인 시 슬롯을 다시 넣는다.

```python
heapq.heappush(free_slots[zone], slot)
```

---

### 9.3 주차 중 차량

```python
parked[car] = (enter_time, zone, slot, token)
```

각 차량의 현재 주차 정보를 저장한다.

| 값 | 의미 |
|---|---|
| `enter_time` | 입차 시각 |
| `zone` | 주차 구역 index |
| `slot` | 슬롯 번호 |
| `token` | 해당 입차 이벤트 식별자 |

---

### 9.4 견인 기록

```python
towed[car] = (enter_time, tow_time, token)
```

각 견인 차량의 기록을 저장한다.

| 값 | 의미 |
|---|---|
| `enter_time` | 원래 입차 시각 |
| `tow_time` | 견인 시각 |
| `token` | 해당 입차 이벤트 식별자 |

---

### 9.5 견인 이벤트 heap

```python
tow_events = [(tow_time, car, token), ...]
```

차량이 입차할 때 견인 예정 시각을 heap에 넣는다.

```python
tow_time = mTime + L_TIME
heapq.heappush(tow_events, (tow_time, car, token))
```

모든 API 시작 시 `mTime`까지 견인될 차량을 처리한다.

---

### 9.6 검색용 suffix heap

뒷 4자리가 같은 차량을 빠르게 검색하기 위해 suffix별 heap을 둔다.

```python
park_suffix[suffix]
tow_suffix[suffix]
```

각 heap에는 다음 형태로 저장한다.

```python
(num, alpha, car, token)
```

- `num = int(car[0:2])`
- `alpha = car[2]`
- `car = 차량 번호`
- `token = 상태 식별자`

주차 차량과 견인 차량의 우선순위가 다르므로 heap도 따로 둔다.

```python
park_suffix  # 현재 주차 중인 차량 검색용
tow_suffix   # 견인 기록 차량 검색용
```

검색할 때는 먼저 `park_suffix`에서 최대 5대를 찾고, 부족하면 `tow_suffix`에서 찾는다.

---

## 10. token을 사용하는 이유

같은 차량 번호가 여러 번 등장할 수 있다.

예를 들어:

```text
시각 10: 차량 A 입차
시각 20: 차량 A 출차
시각 30: 차량 A 재입차
```

첫 번째 입차 때 등록한 견인 이벤트는 heap에 남아 있을 수 있다.

만약 token 없이 처리하면, 이전 입차의 견인 이벤트가 나중에 잘못 실행될 수 있다.

이를 막기 위해 입차할 때마다 새로운 token을 발급한다.

```python
token_seq += 1
token = token_seq
```

그리고 주차 정보와 견인 이벤트에 함께 저장한다.

```python
parked[car] = (mTime, zone, slot, token)
heapq.heappush(tow_events, (tow_time, car, token))
```

견인 이벤트 처리 시 현재 parked의 token과 이벤트 token이 같은지 확인한다.

```python
if cur_token != token:
    continue
```

다르면 낡은 이벤트이므로 무시한다.

---

## 11. lazy deletion

검색용 heap에는 출차되거나 견인 기록이 삭제된 차량의 오래된 기록이 남아 있을 수 있다.

heap은 중간 원소 삭제가 어렵기 때문에, 삭제 시 즉시 heap에서 제거하지 않는다.

대신 검색할 때 꺼내면서 현재 상태와 token을 확인한다.

```python
rec = storage.get(car)

if rec is not None and rec[-1] == token:
    result.append(car)
else:
    # 낡은 기록이므로 버림
```

이 방식을 lazy deletion이라고 한다.

유효한 기록은 검색 후 다시 heap에 넣어둔다.

---

## 12. API별 동작 정리

### 12.1 init

초기 상태를 모두 초기화한다.

```text
1. 구역 수, 슬롯 수, 주차 가능 기간 L 저장
2. 모든 구역의 빈 슬롯 수를 M으로 설정
3. 각 구역의 빈 슬롯 heap 초기화
4. parked, towed 초기화
5. tow_events 초기화
6. 검색용 heap 초기화
7. token_seq 초기화
```

---

### 12.2 enter

입차 처리 순서:

```text
1. mTime까지 견인 이벤트 처리
2. 해당 차량이 견인 기록에 있으면 삭제
3. 주차할 구역과 슬롯 선택
4. 주차 실패 시 success = 0 반환
5. 주차 성공 시 parked에 등록
6. 검색용 park_suffix에 등록
7. 견인 이벤트 등록
8. success = 1과 locname 반환
```

주의:

```text
견인 기록 삭제는 주차 성공 여부와 무관하게 먼저 처리한다.
```

---

### 12.3 pullout

출차 처리 순서:

```text
1. mTime까지 견인 이벤트 처리
2. 차량이 parked에 있으면 일반 출차 처리
   - parked에서 삭제
   - 슬롯 반환
   - 주차 기간 반환
3. 차량이 towed에 있으면 견인 기록 처리
   - towed에서 삭제
   - 음수 penalty 반환
4. 둘 다 없으면 -1 반환
```

---

### 12.4 search

검색 처리 순서:

```text
1. mTime까지 견인 이벤트 처리
2. 뒷 4자리 suffix 추출
3. park_suffix[suffix]에서 유효한 차량 최대 5대 검색
4. 부족하면 tow_suffix[suffix]에서 추가 검색
5. RESULT_S에 cnt와 carlist 저장 후 반환
```

주차 차량이 견인 차량보다 우선이므로 반드시 주차 차량 heap을 먼저 본다.

---

## 13. 전체 코드

```python
import heapq
from collections import defaultdict


class RESULT_E:
    def __init__(self, success, locname):
        self.success = success
        self.locname = locname


class RESULT_S:
    def __init__(self, cnt, carlist):
        self.cnt = cnt
        self.carlist = carlist


N_ZONE = 0
M_SLOT = 0
L_TIME = 0

# 구역별 빈 슬롯 수
free_cnt = []

# 구역별 빈 슬롯 min heap
free_slots = []

# 현재 주차 중인 차량
# car_no -> (enter_time, zone_idx, slot_idx, token)
parked = {}

# 견인 기록
# car_no -> (enter_time, tow_time, token)
towed = {}

# 견인 이벤트 heap
# (tow_time, car_no, token)
tow_events = []

# 검색용 heap
# suffix -> [(XX, Y, car_no, token), ...]
park_suffix = defaultdict(list)
tow_suffix = defaultdict(list)

# 차량 상태 변경마다 새로 발급하는 token
token_seq = 0


def _to_str(car):
    """
    채점 환경에 따라 문자열이 str 또는 char list 형태로 들어올 수 있으므로 방어적으로 처리한다.
    """
    if isinstance(car, str):
        return car
    return ''.join(car)


def _car_key(car):
    """
    검색 우선순위용 key.

    차량 번호 형식: XXYZZZZ

    우선순위:
    1. XX 숫자가 작은 것
    2. Y 알파벳이 빠른 것
    """
    return (int(car[0:2]), car[2], car)


def _suffix(car):
    return car[3:7]


def _locname(zone, slot):
    return chr(ord('A') + zone) + f"{slot:03d}"


def init(N, M, L):
    global N_ZONE, M_SLOT, L_TIME
    global free_cnt, free_slots
    global parked, towed, tow_events
    global park_suffix, tow_suffix
    global token_seq

    N_ZONE = N
    M_SLOT = M
    L_TIME = L

    free_cnt = [M] * N
    free_slots = []

    for _ in range(N):
        free_slots.append(list(range(M)))

    parked = {}
    towed = {}
    tow_events = []

    park_suffix = defaultdict(list)
    tow_suffix = defaultdict(list)

    token_seq = 0


def _process_tow(mTime):
    """
    mTime 시각까지 견인되어야 하는 차량을 모두 처리한다.

    견인 시각이 mTime 이하이면 그 차량은 이미 견인된 상태로 본다.
    """
    global parked, towed

    while tow_events and tow_events[0][0] <= mTime:
        tow_time, car, token = heapq.heappop(tow_events)

        if car not in parked:
            continue

        enter_time, zone, slot, cur_token = parked[car]

        # 이미 출차 후 재입차한 차량의 낡은 이벤트 방지
        if cur_token != token:
            continue

        # 주차 상태 제거
        del parked[car]

        # 슬롯 반환
        free_cnt[zone] += 1
        heapq.heappush(free_slots[zone], slot)

        # 견인 기록 생성
        towed[car] = (enter_time, tow_time, token)

        key = _car_key(car)
        sfx = _suffix(car)
        heapq.heappush(tow_suffix[sfx], (key[0], key[1], key[2], token))


def _select_parking_slot():
    """
    주차할 구역과 슬롯을 선택한다.

    규칙:
    1. 빈 슬롯이 가장 많은 구역
    2. 동률이면 알파벳이 빠른 구역
    3. 해당 구역에서 번호가 가장 작은 빈 슬롯
    """
    best_zone = -1
    best_cnt = -1

    for z in range(N_ZONE):
        if free_cnt[z] > best_cnt:
            best_cnt = free_cnt[z]
            best_zone = z

    if best_cnt == 0:
        return None

    slot = heapq.heappop(free_slots[best_zone])
    free_cnt[best_zone] -= 1

    return best_zone, slot


def enter(mTime, mCarNo):
    global token_seq

    car = _to_str(mCarNo)

    # 입차 시각까지 견인 처리
    _process_tow(mTime)

    # 견인된 차량이 재입차하면, 주차 성공 여부와 무관하게 견인 기록 삭제
    if car in towed:
        del towed[car]

    selected = _select_parking_slot()

    if selected is None:
        return RESULT_E(0, "")

    zone, slot = selected

    token_seq += 1
    token = token_seq

    parked[car] = (mTime, zone, slot, token)

    # 검색용 heap에 추가
    key = _car_key(car)
    sfx = _suffix(car)
    heapq.heappush(park_suffix[sfx], (key[0], key[1], key[2], token))

    # 견인 이벤트 등록
    tow_time = mTime + L_TIME
    heapq.heappush(tow_events, (tow_time, car, token))

    return RESULT_E(1, _locname(zone, slot))


def pullout(mTime, mCarNo):
    car = _to_str(mCarNo)

    # 출차 시각까지 견인 처리
    _process_tow(mTime)

    # 1. 현재 주차 중인 경우
    if car in parked:
        enter_time, zone, slot, token = parked[car]

        del parked[car]

        free_cnt[zone] += 1
        heapq.heappush(free_slots[zone], slot)

        return mTime - enter_time

    # 2. 견인 기록이 있는 경우
    if car in towed:
        enter_time, tow_time, token = towed[car]

        del towed[car]

        parking_period = tow_time - enter_time
        towed_period = mTime - tow_time

        return -1 * (parking_period + towed_period * 5)

    # 3. 주차 중도 아니고 견인 기록도 없는 경우
    return -1


def _collect_from_heap(heap, storage, limit):
    """
    검색용 heap에서 현재 유효한 차량만 우선순위 순서대로 최대 limit개 가져온다.

    heap에는 오래된 기록이 남아 있을 수 있으므로 lazy deletion을 사용한다.
    """
    result = []
    temp = []

    while heap and len(result) < limit:
        num, alpha, car, token = heapq.heappop(heap)

        rec = storage.get(car)

        if rec is not None and rec[-1] == token:
            result.append(car)
            temp.append((num, alpha, car, token))
        # else: 낡은 기록은 버림

    # 유효한 기록은 다시 heap에 넣어둔다.
    for item in temp:
        heapq.heappush(heap, item)

    return result


def search(mTime, mStr):
    sfx = _to_str(mStr)

    # 검색 시각까지 견인 처리
    _process_tow(mTime)

    result = []

    # 주차된 차량이 견인된 차량보다 우선
    if sfx in park_suffix:
        result.extend(_collect_from_heap(park_suffix[sfx], parked, 5))

    # 주차 차량이 5대 미만일 때만 견인 차량 검색
    if len(result) < 5 and sfx in tow_suffix:
        result.extend(_collect_from_heap(tow_suffix[sfx], towed, 5 - len(result)))

    return RESULT_S(len(result), result)
```

---

## 14. 시간복잡도

### 14.1 enter

```text
_process_tow(mTime) + O(N) + O(log M)
```

- 견인 이벤트 처리
- 구역 선택: `N <= 26`이므로 사실상 상수
- 슬롯 선택: min heap에서 `O(log M)`

### 14.2 pullout

```text
_process_tow(mTime) + O(log M)
```

출차 또는 견인 처리 시 슬롯을 heap에 다시 넣는다.

### 14.3 search

최대 5대만 반환한다.

```text
O(5 log K)
```

단, lazy deletion 때문에 낡은 기록을 추가로 pop할 수 있다.

하지만 각 낡은 기록은 한 번 버려지면 다시 보지 않으므로 전체적으로 효율적이다.

---

## 15. 실수하기 쉬운 포인트

### 15.1 모든 API 시작 시 견인 처리

입차, 출차, 검색 모두 시작 시점에 `mTime`까지 견인될 차량을 먼저 처리해야 한다.

```python
_process_tow(mTime)
```

견인 시각이 정확히 `mTime`인 차량도 이미 견인된 것으로 처리한다.

```python
while tow_events and tow_events[0][0] <= mTime:
```

---

### 15.2 재입차 시 견인 기록 삭제

견인된 차량이 다시 입차 요청을 하면 주차 성공 여부와 무관하게 견인 기록을 삭제한다.

```python
if car in towed:
    del towed[car]
```

이 처리는 주차 가능 여부를 확인하기 전에 해야 한다.

---

### 15.3 견인된 차량 pullout 시 음수 반환

견인된 차량에 대해 `pullout`이 들어오면 다음 값을 반환한다.

```python
-1 * (parking_period + towed_period * 5)
```

그리고 견인 기록은 삭제한다.

---

### 15.4 다운로드 완료 같은 개념이 없음

이 문제에서는 주차/견인/출차만 있다.

견인된 차량은 주차장에서 사라졌지만, 기록만 남아 있는 상태이다.

---

### 15.5 search에서는 주차 차량이 항상 먼저

주차 차량 5대를 찾았으면 견인 차량은 보지 않는다.

```python
if len(result) < 5:
    견인 차량 검색
```

---

### 15.6 heap에서 직접 삭제하지 않는다

출차 또는 견인 기록 삭제 시 검색용 heap에서 직접 삭제하지 않는다.

검색 시점에 token을 확인해서 낡은 기록을 버린다.

이것이 lazy deletion이다.

---

## 16. 핵심 결론

이 문제는 다음 네 가지를 정확히 관리하면 된다.

```text
1. 입차/출차/검색 전에 mTime까지 견인 이벤트를 처리한다.
2. 현재 주차 중인 차량 parked와 견인 기록 towed를 분리한다.
3. 재입차/출차/견인 이벤트의 낡은 기록은 token으로 방어한다.
4. 검색은 suffix별 heap과 lazy deletion으로 처리한다.
```

특히 `token`과 `lazy deletion`을 사용하면, 같은 차량이 여러 번 입차/출차/재입차하는 상황에서도 안정적으로 동작한다.

# 네트워크 파일 다운로드 시뮬레이션 문제 정리

## 1. 문제 개요

`N`개의 컴퓨터가 있고, 컴퓨터들은 무방향 링크로 연결된다.

각 링크는 다음 특징을 가진다.

- 두 컴퓨터를 직접 연결한다.
- 방향성이 없다.
- 길이가 있다.
- 양방향으로 데이터 전송이 가능하다.

한 컴퓨터는 다른 컴퓨터가 공유 중인 파일을 다운로드할 수 있다.

단, 다운로드 가능한 경로 길이는 최대 `5000`이다.

```text
최단 경로 길이 <= 5000 → 다운로드 가능
최단 경로 길이 > 5000  → 다운로드 불가능
```

파일이 여러 컴퓨터에서 공유되고 있다면, 해당 공유 파일들을 동시에 다운로드할 수 있다.

공유 파일 1개당 다운로드 속도는 다음과 같다.

```text
1초당 9 크기
```

따라서 거리 5000 이하에 같은 파일을 공유하는 컴퓨터가 `cnt`개 있으면 다운로드 속도는 다음과 같다.

```text
9 * cnt
```

파일 크기가 `size`일 때 다운로드 완료에 걸리는 시간은 다음과 같다.

```python
ceil(size / (9 * cnt))
```

정수 연산으로는 다음처럼 계산한다.

```python
duration = (size + 9 * cnt - 1) // (9 * cnt)
```

---

## 2. API 요약

구현해야 하는 함수는 다음과 같다.

```python
init(N, mShareFileCnt, mFileID, mFileSize)
makeNet(K, mComA, mComB, mDis)
addLink(mTime, mComA, mComB, mDis)
addShareFile(mTime, mComA, mFileID, mSize)
downloadFile(mTime, mComA, mFileID)
getFileSize(mTime, mComA, mFileID)
```

각 함수의 역할은 다음과 같다.

| 함수 | 역할 |
|---|---|
| `init` | 초기 공유 파일 정보 설정 |
| `makeNet` | 초기 링크 추가 |
| `addLink` | 특정 시각에 링크 추가 |
| `addShareFile` | 특정 시각에 공유 파일 추가 |
| `downloadFile` | 특정 컴퓨터가 파일 다운로드 요청 |
| `getFileSize` | 특정 컴퓨터가 가진 파일 크기 확인 |

---

## 3. 중요한 문제 조건

### 3.1 다운로드 요청은 유지된다

`downloadFile()`을 호출했을 때 거리 5000 이하에 공유 파일이 없으면 `0`을 반환한다.

하지만 요청은 사라지지 않는다.

즉, 나중에 링크가 추가되거나 공유 파일이 추가되어 다운로드 가능해지면 자동으로 다운로드가 시작된다.

```text
downloadFile 호출
→ 현재 다운로드 불가능
→ 0 반환
→ 요청은 pending 상태로 유지
→ 나중에 조건 만족 시 자동 다운로드 시작
```

---

### 3.2 링크 추가 또는 공유 파일 추가 시 대기 요청을 확인해야 한다

문제에서 다음 조건이 있다.

```text
링크가 추가되거나 공유 파일이 추가되면,
파일 다운로드를 요청한 컴퓨터는 다운로드 경로의 길이가 5000 이내에
새로운 공유 파일이 있을 경우 다운로드를 바로 시작한다.
```

따라서 다음 처리가 필요하다.

```text
addLink 호출 후:
    모든 pending 요청을 다시 확인

addShareFile 호출 후:
    해당 file_id를 기다리던 pending 요청만 다시 확인
```

---

### 3.3 이미 다운로드 중이면 새 source를 추가하지 않는다

문제에서 다음 조건이 있다.

```text
단, 이미 다운로드 하고 있을 경우는 제외한다.
```

즉, 다운로드가 이미 시작된 요청은 중간에 링크나 공유 파일이 추가되어도 다운로드 속도가 바뀌지 않는다.

예를 들어:

```text
t=10에 source 3개로 다운로드 시작
속도 = 9 * 3

t=15에 같은 파일 source가 2개 더 추가됨
그래도 기존 다운로드 속도는 그대로 9 * 3
```

따라서 다운로드 완료 시간은 다운로드 시작 시점에 고정된다.

---

### 3.4 다운로드 완료된 파일은 공유 파일이 아니다

문제에서 다음 조건이 있다.

```text
파일 다운로드가 완료되어도 다운로드 완료된 파일이 공유되는 것은 아니다.
```

따라서 다운로드가 끝난 컴퓨터는 해당 파일을 보유하게 되지만, 다른 컴퓨터가 그 컴퓨터로부터 다운로드할 수는 없다.

즉, 다운로드 완료 시 다음은 해야 한다.

```python
owned_files[com].add(file_id)
```

하지만 다음은 하면 안 된다.

```python
file_sources[file_id].add(com)  # 하면 안 됨
```

---

## 4. 핵심 상태 관리

이 문제는 그래프 문제이면서 동시에 이벤트 시뮬레이션 문제이다.

따라서 다음 상태들을 관리한다.

---

### 4.1 그래프

```python
graph[com] = [(distance, next_com), ...]
```

컴퓨터 간 링크 정보를 저장한다.

링크는 무방향이므로 양쪽에 모두 추가한다.

```python
graph[a].append((d, b))
graph[b].append((d, a))
```

---

### 4.2 공유 파일 위치

```python
file_sources[file_id] = set(computer_id)
```

해당 파일을 공유 중인 컴퓨터들의 집합이다.

초기 공유 파일과 `addShareFile()`로 추가된 파일만 들어간다.

다운로드 완료된 컴퓨터는 여기에 추가하지 않는다.

---

### 4.3 파일 크기

```python
file_size[file_id] = size
```

파일 ID별 크기를 저장한다.

문제에서 파일 ID가 같으면 동일한 파일임이 보장되므로, 하나의 파일 ID는 항상 같은 크기를 가진다.

---

### 4.4 컴퓨터가 보유한 파일

```python
owned_files[com] = set(file_id)
```

해당 컴퓨터가 가지고 있는 파일 집합이다.

여기에는 다음 파일들이 포함된다.

```text
1. 초기부터 공유하던 파일
2. addShareFile로 추가된 공유 파일
3. 다운로드 완료된 파일
```

단, `owned_files`에 있다고 해서 모두 공유 파일인 것은 아니다.

공유 파일 여부는 반드시 `file_sources`로 판단해야 한다.

---

### 4.5 다운로드 요청 상태

```python
request_state[(com, file_id)] = state
```

상태는 세 가지로 나눈다.

```python
PENDING = 0
ACTIVE = 1
DONE = 2
```

| 상태 | 의미 |
|---|---|
| `PENDING` | 요청은 했지만 아직 다운로드 불가능 |
| `ACTIVE` | 다운로드 중 |
| `DONE` | 다운로드 완료 |

---

### 4.6 대기 요청 목록

```python
pending_by_file[file_id] = set(computer_id)
```

특정 파일을 기다리고 있는 컴퓨터들의 집합이다.

`addShareFile()`이 호출되었을 때, 해당 파일을 기다리던 요청만 빠르게 확인하기 위해 사용한다.

---

### 4.7 다운로드 완료 이벤트

```python
active_heap = [(finish_time, com, file_id), ...]
```

다운로드 완료 이벤트를 시간순으로 처리하기 위한 우선순위 큐다.

각 API 호출 시 먼저 현재 시각까지 완료된 다운로드를 처리한다.

---

## 5. 시간 처리 방식

모든 함수는 시각 `mTime`을 받는다.

문제 조건상 각 함수가 호출될 때는 해당 시각까지 다운로드가 완료된 후 동작해야 한다.

따라서 `addLink`, `addShareFile`, `downloadFile`, `getFileSize`는 모두 시작 부분에서 다음 함수를 호출한다.

```python
_process_until(mTime)
```

이 함수는 `active_heap`에서 완료 시간이 `mTime` 이하인 다운로드를 모두 처리한다.

```python
while active_heap and active_heap[0][0] <= mTime:
    finish_time, com, fid = heapq.heappop(active_heap)
    ...
```

다운로드 완료 시:

```python
request_state[(com, fid)] = DONE
owned_files[com].add(fid)
```

---

## 6. 다운로드 가능 여부 판단

어떤 컴퓨터 `com`이 파일 `fid`를 다운로드할 수 있는지 판단하려면 다음이 필요하다.

```text
com에서 fid를 공유 중인 컴퓨터까지의 최단거리
```

거리 제한은 5000이므로, 다익스트라를 사용할 때 5000을 초과하는 경로는 더 이상 탐색하지 않아도 된다.

```python
if new_cost > LIMIT:
    continue
```

컴퓨터 `com`에서 거리 5000 이하에 있는 `fid` 공유 컴퓨터 개수를 센다.

```python
cnt = 0
for src in file_sources[fid]:
    if dist[src] <= LIMIT:
        cnt += 1
```

`cnt == 0`이면 다운로드 불가능하다.

`cnt > 0`이면 다운로드를 시작할 수 있다.

---

## 7. 제한 다익스트라

링크 길이가 있으므로 단순 BFS가 아니라 다익스트라를 사용한다.

단, 거리 5000 이내의 컴퓨터만 필요하므로 제한 다익스트라를 사용한다.

```python
LIMIT = 5000
```

핵심은 다음과 같다.

```python
if cost > LIMIT:
    break

if new_cost > LIMIT:
    continue
```

다익스트라의 결과는 다음 의미를 가진다.

```python
dist[i] = start에서 i번 컴퓨터까지의 최단거리
```

단, 5000을 초과하는 노드는 `INF`로 남아 있을 수 있다.

---

## 8. 거리 캐싱

동일한 컴퓨터에서 여러 번 거리를 확인할 수 있으므로, 다익스트라 결과를 캐싱할 수 있다.

```python
dist_cache[start] = (graph_version, dist)
```

그래프가 바뀌지 않았다면 캐시를 재사용한다.

링크가 추가되면 그래프가 바뀌므로 `graph_version`을 증가시키고 캐시를 비운다.

```python
graph_version += 1
dist_cache.clear()
```

주의할 점:

```text
공유 파일 추가는 그래프 구조를 바꾸지 않는다.
따라서 dist_cache를 지울 필요가 없다.
```

---

## 9. 함수별 동작 정리

### 9.1 init

초기 상태를 설정한다.

```text
1. graph 초기화
2. file_sources 초기화
3. file_size 초기화
4. owned_files 초기화
5. 요청 상태 초기화
6. 완료 이벤트 heap 초기화
```

초기 공유 파일은 `file_sources`와 `owned_files`에 모두 추가한다.

---

### 9.2 makeNet

초기 링크를 추가한다.

```text
1. 주어진 K개의 링크를 graph에 추가
2. graph_version 증가
3. dist_cache 초기화
```

`makeNet`은 `init()` 직후 1번만 호출되며 현재 시각은 0이다.

---

### 9.3 addLink

특정 시각에 링크를 추가한다.

순서는 다음과 같다.

```text
1. mTime까지 완료된 다운로드 처리
2. 링크 추가
3. graph_version 증가
4. dist_cache 초기화
5. 모든 pending 요청을 다시 확인
```

링크 추가는 특정 파일 하나에만 영향을 주는 것이 아니라, 모든 pending 요청의 거리 조건을 바꿀 수 있다.

따라서 모든 pending 요청을 확인한다.

---

### 9.4 addShareFile

특정 시각에 공유 파일을 추가한다.

순서는 다음과 같다.

```text
1. mTime까지 완료된 다운로드 처리
2. file_sources에 공유 컴퓨터 추가
3. owned_files에 파일 추가
4. 해당 file_id를 기다리던 pending 요청만 다시 확인
```

공유 파일 추가는 특정 `file_id`에만 영향을 주므로, 전체 pending을 볼 필요는 없다.

---

### 9.5 downloadFile

특정 컴퓨터가 특정 파일 다운로드를 요청한다.

순서는 다음과 같다.

```text
1. mTime까지 완료된 다운로드 처리
2. 요청 상태를 PENDING으로 등록
3. 현재 거리 5000 이하의 공유 파일 개수 확인
4. 가능하면 다운로드 시작
5. 다운로드에 사용하는 공유 파일 개수 반환
6. 불가능하면 0 반환
```

반환값은 다운로드 완료 여부가 아니라, 다운로드 시작 시 사용한 공유 파일 개수이다.

---

### 9.6 getFileSize

특정 컴퓨터가 특정 파일을 가지고 있는지 확인한다.

순서는 다음과 같다.

```text
1. mTime까지 완료된 다운로드 처리
2. 해당 컴퓨터가 파일을 보유하고 있으면 크기 반환
3. 없으면 0 반환
```

파일 보유 여부는 `owned_files`로 판단한다.

---

## 10. 전체 코드

```python
import heapq
from collections import defaultdict

LIMIT = 5000
INF = 10 ** 18

PENDING = 0
ACTIVE = 1
DONE = 2

N = 0
graph = []

# file_id -> file_size
file_size = {}

# file_id -> set(computer)
# 실제 공유 중인 파일 위치
file_sources = defaultdict(set)

# computer -> set(file_id)
# 컴퓨터가 보유한 파일
# 공유 파일 + 다운로드 완료 파일 모두 포함
owned_files = defaultdict(set)

# (computer, file_id) -> state
request_state = {}

# (computer, file_id) -> finish_time
request_finish = {}

# file_id -> set(computer)
pending_by_file = defaultdict(set)

# (finish_time, computer, file_id)
active_heap = []

# 그래프 변경 버전
graph_version = 0

# start_computer -> (graph_version, dist)
dist_cache = {}


def init(n, mShareFileCnt, mFileID, mFileSize):
    global N, graph
    global file_size, file_sources, owned_files
    global request_state, request_finish, pending_by_file, active_heap
    global graph_version, dist_cache

    N = n
    graph = [[] for _ in range(N + 1)]

    file_size = {}
    file_sources = defaultdict(set)
    owned_files = defaultdict(set)

    request_state = {}
    request_finish = {}
    pending_by_file = defaultdict(set)
    active_heap = []

    graph_version = 0
    dist_cache = {}

    for i in range(N):
        com = i + 1

        for k in range(mShareFileCnt[i]):
            fid = mFileID[i][k]
            size = mFileSize[i][k]

            file_size[fid] = size
            file_sources[fid].add(com)
            owned_files[com].add(fid)


def makeNet(K, mComA, mComB, mDis):
    global graph_version, dist_cache

    for i in range(K):
        a = mComA[i]
        b = mComB[i]
        d = mDis[i]

        graph[a].append((d, b))
        graph[b].append((d, a))

    graph_version += 1
    dist_cache.clear()


def _process_until(mTime):
    """
    mTime 시각까지 완료된 다운로드를 모두 처리한다.
    """
    while active_heap and active_heap[0][0] <= mTime:
        finish_time, com, fid = heapq.heappop(active_heap)
        key = (com, fid)

        # 낡은 이벤트 방어
        if request_state.get(key) != ACTIVE:
            continue

        if request_finish.get(key) != finish_time:
            continue

        request_state[key] = DONE
        owned_files[com].add(fid)

        # 중요:
        # 다운로드 완료 파일은 공유 파일이 아니므로
        # file_sources[fid].add(com)을 하면 안 된다.


def _get_dist(start):
    """
    start 컴퓨터에서 다른 컴퓨터까지의 최단거리.
    거리 5000 이하만 필요하므로 제한 다익스트라를 사용한다.
    """
    cached = dist_cache.get(start)

    if cached is not None:
        ver, dist = cached
        if ver == graph_version:
            return dist

    dist = [INF] * (N + 1)
    dist[start] = 0

    hq = [(0, start)]

    while hq:
        cost, node = heapq.heappop(hq)

        if cost > dist[node]:
            continue

        if cost > LIMIT:
            break

        for w, nxt in graph[node]:
            new_cost = cost + w

            if new_cost > LIMIT:
                continue

            if new_cost < dist[nxt]:
                dist[nxt] = new_cost
                heapq.heappush(hq, (new_cost, nxt))

    dist_cache[start] = (graph_version, dist)

    return dist


def _count_sources(com, fid):
    """
    com에서 거리 5000 이하에 있는 fid 공유 파일 개수를 반환한다.
    """
    if fid not in file_sources:
        return 0

    dist = _get_dist(com)

    cnt = 0

    for src in file_sources[fid]:
        if dist[src] <= LIMIT:
            cnt += 1

    return cnt


def _start_download_if_possible(mTime, com, fid):
    """
    pending 상태의 요청을 다운로드 시작 가능한지 확인한다.
    가능하면 ACTIVE로 바꾸고 완료 이벤트를 heap에 넣는다.
    반환값은 다운로드에 사용하는 공유 파일 개수이다.
    """
    key = (com, fid)

    if request_state.get(key) != PENDING:
        return 0

    cnt = _count_sources(com, fid)

    if cnt == 0:
        return 0

    size = file_size[fid]
    rate = 9 * cnt
    duration = (size + rate - 1) // rate
    finish_time = mTime + duration

    request_state[key] = ACTIVE
    request_finish[key] = finish_time

    pending_by_file[fid].discard(com)

    heapq.heappush(active_heap, (finish_time, com, fid))

    return cnt


def _try_start_pending_for_file(mTime, fid):
    """
    특정 파일 fid를 기다리던 pending 요청들을 다시 확인한다.
    addShareFile 이후에 사용한다.
    """
    if fid not in pending_by_file:
        return

    waiters = list(pending_by_file[fid])

    for com in waiters:
        _start_download_if_possible(mTime, com, fid)

    if not pending_by_file[fid]:
        del pending_by_file[fid]


def _try_start_all_pending(mTime):
    """
    링크 추가 후에는 모든 pending 요청의 가능성이 바뀔 수 있으므로
    전체 pending 요청을 다시 확인한다.
    """
    fids = list(pending_by_file.keys())

    for fid in fids:
        waiters = list(pending_by_file[fid])

        for com in waiters:
            _start_download_if_possible(mTime, com, fid)

        if fid in pending_by_file and not pending_by_file[fid]:
            del pending_by_file[fid]


def addLink(mTime, mComA, mComB, mDis):
    global graph_version, dist_cache

    _process_until(mTime)

    graph[mComA].append((mDis, mComB))
    graph[mComB].append((mDis, mComA))

    graph_version += 1
    dist_cache.clear()

    # 링크 추가 후 pending 요청이 새로 가능해질 수 있다.
    _try_start_all_pending(mTime)


def addShareFile(mTime, mComA, mFileID, mSize):
    _process_until(mTime)

    file_size[mFileID] = mSize
    file_sources[mFileID].add(mComA)
    owned_files[mComA].add(mFileID)

    # 해당 파일을 기다리던 pending 요청만 확인하면 된다.
    _try_start_pending_for_file(mTime, mFileID)


def downloadFile(mTime, mComA, mFileID):
    _process_until(mTime)

    key = (mComA, mFileID)

    # 일반적으로 같은 요청이 중복으로 들어오지 않는다고 가정할 수 있지만,
    # 방어적으로 처리한다.
    if key in request_state:
        if request_state[key] == PENDING:
            return _start_download_if_possible(mTime, mComA, mFileID)

        if request_state[key] == ACTIVE:
            return 0

        if request_state[key] == DONE:
            return 0

    request_state[key] = PENDING
    pending_by_file[mFileID].add(mComA)

    cnt = _start_download_if_possible(mTime, mComA, mFileID)

    return cnt


def getFileSize(mTime, mComA, mFileID):
    _process_until(mTime)

    if mFileID in owned_files[mComA]:
        return file_size[mFileID]

    return 0
```

---

## 11. 예시 흐름

파일 크기가 1000이고, 거리 5000 이하에 같은 파일을 공유하는 컴퓨터가 5개 있다고 하자.

```text
cnt = 5
rate = 9 * 5 = 45
duration = ceil(1000 / 45) = 23
```

따라서 `mTime = 10`에 다운로드를 시작하면 완료 시각은 다음과 같다.

```text
finish_time = 10 + 23 = 33
```

이 이벤트를 heap에 저장한다.

```python
heapq.heappush(active_heap, (33, com, file_id))
```

이후 `mTime >= 33`인 API 호출이 들어오면 `_process_until(mTime)`에서 다운로드 완료를 처리한다.

---

## 12. 실수하기 쉬운 포인트

### 12.1 다운로드 실패 요청도 유지해야 한다

`downloadFile()`에서 현재 다운로드 가능한 공유 파일이 없다고 해서 요청을 버리면 안 된다.

```python
request_state[(com, fid)] = PENDING
pending_by_file[fid].add(com)
```

을 유지해야 한다.

---

### 12.2 addLink 후에는 전체 pending을 확인해야 한다

링크 추가는 모든 파일 요청의 거리 조건을 바꿀 수 있다.

따라서 특정 파일만 보면 안 된다.

---

### 12.3 addShareFile 후에는 해당 파일 pending만 확인하면 된다

공유 파일 추가는 특정 파일 ID에만 영향을 준다.

따라서 `pending_by_file[mFileID]`만 확인하면 된다.

---

### 12.4 다운로드 완료 파일은 공유 파일이 아니다

완료 시:

```python
owned_files[com].add(fid)
```

만 해야 한다.

아래 코드는 틀린 처리이다.

```python
file_sources[fid].add(com)
```

---

### 12.5 다운로드 중에는 source 개수를 갱신하지 않는다

다운로드가 시작된 후 새 링크나 새 공유 파일이 추가되어도 이미 진행 중인 다운로드의 속도는 변하지 않는다.

완료 시간은 시작 시점의 `cnt`로 고정한다.

---

### 12.6 getFileSize는 공유 파일과 다운로드 완료 파일 모두 반환 가능

`getFileSize()`는 컴퓨터가 해당 파일을 가지고 있으면 크기를 반환한다.

즉, 초기 공유 파일, `addShareFile()`로 추가된 파일, 다운로드 완료 파일 모두 해당된다.

따라서 `owned_files`를 기준으로 판단한다.

---

## 13. 시간복잡도

### 제한 다익스트라

컴퓨터 수:

```text
N <= 1000
```

초기 링크 수:

```text
K <= 2000
```

링크 추가도 존재한다.

각 거리 계산은 제한 다익스트라로 수행한다.

```text
O(E log N)
```

하지만 거리 5000을 초과하는 경로는 확장하지 않으므로 실제 탐색량은 줄어든다.

### pending 확인

`addLink()`는 모든 pending 요청을 다시 확인할 수 있으므로 비용이 클 수 있다.

```text
O(대기 요청 수 * 제한 다익스트라 비용)
```

하지만 거리 캐시를 사용하면 같은 시작 컴퓨터에 대한 다익스트라는 재사용할 수 있다.

즉, pending 요청이 많아도 시작 컴퓨터가 같으면 비용을 줄일 수 있다.

---

## 14. 핵심 결론

이 문제는 단순 최단거리 문제가 아니라 다음이 결합된 문제이다.

```text
1. 동적 그래프
2. 거리 5000 제한 다익스트라
3. 다운로드 요청 상태 관리
4. 완료 이벤트 시뮬레이션
5. pending 요청 자동 시작 처리
```

가장 중요한 구현 포인트는 다음 4가지이다.

```text
1. 각 API 시작 시 _process_until(mTime)으로 완료 이벤트를 먼저 처리한다.
2. downloadFile에서 실패한 요청도 PENDING으로 유지한다.
3. addLink 후에는 모든 pending 요청을 다시 확인한다.
4. 다운로드 완료 파일은 공유 파일이 아니므로 file_sources에 추가하지 않는다.
```

이 구조를 지키면 전체 시뮬레이션을 안정적으로 구현할 수 있다.

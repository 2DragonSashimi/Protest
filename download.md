# 네트워크 파일 다운로드 문제 정리

## 1. 문제 핵심

컴퓨터들이 무방향 링크로 연결되어 있고, 한 컴퓨터는 다른 컴퓨터가 공유 중인 파일을 다운로드할 수 있다.

단, 다운로드 가능한 공유 파일은 다음 조건을 만족해야 한다.

```text
다운로드 요청 컴퓨터와 공유 컴퓨터 사이의 최단거리 <= 5000
```

같은 파일이 여러 컴퓨터에 공유되어 있으면 동시에 다운로드할 수 있다.

```text
공유 source 1개당 초당 9 크기 다운로드
source가 k개면 초당 9 * k 다운로드
```

중요한 점:

```text
링크가 추가되거나 공유 파일이 추가되면,
이미 다운로드 요청한 컴퓨터가 새롭게 접근 가능한 source를 추가로 사용한다.
```

따라서 다운로드 완료 시간을 처음에 고정하면 안 된다.

---

## 2. 처음에 잘못 생각하기 쉬운 부분

처음에는 다음처럼 생각할 수 있다.

```text
downloadFile 호출
→ 현재 source 개수 cnt 계산
→ 완료 시간 finish_time 계산
→ heap에 완료 이벤트 저장
```

하지만 이 방식은 틀릴 수 있다.

왜냐하면 다운로드 도중에 새 링크나 새 공유 파일이 추가되면 source 개수가 증가할 수 있기 때문이다.

예를 들어:

```text
t=10 : source 2개로 다운로드 시작
t=20 : 새 source 1개 추가
t=30 : 파일 크기 조회
```

이면 다운로드량은 다음처럼 계산해야 한다.

```text
t=10~20 : source 2개 * 10초 * 9
t=20~30 : source 3개 * 10초 * 9
```

즉, 완료 시간을 미리 정하는 것이 아니라, **필요할 때 현재까지 받은 양을 누적 계산**해야 한다.

---

## 3. 핵심 아이디어: Lazy Update

이 문제는 다운로드 상태를 다음 형태로 관리한다.

```python
downloading[com][fid] = [downloaded, sources, last_time]
```

각 값의 의미는 다음과 같다.

| 값 | 의미 |
|---|---|
| `downloaded` | 현재까지 다운로드된 크기 |
| `sources` | 현재 다운로드에 사용 중인 공유 컴퓨터 set |
| `last_time` | 마지막으로 다운로드량을 갱신한 시각 |

예를 들어:

```python
downloading[3][100] = [270, {1, 5}, 20]
```

의미는 다음과 같다.

```text
3번 컴퓨터가 100번 파일을 다운로드 중
현재까지 270만큼 받음
현재 source는 1번, 5번
마지막 갱신 시각은 20
```

현재 시각이 `mTime`이라면, 갱신 공식은 다음과 같다.

```python
downloaded += len(sources) * (mTime - last_time) * 9
last_time = mTime
```

즉:

```text
추가 다운로드량 = source 개수 * 지난 시간 * 9
```

---

## 4. 필요한 자료구조

### 4.1 그래프

```python
graph[com] = [(next_com, distance), ...]
```

무방향 링크이므로 양쪽에 모두 추가한다.

```python
graph[a].append((b, d))
graph[b].append((a, d))
```

---

### 4.2 파일 크기

```python
file_size[fid] = size
```

파일 ID별 크기를 저장한다.

---

### 4.3 공유 파일 위치

```python
share_file[fid] = {com1, com2, ...}
```

해당 파일을 공유 중인 컴퓨터 집합이다.

주의:

```text
다운로드 완료된 파일은 공유 파일이 아니다.
```

따라서 다운로드가 완료되어도 `share_file[fid]`에 그 컴퓨터를 추가하면 안 된다.

---

### 4.4 다운로드 진행 정보

```python
downloading[com][fid] = [downloaded, sources, last_time]
```

다운로드 요청을 한 컴퓨터의 현재 다운로드 상태를 저장한다.

---

### 4.5 파일별 요청자 목록

```python
req_file[fid] = {com1, com2, ...}
```

해당 파일을 요청했고, 아직 다운로드 완료되지 않은 컴퓨터 집합이다.

`addLink()`나 `addShareFile()`에서 새롭게 source를 추가할 대상을 빠르게 찾기 위해 사용한다.

완료되면 `req_file[fid]`에서 제거한다.

---

## 5. 상태 해석

`downloading[com][fid]`가 존재한다는 것은 다음 의미이다.

```text
com 컴퓨터가 fid 파일 다운로드를 요청한 적이 있다.
```

그 안의 `sources` 상태에 따라 의미가 나뉜다.

```text
sources가 비어 있음:
    요청은 했지만 아직 다운로드 가능한 source가 없음

sources가 비어 있지 않음:
    해당 source들로 다운로드 중

downloaded == file_size[fid]:
    다운로드 완료
```

---

## 6. 다익스트라

링크에 길이가 있으므로 BFS가 아니라 다익스트라를 사용한다.

단, 필요한 것은 거리 5000 이하의 컴퓨터뿐이다.

따라서 5000을 초과하는 경로는 더 이상 확장하지 않는다.

```python
if nd > LIMIT:
    continue
```

또 heap에서 꺼낸 최단거리가 이미 5000을 넘으면 이후도 전부 5000 초과이므로 종료할 수 있다.

```python
if cur_dist > LIMIT:
    break
```

---

## 7. API별 로직

## 7.1 downloadFile

다운로드 요청이 들어오면 다음을 수행한다.

```text
1. 요청 컴퓨터 기준으로 다익스트라 수행
2. 거리 5000 이하의 공유 source를 찾음
3. downloading[com][fid] 생성
4. req_file[fid]에 com 추가
5. 현재 사용 가능한 source 개수 반환
```

초기 상태:

```python
downloading[com][fid] = [0, source_set, mTime]
```

만약 source가 없다면 `source_set`은 빈 set이고, 반환값은 0이다.

하지만 요청은 유지된다.

---

## 7.2 getFileSize

파일 크기 조회는 다음 순서이다.

```text
1. 해당 컴퓨터가 원래 공유 파일로 가지고 있으면 전체 크기 반환
2. 다운로드 요청 기록이 없으면 0 반환
3. 다운로드 요청 기록이 있으면 mTime까지 받은 양을 갱신
4. 현재 다운로드된 크기 반환
```

아직 다운로드 중이어도 0이 아니라 **현재까지 받은 크기**를 반환한다.

파일 크기 이상 받았으면 파일 크기로 cap 한다.

```python
if downloaded >= file_size[fid]:
    downloaded = file_size[fid]
```

---

## 7.3 addShareFile

새 공유 파일이 추가되면 다음을 수행한다.

```text
1. share_file에 새 source 추가
2. 해당 파일을 요청 중인 컴퓨터들을 확인
3. 새 source와 거리 5000 이하인 요청자에게 source 추가
```

중요한 순서:

```text
새 source를 추가하기 전에,
기존 source들로 mTime까지 받은 양을 먼저 갱신한다.
```

즉:

```python
update_download(mTime, com, fid)
sources.add(new_source)
```

순서여야 한다.

그래야 새 source가 과거 시간까지 소급 적용되지 않는다.

---

## 7.4 addLink

새 링크가 추가되면, 기존에 멀어서 못 쓰던 source가 새로 5000 이내에 들어올 수 있다.

단순하게는 모든 요청자마다 다익스트라를 돌릴 수 있지만, 시간 초과가 날 수 있다.

최적화 핵심:

```text
새 링크 A-B가 추가되었을 때,
새롭게 가능해지는 경로는 반드시 그 새 링크를 지난다.
```

새 링크가 `A --w-- B`라고 하자.

요청자 `u`, 공유 source `v`에 대해 새 링크를 사용하는 경로는 두 가지이다.

```text
u → A → 새 링크 → B → v
u → B → 새 링크 → A → v
```

무방향 그래프이므로 새 링크 추가 전 그래프에서:

```python
distA = dijkstra(A)
distB = dijkstra(B)
```

를 구하면 된다.

그러면 새 링크를 통해 `u`와 `v`가 5000 이내가 되는 조건은:

```python
distA[u] + w + distB[v] <= 5000
```

또는:

```python
distB[u] + w + distA[v] <= 5000
```

이다.

공통으로 `w`가 들어가므로 코드에서는 이렇게 쓸 수 있다.

```python
limit = 5000 - w

if min(distA[u] + distB[v], distB[u] + distA[v]) <= limit:
    source 추가 가능
```

주의:

```text
distA, distB는 반드시 새 링크 추가 전 그래프 기준이어야 한다.
```

그래서 순서는 다음과 같다.

```text
1. distA = dijkstra(A)
2. distB = dijkstra(B)
3. graph에 새 링크 추가
4. distA/distB를 이용해서 새 source 후보 확인
```

---

## 8. 전체 코드

```python
from typing import List
import heapq
from collections import defaultdict

LIMIT = 5000
INF = 10 ** 18
SPEED = 9

N = 0
graph = []

file_size = {}
share_file = defaultdict(set)

# downloading[com][fid] = [downloaded, sources, last_time]
downloading = []

# req_file[fid] = 아직 다운로드 완료되지 않은 요청자 set
req_file = defaultdict(set)


def init(n: int, mShareFileCnt: List[int], mFileID: List[List[int]], mFileSize: List[List[int]]) -> None:
    global N, graph, file_size, share_file, downloading, req_file

    N = n
    graph = [[] for _ in range(N + 1)]

    file_size = {}
    share_file = defaultdict(set)
    downloading = [dict() for _ in range(N + 1)]
    req_file = defaultdict(set)

    for com in range(1, N + 1):
        cnt = mShareFileCnt[com - 1]

        for i in range(cnt):
            fid = mFileID[com - 1][i]
            size = mFileSize[com - 1][i]

            file_size[fid] = size
            share_file[fid].add(com)


def makeNet(K: int, mComA: List[int], mComB: List[int], mDis: List[int]) -> None:
    for i in range(K):
        a = mComA[i]
        b = mComB[i]
        d = mDis[i]

        graph[a].append((b, d))
        graph[b].append((a, d))


def dijkstra(start: int):
    dist = [INF] * (N + 1)
    dist[start] = 0

    hq = [(0, start)]

    while hq:
        cur_dist, cur = heapq.heappop(hq)

        if cur_dist != dist[cur]:
            continue

        if cur_dist > LIMIT:
            break

        for nxt, w in graph[cur]:
            nd = cur_dist + w

            if nd > LIMIT:
                continue

            if nd < dist[nxt]:
                dist[nxt] = nd
                heapq.heappush(hq, (nd, nxt))

    return dist


def update_download(mTime: int, com: int, fid: int) -> None:
    """
    com이 fid를 마지막 갱신 시각부터 mTime까지 얼마나 받았는지 누적한다.
    """
    info = downloading[com][fid]

    downloaded = info[0]
    sources = info[1]
    last_time = info[2]

    total_size = file_size[fid]

    if downloaded >= total_size:
        info[0] = total_size
        return

    downloaded += len(sources) * (mTime - last_time) * SPEED

    if downloaded >= total_size:
        downloaded = total_size

        if fid in req_file:
            req_file[fid].discard(com)

            if not req_file[fid]:
                del req_file[fid]

    info[0] = downloaded
    info[2] = mTime


def downloadFile(mTime: int, mComA: int, mFileID: int) -> int:
    """
    mComA가 mFileID 다운로드 요청.

    현재 접근 가능한 source를 찾아 등록하고,
    사용 가능한 source 개수를 반환한다.
    """
    dist = dijkstra(mComA)

    sources = set()

    for src in share_file[mFileID]:
        if src == mComA:
            continue

        if dist[src] <= LIMIT:
            sources.add(src)

    downloading[mComA][mFileID] = [0, sources, mTime]
    req_file[mFileID].add(mComA)

    return len(sources)


def getFileSize(mTime: int, mComA: int, mFileID: int) -> int:
    """
    mTime 시각에 mComA가 가진 mFileID 크기를 반환한다.

    1. 공유 파일로 가지고 있으면 전체 크기
    2. 다운로드 요청 기록이 있으면 현재까지 받은 크기
    3. 없으면 0
    """
    if mComA in share_file[mFileID]:
        return file_size[mFileID]

    if mFileID not in downloading[mComA]:
        return 0

    update_download(mTime, mComA, mFileID)

    return downloading[mComA][mFileID][0]


def addShareFile(mTime: int, mComA: int, mFileID: int, mSize: int) -> None:
    """
    mComA에 mFileID 공유 파일 추가.

    이 파일을 요청 중인 컴퓨터들이 새 source를 사용할 수 있는지 확인한다.
    """
    file_size[mFileID] = mSize
    share_file[mFileID].add(mComA)

    if mFileID not in req_file:
        return

    dist = dijkstra(mComA)

    for com in list(req_file[mFileID]):
        if com == mComA:
            continue

        update_download(mTime, com, mFileID)

        if downloading[com][mFileID][0] == file_size[mFileID]:
            continue

        if dist[com] <= LIMIT:
            downloading[com][mFileID][1].add(mComA)


def addLink(mTime: int, mComA: int, mComB: int, mDis: int) -> None:
    """
    새 링크 추가 최적화 버전.

    새 링크 추가 전 그래프 기준으로
    양 끝점에서 다익스트라를 돌린다.
    """
    # 1. 새 링크 추가 전 거리
    distA = dijkstra(mComA)
    distB = dijkstra(mComB)

    # 2. 실제 링크 추가
    graph[mComA].append((mComB, mDis))
    graph[mComB].append((mComA, mDis))

    limit = LIMIT - mDis

    # 3. 아직 완료되지 않은 요청들 확인
    for fid in list(req_file.keys()):
        requesters = list(req_file[fid])
        sources = share_file[fid]

        for com in requesters:
            update_download(mTime, com, fid)

            if downloading[com][fid][0] == file_size[fid]:
                continue

            used_sources = downloading[com][fid][1]

            for src in sources:
                if src == com:
                    continue

                if src in used_sources:
                    continue

                # 새 링크를 통해 com과 src가 5000 이내가 되는지 확인
                # com -> A -> B -> src
                # com -> B -> A -> src
                if min(
                    distA[com] + distB[src],
                    distB[com] + distA[src]
                ) <= limit:
                    used_sources.add(src)
```

---

## 9. 핵심 로직 요약

이 문제는 다음 3줄로 요약된다.

```python
downloaded += len(sources) * (mTime - last_time) * 9
last_time = mTime
sources.add(new_source)
```

반드시 순서는 다음과 같아야 한다.

```text
1. 기존 source들로 현재 시각까지 받은 양을 먼저 계산
2. last_time을 현재 시각으로 갱신
3. 새롭게 접근 가능한 source를 추가
```

새 source를 먼저 추가하면, 그 source가 과거 시간부터 다운로드한 것처럼 계산되어 틀린다.

---

## 10. addLink 최적화 요약

```text
새 링크 A-B가 추가되었을 때,
새롭게 생기는 경로는 반드시 A-B를 지난다.
```

따라서 모든 요청자마다 다익스트라를 다시 돌릴 필요가 없다.

```text
기존 단순 방식:
    미완료 요청자마다 dijkstra 수행

최적화 방식:
    A에서 dijkstra 1번
    B에서 dijkstra 1번
```

요청자 `u`, source `v`에 대해:

```python
min(distA[u] + distB[v], distB[u] + distA[v]) + mDis <= 5000
```

이면 새 source로 추가할 수 있다.

코드에서는:

```python
limit = 5000 - mDis

if min(distA[u] + distB[v], distB[u] + distA[v]) <= limit:
    used_sources.add(v)
```

로 처리한다.

---

## 11. 실수하기 쉬운 포인트

### 11.1 다운로드 완료 시간을 미리 계산하면 안 됨

source가 중간에 추가될 수 있으므로 `finish_time`을 처음에 고정하면 틀릴 수 있다.

---

### 11.2 getFileSize는 현재까지 받은 크기를 반환함

완료 전이면 0이 아니라 현재까지 다운로드된 크기를 반환한다.

---

### 11.3 다운로드 완료 파일은 공유 파일이 아님

다운로드 완료 후에도 `share_file[fid].add(com)`을 하면 안 된다.

---

### 11.4 새 source 추가 전 반드시 다운로드량 갱신

```python
update_download(mTime, com, fid)
sources.add(new_source)
```

순서여야 한다.

---

### 11.5 addLink의 다익스트라는 링크 추가 전 기준

새 링크 추가 전 그래프에서 `distA`, `distB`를 구해야 한다.

```python
distA = dijkstra(A)
distB = dijkstra(B)

graph[A].append((B, w))
graph[B].append((A, w))
```

순서가 바뀌면 새 링크를 중복 사용한 거리처럼 계산될 수 있다.

---

## 12. 결론

이 문제는 단순한 최단거리 문제가 아니라:

```text
동적 그래프
+
다운로드 source 증가
+
lazy 다운로드량 갱신
```

문제이다.

핵심 자료구조는 다음 세 가지다.

```python
share_file[fid]          # 공유 source 목록
downloading[com][fid]    # 현재 다운로드 상태
req_file[fid]            # 아직 완료되지 않은 요청자 목록
```

그리고 핵심 사고방식은 다음이다.

```text
다운로드 완료 이벤트를 예약하지 않는다.
필요한 시점에 현재까지 받은 양을 계산한다.
새 source는 현재 시각부터만 다운로드에 참여한다.
```
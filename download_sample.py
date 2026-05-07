import heapq
from collections import defaultdict
from typing import List

from answer import owned_files

LIMIT = 5000
INF = 10**17

WAITING = 0
ACTIVE = 1
DONE = 2

N_global = 0
graph = []

file_size = {}

file_sources = defaultdict(set)

owned_files = defaultdict(set)

waiting_by_file = defaultdict(set)

active_heap = []

graph_version = 0

dist_cache = {}


def init(N: int, mShareFileCnt: List[int], mFileID: List[List[int]], mFileSize: List[List[int]]) -> None:
    global N_global, graph
    global file_size, file_sources,owned_files
    global request_state, request_finish, waiting_by_file, active_heap
    global graph_version, dist_cache

    N_global = N
    graph = [[] for _ in range(N_global + 1)]

    file_size = {}
    file_sources = defaultdict(set)
    owned_files = defaultdict(set)

    request_state = {}
    request_finish = {}

    waiting_by_file = defaultdict(set)

    active_heap = []

    for i in range(N_global):
        com = i + 1

        for k in range(mShareFileCnt[i]):
            f_id = mFileID[i][k]
            f_size = mFileSize[i][k]
            file_size[f_id] = f_size
            file_sources[f_id].add(com)
            owned_files[com].add(f_id)

    pass


def makeNet(K: int, mComA: List[int], mComB: List[int], mDis: List[int]) -> None:
    global N_global, graph
    global graph_version, dist_cache

    for k in range(K):
        comA = mComA[k]
        comB = mComB[k]
        dist = mDis[k]
        graph[comA].append((dist,comB))
        graph[comB].append((dist,comA))

    graph_version = 1
    dist_cache = {}
    pass

def update(time):
    while active_heap and active_heap[0][0] <= time:
        finish, com, fid = heapq.heappop(active_heap)

        key = (com, fid)

        owned_files[com].add(fid)
        request_state[key] = DONE



def dijkstra(com_id):
    cached = dist_cache.get(com_id)
    if cached is not None:
        ver, dis = cached
        if ver == graph_version:
            return dis

    distances = [INF for _ in range(N_global + 1)]
    distances[com_id] = 0
    hq = []
    heapq.heappush(hq, (0, com_id))
    while hq:
        dist, com = heapq.heappop(hq)
        if dist > distances[com]:
            continue
        if dist > LIMIT:
            break

        for cost, n_com in graph[com]:
            n_dist = dist + cost

            if n_dist > LIMIT:
                continue

            if n_dist < distances[n_com]:
                distances[n_com] = n_dist
                heapq.heappush(hq, (n_dist, com))

    dist_cache[com_id] = (graph_version, distances)
    return distances

def find_sources(com_id, f_id):
    count = 0
    distances = dijkstra(com_id)
    for com in file_sources[f_id]:
        if distances[com] > LIMIT:
            continue
        count += 1
    return count

def start_download(time, com, fid):
    count = find_sources(com, fid)

    if count == 0:
        return 0

    size = file_size[fid]
    rate = 9*count
    duration = (size + rate - 1)//rate
    finish_time = time + duration

    heapq.heappush(active_heap,(finish_time, com, fid))
    waiting_by_file[fid].remove(com)
    return count



def addLink(mTime: int, mComA: int, mComB: int, mDis: int) -> None:
    global N_global, graph, graph_version, dist_cache
    update(mTime)
    comA = mComA
    comB = mComB
    dist = mDis
    graph[comA].append((dist,comB))
    graph[comB].append((dist,comA))

    graph_version += 1
    dist_cache.clear()
    waiting_files = list(waiting_by_file.keys())

    for file in waiting_files:
        coms = list(waiting_by_file[file])

        for com in coms:
            start_download(mTime, com, file)


    pass


def addShareFile(mTime: int, mComA: int, mFileID: int, mSize: int) -> None:
    update(mTime)

    file_sources[mFileID].add(mComA)
    file_size[mFileID] = mSize
    owned_files[mComA].add(mFileID)

    coms = list(waiting_by_file[mFileID])

    for com in coms:
        start_download(mTime, com, mFileID)

    pass


def downloadFile(mTime: int, mComA: int, mFileID: int) -> int:
    update(mTime)
    waiting_by_file[mFileID].add(mComA)
    coms = start_download(mTime, mComA, mFileID)

    return coms


def getFileSize(mTime: int, mComA: int, mFileID: int) -> int:
    update(mTime)

    if mFileID in owned_files[mComA]:
        return file_size[mFileID]
    return 0

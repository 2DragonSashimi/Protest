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
        # 초기 component에는 대표 좌표의 방향이 하나 들어 있다.
        direction = next(iter(comp["sources"]))

        groups[g] = {
            "dir": direction,
            "area": comp["area"],
            "volume": comp["volume"],
            "pos": comp["pos"],
        }


def melt():
    """
    a. 융해

    현재 height 기준으로 바다와 인접한 얼음들을 먼저 모두 찾고,
    그 뒤 한 번에 높이를 1 감소시킨다.
    """
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
    """
    융해 후 빙하를 다시 찾는다.

    융해로 기존 빙하가 여러 조각으로 나뉠 수 있다.
    나뉜 조각은 원래 빙하의 방향을 그대로 상속한다.
    """
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
    """
    이동 후 병합 방향 결정은 이동 전 상태 기준이다.
    그래서 이동하기 전에 현재 groups 정보를 저장한다.
    """
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
    """
    b. 이동

    모든 얼음 cell을 전체 grid에서 훑는다.
    각 cell은 자신이 속한 group의 방향으로 한 칸 이동한다.

    겹치면 높이가 큰 얼음만 남는다.
    단, 낮아서 사라진 얼음도 충돌에는 참여했으므로
    moved_sources에 source group id를 기록한다.
    """
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
    """
    c. 병합

    이동 후에는 겹치거나 인접한 빙하가 하나로 합쳐진다.
    moved_height 기준으로 다시 component를 찾는다.

    새 빙하의 방향은 병합에 참여한 이전 group들 중
    이동 전 상태 기준 우선순위가 가장 높은 group의 방향을 따른다.
    """
    components, new_gid = collect_components(moved_height, moved_sources)

    new_groups = {}

    for g, comp in enumerate(components):
        sources = comp["sources"]

        best_src = min(
            sources,
            key=lambda src: (
                -pre_info[src]["volume"],      # 부피 큰 것 우선
                pre_info[src]["area"],         # 면적 작은 것 우선
                pre_info[src]["pos"][0],       # Y 작은 것 우선
                pre_info[src]["pos"][1],       # X 작은 것 우선
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

    # 융해 후 방향 상속을 위해 이전 상태 저장
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

    # 융해 후 쪼개진 빙하 재구성
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
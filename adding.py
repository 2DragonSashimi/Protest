import heapq
IDX_MAX = 15000

class RESULT:
    def __init__(self):
        self.cnt = 0
        self.index = [0] * 10
        self.size = [0] * 10

class UnionFind:
    def __init__(self, n):
        self.parent = {}
        self.size = {}
        self.root_table = []
        heapq.heapify(self.root_table)
        self.root_alive = [False for _ in range(IDX_MAX + 1)]
        self.blocks = {}
        self.x1_table = [[] for _ in range(n + 1)]
        self.x2_table = [[] for _ in range(n + 1)]
        self.y1_table = [[] for _ in range(n + 1)]
        self.y2_table = [[] for _ in range(n + 1)]

    def find(self, idx):
        if self.parent[idx] != idx:
            self.root_alive[idx] = False
            self.root_alive[self.parent[idx]] = True
            self.parent[idx] = self.find(self.parent[idx])  # 경로 압축
        return self.parent[idx]

    def union(self, idx1, idx2):
        root1 = self.find(idx1)
        root2 = self.find(idx2)
        # self.root_alive[root1] = True
        # self.root_alive[root2] = True
        # self.root_alive[idx1] = False
        # self.root_alive[idx2] = False
        # print(idx1,idx2,root1,root2)
        # print(self.root_alive[0:n+1])
        if root1 != root2:
            # idx 작은 걸 root로 선택
            if root1 < root2:
                self.parent[root2] = root1
                self.size[root1] += self.size[root2]
                self.parent[idx2] = root1
                self.root_alive[root2] = False
                self.root_alive[root1] = True
                heapq.heappush(self.root_table, (-self.size[root1], root1))
            else:
                self.parent[root1] = root2
                self.size[root2] += self.size[root1]
                self.parent[idx1] = root2
                self.root_alive[root1] = False
                self.root_alive[root2] = True
                heapq.heappush(self.root_table, (-self.size[root2], root2))
                # return root2, self.size[root2]

    def add(self, idx, x1, y1, x2, y2):
        self.parent[idx] = idx
        self.size[idx] = (x2 - x1) * (y2 - y1)
        self.blocks[idx] = (x1, y1, x2, y2)
        self.x1_table[x1].append((idx, y1))
        self.x2_table[x2].append((idx, y1))
        self.y1_table[y1].append((idx, x1))
        self.y2_table[y2].append((idx, x1))
        self.root_alive[idx] = True
        heapq.heappush(self.root_table, (-self.size[idx], idx))

        union_list = self.check_neighbor(x1,y1,x2,y2)
        for neighbor in union_list:
            if self.parent[neighbor] == self.parent[idx]:
                continue
            self.union(neighbor,idx)
            self.find(idx)



    def check_neighbor(self,x1,y1,x2,y2):
        checked_list = set()

        left_check = self.x2_table[x1][:]
        left_list = sorted(left_check, key=lambda x:x[1])
        for idx, _ in left_list:
            a1,b1,a2,b2 = self.blocks[idx]
            if b2 <= y1:
                continue
            if b1 >= y2:
                break
            checked_list.add(idx)

        right_check = self.x1_table[x2][:]
        right_list = sorted(right_check, key=lambda x:x[1])

        for idx, _ in right_list:
            a1,b1,a2,b2 = self.blocks[idx]
            if b2 <= y1:
                continue
            if b1 >= y2:
                break
            checked_list.add(idx)

        up_check = self.y2_table[y1][:]
        up_list = sorted(up_check, key=lambda x:x[1])

        for idx, _ in up_list:
            a1,b1,a2,b2 = self.blocks[idx]
            if a2 <= x1:
                continue
            if a1 >= x2:
                break
            checked_list.add(idx)

        down_check = self.y1_table[y2][:]
        down_list = sorted(down_check, key=lambda x:x[1])

        for idx, _ in down_list:
            a1,b1,a2,b2 = self.blocks[idx]
            if a2 <= x1:
                continue
            if a1 >= x2:
                break
            checked_list.add(idx)

        return checked_list

    def find_top(self):
        count = 0
        i = 0
        top_score = []
        top_idx = set()
        len_top = len(self.root_table)
        while count < 10 and i < len_top:
            m_size, root = self.root_table[i]
            if self.root_alive[root] and root not in top_idx:
                top_idx.add(root)
                top_score.append(-m_size)
                count += 1
            i += 1

        return top_score, top_idx


area = UnionFind(0)
n = 0


def init(N):
    global area,n
    n = N
    area = UnionFind(n)
    pass


def addBlock(index, x1, y1, x2, y2):
    area.add(index,x1,y1,x2,y2)
    root = area.parent[index]
    return area.size[root]


def isSameArea(blockIndex1, blockIndex2):
    root1 = area.parent[blockIndex1]
    root2 = area.parent[blockIndex2]

    return 1 if root1 == root2 else 0


def queryAreaSize(areaIndex):
    root = area.parent[areaIndex]
    return area.size[root]


def queryAreaSizeTop10():
    score, idx = area.find_top()
    res = RESULT()
    blocks = list(idx)
    cnt = len(idx)
    for i in range(cnt):
        res.size[i] = score[i]
        res.index[i] = blocks[i]
    res.cnt = cnt
    return res

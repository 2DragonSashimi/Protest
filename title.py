from typing import List
import heapq

TXT = 0
CMT = 1
REP = 2

nodes = None
user_score = None
root_score = None

text_heap = None
user_heap = None

root_ver = None
user_ver = None

class Node:
    def __init__(self, type, user, text_id, point):
        self.user = user
        self.type = type
        self.text_id = text_id
        self.point = point
        self.root = None
        self.children = []
        self.alive = True

def init() -> None:
    global nodes, user_score, root_score, text_heap, user_heap, root_ver, user_ver

    nodes = {}
    user_score = {}
    root_score = {}

    text_heap = []
    user_heap = []

    root_ver = {}
    user_ver = {}

def update_user(user, point):
    new_score = user_score.get(user,0) + point
    user_score[user] = new_score

    version = user_ver.get(user,0)
    user_ver[user] = version + 1

    if new_score > 0:
        heapq.heappush(user_heap, (-new_score, user, -user_ver[user]))

def update_root(text_id, point):
    new_score = root_score.get(text_id,0) + point
    root_score[text_id] = new_score

    version = root_ver.get(text_id,0)
    root_ver[text_id] = version + 1

    if new_score > 0:
        heapq.heappush(text_heap, (-new_score, text_id, -root_ver[text_id]))

def writeMessage(mUser: str, mID: int, mPoint: int) -> int:
    node = Node(TXT, mUser, mID, mPoint)
    node.root = mID
    nodes[mID] = node
    update_user(node.user, node.point)
    update_root(node.text_id, node.point)

    return user_score[mUser]


def commentTo(mUser: str, mID: int, mTargetID: int, mPoint: int) -> int:
    if nodes[mTargetID].root == mTargetID:
        txtype, root_id = CMT, mTargetID
    else:
        txtype, root_id = REP, nodes[mTargetID].root

    node = Node(txtype, mUser, mID, mPoint)
    node.root = root_id
    nodes[mID] = node
    update_user(node.user, node.point)
    update_root(root_id, node.point)

    return root_score[root_id]

def search(text):
    node = nodes[text]

    if not node.alive:
        return 0

    node.alive = False
    update_user(node.user,-node.point)
    total = node.point

    if node.children:
        for child in node.children:
            child_node = nodes[child]
            if child_node.alive:
                total += search(child)

    return total

def erase(mID: int) -> int:
    node = nodes[mID]
    remove_point = search(mID)
    update_root(node.root, -remove_point)

    if node.root == node.text_id:
        return user_score[node.user]

    else: return root_score[node.root]


def getBestMessages(mBestMessageList: List[int]) -> None:

    count = 0

    while count < 5:
        print(text_heap)
        (now_best, now_text, now_version) = heapq.heappop(text_heap)
        if -now_version != root_ver[now_text]:
            continue
        mBestMessageList.append(now_text)
        count += 1


def getBestUsers(mBestUserList: List[str]) -> None:
    count = 0
    while count < 5:
        print(user_heap)
        (now_best, now_user, now_version) = heapq.heappop(user_heap)
        if -now_version != user_ver[now_user]:
            continue
        mBestUserList.append(now_user)
        count += 1

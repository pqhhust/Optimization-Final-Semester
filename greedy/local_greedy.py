import sys
import random
import time

sys.setrecursionlimit(5000)
input = sys.stdin.buffer.readline


class Council:
    def __init__(self, id):
        self.id = id
        self.theses = []    # ID đồ án (1-based)
        self.teachers = []  # ID giáo viên (1-based)


def solve():
    # 1) ĐỌC DỮ LIỆU
    N, M, K = map(int, input().split())
    a, b, c, d, e, f = map(int, input().split())

    s = [[0] for _ in range(N + 1)]
    for i in range(1, N + 1):
        s[i] = [0] + list(map(int, input().split()))

    g = [[0] for _ in range(N + 1)]
    for i in range(1, N + 1):
        g[i] = [0] + list(map(int, input().split()))

    t = [0] + list(map(int, input().split()))

    # 2) CHECK RÀNG BUỘC
    def check_thesis(u, council_theses, council_teachers):
        if len(council_theses) >= b:
            return False
        for eth in council_theses:
            if s[u][eth] < e:
                return False
        for ete in council_teachers:
            if g[u][ete] < f:
                return False
        for ete in council_teachers:
            if t[u] == ete:
                return False
        return True

    def check_teacher(v, council_theses, council_teachers):
        if len(council_teachers) >= d:
            return False
        for eth in council_theses:
            if g[eth][v] < f:
                return False
        for eth in council_theses:
            if t[eth] == v:
                return False
        return True

    # 3) 1 LẦN XÂY DỰNG (Seed random + greedy + vét cạn)
    def run_one_pass():
        curr_c_thesis = [0] * (N + 1)    # thesis -> council_id (0 nếu chưa gán)
        curr_c_teacher = [0] * (M + 1)   # teacher -> council_id
        councils = [Council(k) for k in range(1, K + 1)]

        council_indices = list(range(K))
        # random chút để đa dạng lời giải
        random.shuffle(council_indices)

        # 3.1) Điền đến MIN (a đồ án, c GV)
        for k_idx in council_indices:
            curr_council = councils[k_idx]

            # Seed thesis (chỗ duy nhất random)
            if not curr_council.theses:
                candidates = [i for i in range(1, N + 1) if curr_c_thesis[i] == 0]
                if candidates:
                    seed = random.choice(candidates)
                    curr_council.theses.append(seed)
                    curr_c_thesis[seed] = curr_council.id

            # Greedy fill teacher -> min c
            while len(curr_council.teachers) < c:
                best_cand = -1
                best_gain = -1
                for j in range(1, M + 1):
                    if curr_c_teacher[j] == 0 and check_teacher(j, curr_council.theses, curr_council.teachers):
                        gain = sum(g[x][j] for x in curr_council.theses)
                        if gain > best_gain:
                            best_gain = gain
                            best_cand = j
                if best_cand != -1:
                    curr_council.teachers.append(best_cand)
                    curr_c_teacher[best_cand] = curr_council.id
                else:
                    break

            # Greedy fill thesis -> min a
            while len(curr_council.theses) < a:
                best_cand = -1
                best_gain = -1
                for i in range(1, N + 1):
                    if curr_c_thesis[i] == 0 and check_thesis(i, curr_council.theses, curr_council.teachers):
                        gain = sum(s[i][x] for x in curr_council.theses)
                        if gain > best_gain:
                            best_gain = gain
                            best_cand = i
                if best_cand != -1:
                    curr_council.theses.append(best_cand)
                    curr_c_thesis[best_cand] = curr_council.id
                else:
                    break

        # 3.2) Điền đến MAX (b đồ án, d GV)
        for k_idx in council_indices:
            curr_council = councils[k_idx]

            # Greedy fill thesis -> max b
            while len(curr_council.theses) < b:
                best_cand = -1
                best_gain = -1
                for i in range(1, N + 1):
                    if curr_c_thesis[i] == 0 and check_thesis(i, curr_council.theses, curr_council.teachers):
                        gain = sum(s[i][x] for x in curr_council.theses)
                        if gain > best_gain:
                            best_gain = gain
                            best_cand = i
                if best_cand != -1:
                    curr_council.theses.append(best_cand)
                    curr_c_thesis[best_cand] = curr_council.id
                else:
                    break

            # Greedy fill teacher -> max d
            while len(curr_council.teachers) < d:
                best_cand = -1
                best_gain = -1
                for j in range(1, M + 1):
                    if curr_c_teacher[j] == 0 and check_teacher(j, curr_council.theses, curr_council.teachers):
                        gain = sum(g[x][j] for x in curr_council.theses)
                        if gain > best_gain:
                            best_gain = gain
                            best_cand = j
                if best_cand != -1:
                    curr_council.teachers.append(best_cand)
                    curr_c_teacher[best_cand] = curr_council.id
                else:
                    break

        # 3.3) Vét cạn (best-fit)
        # Vét đồ án
        unassigned_theses = [i for i in range(1, N + 1) if curr_c_thesis[i] == 0]
        for i in unassigned_theses:
            best_k = -1
            best_gain = -1
            for k_idx in range(K):
                if check_thesis(i, councils[k_idx].theses, councils[k_idx].teachers):
                    gain = sum(s[i][x] for x in councils[k_idx].theses)
                    if gain > best_gain:
                        best_gain = gain
                        best_k = k_idx
            if best_k != -1:
                councils[best_k].theses.append(i)
                curr_c_thesis[i] = councils[best_k].id

        # Vét giáo viên
        unassigned_teachers = [j for j in range(1, M + 1) if curr_c_teacher[j] == 0]
        for j in unassigned_teachers:
            best_k = -1
            best_gain = -1
            for k_idx in range(K):
                if check_teacher(j, councils[k_idx].theses, councils[k_idx].teachers):
                    gain = sum(g[x][j] for x in councils[k_idx].theses)
                    if gain > best_gain:
                        best_gain = gain
                        best_k = k_idx
            if best_k != -1:
                councils[best_k].teachers.append(j)
                curr_c_teacher[j] = councils[best_k].id   

        # Đếm số người được gán (đúng)
        assigned_count = (N - curr_c_thesis[1:].count(0)) + (M - curr_c_teacher[1:].count(0))
        return assigned_count, curr_c_thesis, curr_c_teacher

    # 4) TÍNH ĐIỂM
    def calculate_score(res_th, res_te):
        score = 0
        local_councils = [Council(k) for k in range(1, K + 1)]

        for idx in range(1, N + 1):
            c_id = res_th[idx]
            if c_id > 0:
                local_councils[c_id - 1].theses.append(idx)

        for idx in range(1, M + 1):
            c_id = res_te[idx]
            if c_id > 0:
                local_councils[c_id - 1].teachers.append(idx)

        for council in local_councils:
            cth = council.theses
            cte = council.teachers

            # S: trong hội đồng (thesis-thesis)
            for i in range(len(cth)):
                for j in range(i + 1, len(cth)):
                    score += s[cth[i]][cth[j]]

            # G: thesis-teacher
            for th in cth:
                for te in cte:
                    score += g[th][te]

        return score

    # 5) HILL CLIMBING 
    def hill_climbing(res_th, res_te, max_iter=50, max_time=0.08):
        start_time = time.time()

        councils_th = [[] for i in range(K + 1)]
        councils_te = [[] for i in range(K + 1)]

        for i in range(1, N + 1):
            if res_th[i] > 0:
                councils_th[res_th[i]].append(i)
        for j in range(1, M + 1):
            if res_te[j] > 0:
                councils_te[res_te[j]].append(j)

        current_score = calculate_score(res_th, res_te)

        for i in range(max_iter):
            if time.time() - start_time > max_time:
                break

            op = random.randint(1, 4)

            # 1) Di chuyển 1 giáo viên
            if op == 1:
                te = random.randint(1, M)
                c_from = res_te[te]
                c_to = random.randint(1, K)

                if c_from != 0 and c_from != c_to:
                    if len(councils_te[c_from]) > c and len(councils_te[c_to]) < d:
                        if check_teacher(te, councils_th[c_to], councils_te[c_to]):
                            gain = sum(g[th][te] for th in councils_th[c_to])
                            loss = sum(g[th][te] for th in councils_th[c_from])
                            delta = gain - loss
                            if delta > 0:
                                res_te[te] = c_to
                                councils_te[c_from].remove(te)
                                councils_te[c_to].append(te)
                                current_score += delta

            # 2) Di chuyển 1 luận văn
            elif op == 2:
                th = random.randint(1, N)
                c_from = res_th[th]
                c_to = random.randint(1, K)

                if c_from != 0 and c_from != c_to:
                    if len(councils_th[c_from]) > a and len(councils_th[c_to]) < b:
                        if check_thesis(th, councils_th[c_to], councils_te[c_to]):
                            gain = sum(s[th][x] for x in councils_th[c_to]) + sum(g[th][y] for y in councils_te[c_to])
                            loss = sum(s[th][x] for x in councils_th[c_from] if x != th) + sum(g[th][y] for y in councils_te[c_from])
                            delta = gain - loss
                            if delta > 0:
                                res_th[th] = c_to
                                councils_th[c_from].remove(th)
                                councils_th[c_to].append(th)
                                current_score += delta

            # 3) Đổi chỗ 2 giáo viên
            elif op == 3:
                t1 = random.randint(1, M)
                t2 = random.randint(1, M)
                c1, c2 = res_te[t1], res_te[t2]

                if c1 != 0 and c2 != 0 and c1 != c2:
                    # check chéo
                    if check_teacher(t1, councils_th[c2], [x for x in councils_te[c2] if x != t2]) and \
                       check_teacher(t2, councils_th[c1], [x for x in councils_te[c1] if x != t1]):

                        gain = sum(g[th][t1] for th in councils_th[c2]) + sum(g[th][t2] for th in councils_th[c1])
                        loss = sum(g[th][t1] for th in councils_th[c1]) + sum(g[th][t2] for th in councils_th[c2])
                        delta = gain - loss

                        if delta > 0:
                            res_te[t1], res_te[t2] = c2, c1
                            councils_te[c1].remove(t1); councils_te[c1].append(t2)
                            councils_te[c2].remove(t2); councils_te[c2].append(t1)
                            current_score += delta

            # 4) Đổi chỗ 2 luận văn
            else:
                th1 = random.randint(1, N)
                th2 = random.randint(1, N)
                c1, c2 = res_th[th1], res_th[th2]

                if c1 != 0 and c2 != 0 and c1 != c2:
                    if check_thesis(th1, [x for x in councils_th[c2] if x != th2], councils_te[c2]) and \
                       check_thesis(th2, [x for x in councils_th[c1] if x != th1], councils_te[c1]):

                        gain = (sum(s[th1][x] for x in councils_th[c2] if x != th2) + sum(g[th1][y] for y in councils_te[c2])) + \
                               (sum(s[th2][x] for x in councils_th[c1] if x != th1) + sum(g[th2][y] for y in councils_te[c1]))

                        loss = (sum(s[th1][x] for x in councils_th[c1] if x != th1) + sum(g[th1][y] for y in councils_te[c1])) + \
                               (sum(s[th2][x] for x in councils_th[c2] if x != th2) + sum(g[th2][y] for y in councils_te[c2]))

                        delta = gain - loss
                        if delta > 0:
                            res_th[th1], res_th[th2] = c2, c1
                            councils_th[c1].remove(th1); councils_th[c1].append(th2)
                            councils_th[c2].remove(th2); councils_th[c2].append(th1)
                            current_score += delta

        return res_th, res_te, current_score

    # 6) MULTI-START
    TOTAL_TIME = 30
    start_all = time.time()

    best_thesis_assign = None
    best_teacher_assign = None
    best_assigned = -1
    best_score = -10**18

    while time.time() - start_all < TOTAL_TIME:
        assigned_count, th, te = run_one_pass()

        # hill climb trên bản copy
        th2, te2, sc = hill_climbing(th[:], te[:], max_iter=250, max_time=0.08)

        # Ưu tiên gán được nhiều người trước, sau đó mới xét score
        if assigned_count > best_assigned or (assigned_count == best_assigned and sc > best_score):
            best_assigned = assigned_count
            best_score = sc
            best_thesis_assign = th2[:]
            best_teacher_assign = te2[:]

    
    if best_thesis_assign is None or best_teacher_assign is None:
        _, best_thesis_assign, best_teacher_assign = run_one_pass()

    # 7) IN KẾT QUẢ 
    out = []
    out.append(str(N))
    out.append(" ".join(map(str, best_thesis_assign[1:])))
    out.append(str(M))
    out.append(" ".join(map(str, best_teacher_assign[1:])))
    print(best_score)
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    solve()

import sys
import random
import time

# Tăng giới hạn đệ quy và tối ưu IO
sys.setrecursionlimit(5000)
input = sys.stdin.buffer.readline

class Council:
    def __init__(self, id):
        self.id = id
        self.theses = []    # ID đồ án (1-based)
        self.teachers = []  # ID giáo viên (1-based)

def solve():
    # 1. ĐỌC DỮ LIỆU
    try:
        line1 = input().split()
        if not line1: return
        N, M, K = map(int, line1)
        a, b, c, d, e, f = map(int, input().split())

        s = [[0] for _ in range(N + 1)]
        for i in range(1, N + 1):
            s[i] = [0] + list(map(int, input().split()))

        g = [[0] for _ in range(N + 1)]
        for i in range(1, N + 1):
            g[i] = [0] + list(map(int, input().split()))

        t = [0] + list(map(int, input().split()))
    except ValueError:
        return

    # Hằng số phạt cho Unassigned
    ALPHA = 1000000 

    # 2. CÁC HÀM CHECK RÀNG BUỘC
    def check_thesis(u, council_theses, council_teachers):
        if len(council_theses) >= b: return False
        for eth in council_theses:
            if s[u][eth] < e: return False
        for ete in council_teachers:
            if g[u][ete] < f: return False
        for ete in council_teachers:
            if t[u] == ete: return False
        return True

    def check_teacher(v, council_theses, council_teachers):
        if len(council_teachers) >= d: return False
        for eth in council_theses:
            if g[eth][v] < f: return False
        for eth in council_theses:
            if t[eth] == v: return False
        return True

    # 3. THUẬT TOÁN XÂY DỰNG: PURE GREEDY
    def run_one_pass():
        curr_c_thesis = [0] * (N + 1)
        curr_c_teacher = [0] * (M + 1)
        councils = [Council(k) for k in range(1, K + 1)]

        council_indices = list(range(K))
        random.shuffle(council_indices)

        # 3.1) Điền đến MIN
        for k_idx in council_indices:
            curr_council = councils[k_idx]

            # Random Seed
            if not curr_council.theses:
                candidates = [i for i in range(1, N + 1) if curr_c_thesis[i] == 0]
                if candidates:
                    seed = random.choice(candidates)
                    curr_council.theses.append(seed)
                    curr_c_thesis[seed] = curr_council.id

            # Greedy Teacher -> Min c
            while len(curr_council.teachers) < c:
                best_cand, best_gain = -1, -float('inf')
                for j in range(1, M + 1):
                    if curr_c_teacher[j] == 0 and check_teacher(j, curr_council.theses, curr_council.teachers):
                        gain = sum(g[x][j] for x in curr_council.theses)
                        if gain > best_gain: best_gain, best_cand = gain, j
                if best_cand != -1:
                    curr_council.teachers.append(best_cand)
                    curr_c_teacher[best_cand] = curr_council.id
                else: break

            # Greedy Thesis -> Min a
            while len(curr_council.theses) < a:
                best_cand, best_gain = -1, -float('inf')
                for i in range(1, N + 1):
                    if curr_c_thesis[i] == 0 and check_thesis(i, curr_council.theses, curr_council.teachers):
                        gain = sum(s[i][x] for x in curr_council.theses) + sum(g[i][y] for y in curr_council.teachers)
                        if gain > best_gain: best_gain, best_cand = gain, i
                if best_cand != -1:
                    curr_council.theses.append(best_cand)
                    curr_c_thesis[best_cand] = curr_council.id
                else: break

        # 3.2) Điền đến MAX
        for k_idx in council_indices:
            curr_council = councils[k_idx]
            while len(curr_council.theses) < b:
                best_cand, best_gain = -1, -float('inf')
                for i in range(1, N + 1):
                    if curr_c_thesis[i] == 0 and check_thesis(i, curr_council.theses, curr_council.teachers):
                        gain = sum(s[i][x] for x in curr_council.theses) + sum(g[i][y] for y in curr_council.teachers)
                        if gain > best_gain: best_gain, best_cand = gain, i
                if best_cand != -1:
                    curr_council.theses.append(best_cand)
                    curr_c_thesis[best_cand] = curr_council.id
                else: break

            while len(curr_council.teachers) < d:
                best_cand, best_gain = -1, -float('inf')
                for j in range(1, M + 1):
                    if curr_c_teacher[j] == 0 and check_teacher(j, curr_council.theses, curr_council.teachers):
                        gain = sum(g[x][j] for x in curr_council.theses)
                        if gain > best_gain: best_gain, best_cand = gain, j
                if best_cand != -1:
                    curr_council.teachers.append(best_cand)
                    curr_c_teacher[best_cand] = curr_council.id
                else: break

        # 3.3) Vét cạn
        unassigned_theses = [i for i in range(1, N + 1) if curr_c_thesis[i] == 0]
        random.shuffle(unassigned_theses)
        for i in unassigned_theses:
            best_k, best_gain = -1, -float('inf')
            for k_idx in range(K):
                if check_thesis(i, councils[k_idx].theses, councils[k_idx].teachers):
                    gain = sum(s[i][x] for x in councils[k_idx].theses) + sum(g[i][y] for y in councils[k_idx].teachers)
                    if gain > best_gain: best_gain, best_k = gain, k_idx
            if best_k != -1:
                councils[best_k].theses.append(i)
                curr_c_thesis[i] = councils[best_k].id

        unassigned_teachers = [j for j in range(1, M + 1) if curr_c_teacher[j] == 0]
        random.shuffle(unassigned_teachers)
        for j in unassigned_teachers:
            best_k, best_gain = -1, -float('inf')
            for k_idx in range(K):
                if check_teacher(j, councils[k_idx].theses, councils[k_idx].teachers):
                    gain = sum(g[x][j] for x in councils[k_idx].theses)
                    if gain > best_gain: best_gain, best_k = gain, k_idx
            if best_k != -1:
                councils[best_k].teachers.append(j)
                curr_c_teacher[j] = councils[best_k].id   

        return curr_c_thesis, curr_c_teacher

    # 4. HÀM TÍNH ĐIỂM 
    def calculate_score(res_th, res_te):
        score = 0
        unassigned_th = res_th[1:].count(0)
        unassigned_te = res_te[1:].count(0)
        
        local_councils = [Council(k) for k in range(1, K + 1)]
        for idx in range(1, N + 1):
            if res_th[idx] > 0: local_councils[res_th[idx] - 1].theses.append(idx)
        for idx in range(1, M + 1):
            if res_te[idx] > 0: local_councils[res_te[idx] - 1].teachers.append(idx)

        for council in local_councils:
            cth = council.theses
            cte = council.teachers
            for i in range(len(cth)):
                for j in range(i + 1, len(cth)):
                    score += s[cth[i]][cth[j]]
            for th in cth:
                for te in cte:
                    score += g[th][te]
        
        score -= ALPHA * (unassigned_th + unassigned_te)
        return score

    # 5. HILL CLIMBING 
    def hill_climbing(res_th, res_te, max_iter=100000, max_time=4.0, patience=3000):
        start_time = time.time()
        councils_th = [[] for i in range(K + 1)]
        councils_te = [[] for i in range(K + 1)]

        for i in range(1, N + 1):
            if res_th[i] > 0: councils_th[res_th[i]].append(i)
        for j in range(1, M + 1):
            if res_te[j] > 0: councils_te[res_te[j]].append(j)

        current_score = calculate_score(res_th, res_te)
        fails = 0
        iter_count = 0

        while iter_count < max_iter and fails < patience:
            if time.time() - start_time > max_time: break
            iter_count += 1
            op = random.randint(1, 4)
            improved = False 

            # Move Teacher
            if op == 1:
                te = random.randint(1, M)
                c_from = res_te[te]
                c_to = random.randint(1, K)
                if c_from != c_to and len(councils_te[c_to]) < d:
                    can_leave = True
                    if c_from != 0 and len(councils_te[c_from]) <= c: can_leave = False
                    if can_leave:
                        if check_teacher(te, councils_th[c_to], councils_te[c_to]):
                            gain = sum(g[th][te] for th in councils_th[c_to])
                            loss = 0 if c_from == 0 else sum(g[th][te] for th in councils_th[c_from])
                            bonus = ALPHA if c_from == 0 else 0
                            if (gain - loss + bonus) > 0:
                                res_te[te] = c_to
                                if c_from != 0: councils_te[c_from].remove(te)
                                councils_te[c_to].append(te)
                                current_score += (gain - loss + bonus)
                                improved = True
            
            # Move Thesis
            elif op == 2:
                th = random.randint(1, N)
                c_from = res_th[th]
                c_to = random.randint(1, K)
                if c_from != c_to and len(councils_th[c_to]) < b:
                    can_leave = True
                    if c_from != 0 and len(councils_th[c_from]) <= a: can_leave = False
                    if can_leave:
                        if check_thesis(th, councils_th[c_to], councils_te[c_to]):
                            gain = sum(s[th][x] for x in councils_th[c_to]) + sum(g[th][y] for y in councils_te[c_to])
                            loss = 0 if c_from == 0 else sum(s[th][x] for x in councils_th[c_from] if x != th) + sum(g[th][y] for y in councils_te[c_from])
                            bonus = ALPHA if c_from == 0 else 0
                            if (gain - loss + bonus) > 0:
                                res_th[th] = c_to
                                if c_from != 0: councils_th[c_from].remove(th)
                                councils_th[c_to].append(th)
                                current_score += (gain - loss + bonus)
                                improved = True

            # Swap Teachers
            elif op == 3:
                t1 = random.randint(1, M); t2 = random.randint(1, M)
                c1, c2 = res_te[t1], res_te[t2]
                if c1 != 0 and c2 != 0 and c1 != c2:
                    if check_teacher(t1, councils_th[c2], [x for x in councils_te[c2] if x != t2]) and \
                       check_teacher(t2, councils_th[c1], [x for x in councils_te[c1] if x != t1]):
                        gain = sum(g[th][t1] for th in councils_th[c2]) + sum(g[th][t2] for th in councils_th[c1])
                        loss = sum(g[th][t1] for th in councils_th[c1]) + sum(g[th][t2] for th in councils_th[c2])
                        if gain - loss > 0:
                            res_te[t1], res_te[t2] = c2, c1
                            councils_te[c1].remove(t1); councils_te[c1].append(t2)
                            councils_te[c2].remove(t2); councils_te[c2].append(t1)
                            current_score += (gain - loss)
                            improved = True
            
            # Swap Theses
            else:
                th1 = random.randint(1, N); th2 = random.randint(1, N)
                c1, c2 = res_th[th1], res_th[th2]
                if c1 != 0 and c2 != 0 and c1 != c2:
                    if check_thesis(th1, [x for x in councils_th[c2] if x != th2], councils_te[c2]) and \
                       check_thesis(th2, [x for x in councils_th[c1] if x != th1], councils_te[c1]):
                        gain = (sum(s[th1][x] for x in councils_th[c2] if x != th2) + sum(g[th1][y] for y in councils_te[c2])) + \
                               (sum(s[th2][x] for x in councils_th[c1] if x != th1) + sum(g[th2][y] for y in councils_te[c1]))
                        loss = (sum(s[th1][x] for x in councils_th[c1] if x != th1) + sum(g[th1][y] for y in councils_te[c1])) + \
                               (sum(s[th2][x] for x in councils_th[c2] if x != th2) + sum(g[th2][y] for y in councils_te[c2]))
                        if gain - loss > 0:
                            res_th[th1], res_th[th2] = c2, c1
                            councils_th[c1].remove(th1); councils_th[c1].append(th2)
                            councils_th[c2].remove(th2); councils_th[c2].append(th1)
                            current_score += (gain - loss)
                            improved = True

            if improved: fails = 0
            else: fails += 1

        return res_th, res_te, current_score

    # 6. MAIN LOOP 
    TOTAL_TIME = 90.0  # Time limit
    MAX_ITER_GREEDY = 500    # Chạy Greedy liên tục 1s để tìm ứng viên tốt nhất
    start_all = time.time()

    best_thesis_assign = None
    best_teacher_assign = None
    best_score = -float('inf')

    while time.time() - start_all < TOTAL_TIME:
        # PHASE 1: BATCH GREEDY (1s)
        batch_start = time.time()
        batch_best_th = None
        batch_best_te = None
        batch_best_score = -float('inf')

        for _ in range(MAX_ITER_GREEDY):
            if time.time() - start_all > TOTAL_TIME: 
                break
                
            curr_th, curr_te = run_one_pass()
            curr_score = calculate_score(curr_th, curr_te)

            if curr_score > batch_best_score:
                batch_best_score = curr_score
                batch_best_th = curr_th[:]
                batch_best_te = curr_te[:]

        # PHASE 2: HILL CLIMBING
        if batch_best_th is not None:
            final_th, final_te, final_sc = hill_climbing(
                batch_best_th, batch_best_te, 
                max_iter=50000, 
                max_time=2.5, 
                patience=1500
            )

            # Update Global Best
            if final_sc > best_score:
                best_score = final_sc
                best_thesis_assign = final_th[:]
                best_teacher_assign = final_te[:]
    
    # Fallback safety
    if best_thesis_assign is None:
        best_thesis_assign, best_teacher_assign = run_one_pass()

    # 7. IN KẾT QUẢ
    out = []
    out.append(str(N))
    out.append(" ".join(map(str, best_thesis_assign[1:])))
    out.append(str(M))
    out.append(" ".join(map(str, best_teacher_assign[1:])))
    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    solve()

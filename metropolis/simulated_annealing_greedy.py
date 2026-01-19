import sys
import random
import time
import math

# =========================================================
# 1. INPUT HANDLING (GIỮ NGUYÊN)
# =========================================================
def input_data():
    try:
        line1 = sys.stdin.read().split()
    except Exception:
        return None
    
    if not line1: return None
    
    iterator = iter(line1)
    
    try:
        N = int(next(iterator))
        M = int(next(iterator))
        K = int(next(iterator))
        
        a = float(next(iterator)); b = float(next(iterator))
        c = float(next(iterator)); d = float(next(iterator))
        e = float(next(iterator)); f = float(next(iterator))
        
        # Convert constraints to appropriate types
        a, b, c, d = int(a), int(b), int(c), int(d)
        
        s_matrix = [[0.0] * (N + 1)] 
        for _ in range(N):
            row = [0.0] + [float(next(iterator)) for _ in range(N)]
            s_matrix.append(row)

        g_matrix = [[0.0] * (M + 1)] 
        for _ in range(N):
            row = [0.0] + [float(next(iterator)) for _ in range(M)]
            g_matrix.append(row)

        t_list = [0] + [int(next(iterator)) for _ in range(N)]
        
        return N, M, K, a, b, c, d, e, f, s_matrix, g_matrix, t_list
        
    except StopIteration:
        return None

# =========================================================
# 2. GRASP INITIALIZER (GIỮ NGUYÊN)
# =========================================================
class GraspInitializer:
    def __init__(self, N, M, K, a, b, c, d, e, f, s, g, t):
        self.N, self.M, self.K = N, M, K
        self.a, self.b, self.c, self.d = a, b, c, d
        self.e, self.f = e, f
        self.s = s
        self.g = g
        self.t = t
        
    class Council:
        def __init__(self, id):
            self.id = id
            self.theses = []   # List ID
            self.teachers = [] # List ID

    def check_thesis_valid(self, u, current_theses, current_teachers):
        if len(current_theses) >= self.b: return False
        for v in current_theses:
            if self.s[u][v] < self.e: return False
        for te in current_teachers:
            if self.g[u][te] < self.f: return False
        if self.t[u] in current_teachers: 
            return False           
        return True

    def check_teacher_valid(self, v, current_theses, current_teachers):
        if len(current_teachers) >= self.d: return False
        for th in current_theses:
            if self.g[th][v] < self.f: return False
        for th in current_theses:
            if self.t[th] == v: return False           
        return True
    
    def calculate_total_score(self, res_th, res_te):
        score = 0
        tmp_councils_th = [[] for _ in range(self.K + 1)]
        tmp_councils_te = [[] for _ in range(self.K + 1)]
        
        for i in range(1, self.N + 1):
            if res_th[i] > 0: tmp_councils_th[res_th[i]].append(i)
        for j in range(1, self.M + 1):
            if res_te[j] > 0: tmp_councils_te[res_te[j]].append(j)
            
        for k in range(1, self.K + 1):
            cth = tmp_councils_th[k]
            cte = tmp_councils_te[k]
            for i_idx in range(len(cth)):
                for j_idx in range(i_idx + 1, len(cth)):
                    score += self.s[cth[i_idx]][cth[j_idx]]
            for th in cth:
                for te in cte:
                    score += self.g[th][te]
        return score

    def run_one_solution(self):
        RCL_SIZE = 4
        curr_th_assign = [0] * (self.N + 1)
        curr_te_assign = [0] * (self.M + 1)
        councils = [self.Council(k) for k in range(1, self.K + 1)]
        council_indices = list(range(self.K))

        # --- PHASE 1: BUILD SKELETON (Min a, Min c) ---
        for idx in council_indices:
            cou = councils[idx]
            if len(cou.theses) == 0:
                pool = [i for i in range(1, self.N+1) if curr_th_assign[i] == 0]
                if pool:
                    seed = random.choice(pool)
                    cou.theses.append(seed)
                    curr_th_assign[seed] = cou.id

            while len(cou.theses) < self.a:
                candidates = []
                for i in range(1, self.N+1):
                    if curr_th_assign[i] == 0:
                        if self.check_thesis_valid(i, cou.theses, cou.teachers): 
                            gain_s = sum(self.s[i][x] for x in cou.theses)
                            gain_g = sum(self.g[i][y] for y in cou.teachers)
                            candidates.append((gain_s + gain_g, i))
                if not candidates: break
                candidates.sort(key=lambda x: x[0], reverse=True)
                top_k = candidates[:RCL_SIZE]
                chosen = random.choice(top_k)[1]
                cou.theses.append(chosen)
                curr_th_assign[chosen] = cou.id

            while len(cou.teachers) < self.c:
                candidates = []
                for j in range(1, self.M+1):
                    if curr_te_assign[j] == 0:
                        if self.check_teacher_valid(j, cou.theses, cou.teachers):
                            gain = sum(self.g[x][j] for x in cou.theses)
                            candidates.append((gain, j))
                if not candidates: break
                candidates.sort(key=lambda x: x[0], reverse=True)
                top_k = candidates[:RCL_SIZE]
                chosen = random.choice(top_k)[1]
                cou.teachers.append(chosen)
                curr_te_assign[chosen] = cou.id

        # --- PHASE 2: FILL REMAINING (Max b, Max d) ---
        random.shuffle(council_indices)
        for idx in council_indices:
            cou = councils[idx]
            while len(cou.teachers) < self.d:
                candidates = []
                for j in range(1, self.M+1):
                    if curr_te_assign[j] == 0:
                        if self.check_teacher_valid(j, cou.theses, cou.teachers):
                            gain_g = sum(self.g[x][j] for x in cou.theses)
                            candidates.append((gain_g, j))
                if not candidates: break
                candidates.sort(key=lambda x: x[0], reverse=True)
                best_cand = candidates[0][1]
                cou.teachers.append(best_cand)
                curr_te_assign[best_cand] = cou.id

            while len(cou.theses) < self.b:
                candidates = []
                for i in range(1, self.N+1):
                    if curr_th_assign[i] == 0:
                        if self.check_thesis_valid(i, cou.theses, cou.teachers):
                            gain_s = sum(self.s[i][x] for x in cou.theses)
                            gain_g = sum(self.g[i][y] for y in cou.teachers)
                            candidates.append((gain_s + gain_g, i))
                if not candidates: break
                candidates.sort(key=lambda x: x[0], reverse=True)
                best_cand = candidates[0][1]
                cou.theses.append(best_cand)
                curr_th_assign[best_cand] = cou.id
                
        cnt = (self.N - curr_th_assign.count(0)) + (self.M - curr_te_assign.count(0))
        return cnt, curr_th_assign, curr_te_assign

    def solve(self, time_limit=5.0):
        best_cnt = -1
        best_score = -1
        best_th_assign = [0] * (self.N + 1)
        best_te_assign = [0] * (self.M + 1)
        
        start_time = time.time()
        
        while True:
            if (time.time() - start_time) > time_limit:
                break
            curr_cnt, curr_th, curr_te = self.run_one_solution()
            
            if curr_cnt > best_cnt:
                best_cnt = curr_cnt
                best_score = self.calculate_total_score(curr_th, curr_te)
                best_th_assign = list(curr_th)
                best_te_assign = list(curr_te)
            elif curr_cnt == best_cnt:
                curr_s = self.calculate_total_score(curr_th, curr_te)
                if curr_s > best_score:
                    best_score = curr_s
                    best_th_assign = list(curr_th)
                    best_te_assign = list(curr_te)
                    
        return best_th_assign, best_te_assign

# =========================================================
# 3. SIMULATED ANNEALING SOLVER (Cải tiến từ Metropolis)
# =========================================================
class SimulatedAnnealingSolver:
    def __init__(self, N, M, K, a, b, c, d, e, f, s_matrix, g_matrix, t_list, init_x=None, init_y=None):
        self.N, self.M, self.K = N, M, K
        self.a, self.b, self.c, self.d = a, b, c, d
        self.e, self.f = e, f
        self.s = s_matrix
        self.g = g_matrix
        self.t = t_list
        
        # --- CẤU HÌNH SIMULATED ANNEALING ---
        self.max_iter = 1000000 
        self.T_start = 1     # Nhiệt độ ban đầu (cho phép khám phá)
        self.T_end = 0.001       # Nhiệt độ kết thúc (hội tụ)
        self.T = self.T_start
        
        # Tính toán hệ số làm nguội (Decay factor) sao cho T giảm từ Start -> End sau Max_Iter
        # Công thức: T_end = T_start * (decay ^ max_iter)
        # -> decay = (T_end / T_start) ^ (1 / max_iter)
        if self.max_iter > 0:
            self.decay = (self.T_end / self.T_start) ** (1.0 / self.max_iter)
        else:
            self.decay = 0.999
        
        # Trọng số phạt
        self.W_count = 12000
        self.W_conflict = 10000
        self.W_sim = 9999
        
        # --- KHỞI TẠO TỪ GREEDY ---
        if init_x and init_y:
            self.x = list(init_x)
            self.y = list(init_y)
            # Greedy có thể chưa gán hết (giá trị 0), fill random
            for i in range(1, N + 1):
                if self.x[i] == 0: self.x[i] = random.randint(1, K)
            for j in range(1, M + 1):
                if self.y[j] == 0: self.y[j] = random.randint(1, K)
        else:
            self.x = [0] + [random.randint(1, K) for _ in range(N)] 
            self.y = [0] + [random.randint(1, K) for _ in range(M)]
        
        # Cấu trúc dữ liệu hỗ trợ Delta Eval
        self.c_p = [[] for _ in range(K + 1)] 
        self.c_t = [[] for _ in range(K + 1)] 
        
        for i in range(1, N + 1):
            self.c_p[self.x[i]].append(i)
        for j in range(1, M + 1):
            self.c_t[self.y[j]].append(j)

        # Đánh giá ban đầu
        self.curr_fitness, self.curr_sim, self.curr_pen = self.evaluate_full()
        
        # Lưu Best Global
        self.best_x = list(self.x)
        self.best_y = list(self.y)
        self.best_fitness = self.curr_fitness

    def get_count_penalty(self, count, min_val, max_val):
        pen = 0
        if count < min_val: pen += (min_val - count) * self.W_count
        if count > max_val: pen += (count - max_val) * self.W_count
        return pen

    def evaluate_full(self):
        total_sim = 0
        penalty = 0
        
        for k in range(1, self.K + 1):
            p_list = self.c_p[k]
            t_list = self.c_t[k]
            p_len = len(p_list)
            t_len = len(t_list)
            
            penalty += self.get_count_penalty(p_len, self.a, self.b)
            penalty += self.get_count_penalty(t_len, self.c, self.d)
            
            for i in range(p_len):
                u = p_list[i]
                for j in range(i+1, p_len):
                    v = p_list[j]
                    sim = self.s[u][v]
                    if sim < self.e: penalty += self.W_sim
                    else: total_sim += sim
                
                for v in t_list:
                    if self.t[u] == v: penalty += self.W_conflict
                    sim = self.g[u][v]
                    if sim < self.f: penalty += self.W_sim
                    else: total_sim += sim
                        
        return total_sim - penalty, total_sim, penalty

    # --- CÁC HÀM TÍNH DELTA (GIỮ NGUYÊN) ---
    def calc_delta_move_proj(self, u, old_c, new_c):
        delta_sim = 0; delta_pen = 0
        old_len = len(self.c_p[old_c]); new_len = len(self.c_p[new_c])
        
        delta_pen -= self.get_count_penalty(old_len, self.a, self.b)
        delta_pen += self.get_count_penalty(old_len - 1, self.a, self.b)
        delta_pen -= self.get_count_penalty(new_len, self.a, self.b)
        delta_pen += self.get_count_penalty(new_len + 1, self.a, self.b)

        for v in self.c_p[old_c]:
            if u == v: continue
            sim = self.s[u][v]
            if sim < self.e: delta_pen -= self.W_sim 
            else: delta_sim -= sim
        for t in self.c_t[old_c]:
            if self.t[u] == t: delta_pen -= self.W_conflict
            sim = self.g[u][t]
            if sim < self.f: delta_pen -= self.W_sim
            else: delta_sim -= sim
        for v in self.c_p[new_c]:
            sim = self.s[u][v]
            if sim < self.e: delta_pen += self.W_sim
            else: delta_sim += sim
        for t in self.c_t[new_c]:
            if self.t[u] == t: delta_pen += self.W_conflict
            sim = self.g[u][t]
            if sim < self.f: delta_pen += self.W_sim
            else: delta_sim += sim
            
        return delta_sim, delta_pen

    def calc_delta_move_teach(self, u, old_c, new_c):
        delta_sim = 0; delta_pen = 0
        old_len = len(self.c_t[old_c]); new_len = len(self.c_t[new_c])
        
        delta_pen -= self.get_count_penalty(old_len, self.c, self.d)
        delta_pen += self.get_count_penalty(old_len - 1, self.c, self.d)
        delta_pen -= self.get_count_penalty(new_len, self.c, self.d)
        delta_pen += self.get_count_penalty(new_len + 1, self.c, self.d)
        
        for p in self.c_p[old_c]:
            if self.t[p] == u: delta_pen -= self.W_conflict
            sim = self.g[p][u]
            if sim < self.f: delta_pen -= self.W_sim
            else: delta_sim -= sim
        for p in self.c_p[new_c]:
            if self.t[p] == u: delta_pen += self.W_conflict
            sim = self.g[p][u]
            if sim < self.f: delta_pen += self.W_sim
            else: delta_sim += sim
            
        return delta_sim, delta_pen

    def solve(self):
        for iteration in range(self.max_iter):
            action_type = random.randint(0, 99)
            candidate = None 
            
            if action_type < 50: # MOVE
                move_target = random.choice(['proj', 'teach'])
                if move_target == 'proj':
                    idx = random.randint(1, self.N)
                    old_c = self.x[idx]
                    new_c = random.randint(1, self.K)
                    while new_c == old_c: new_c = random.randint(1, self.K)
                    d_sim, d_pen = self.calc_delta_move_proj(idx, old_c, new_c)
                    candidate = {'type': 'proj', 'id': idx, 'from': old_c, 'to': new_c, 'd_sim': d_sim, 'd_pen': d_pen}
                else: 
                    idx = random.randint(1, self.M)
                    old_c = self.y[idx]
                    new_c = random.randint(1, self.K)
                    while new_c == old_c: new_c = random.randint(1, self.K)
                    d_sim, d_pen = self.calc_delta_move_teach(idx, old_c, new_c)
                    candidate = {'type': 'teach', 'id': idx, 'from': old_c, 'to': new_c, 'd_sim': d_sim, 'd_pen': d_pen}
                    
            else: # SWAP
                swap_target = random.choice(['proj', 'teach'])
                if swap_target == 'proj':
                    u = random.randint(1, self.N)
                    v = random.randint(1, self.N)
                    while u == v: v = random.randint(1, self.N)
                    c1 = self.x[u]; c2 = self.x[v]
                    if c1 != c2:
                        d_sim = 0; d_pen = 0
                        # Move u: c1->c2
                        for other in self.c_p[c1]:
                            if other == u: continue
                            if self.s[u][other] < self.e: d_pen -= self.W_sim
                            else: d_sim -= self.s[u][other]
                        for t in self.c_t[c1]:
                            if self.t[u] == t: d_pen -= self.W_conflict
                            if self.g[u][t] < self.f: d_pen -= self.W_sim
                            else: d_sim -= self.g[u][t]
                        for other in self.c_p[c2]:
                            if other == v: continue 
                            if self.s[u][other] < self.e: d_pen += self.W_sim
                            else: d_sim += self.s[u][other]
                        for t in self.c_t[c2]:
                            if self.t[u] == t: d_pen += self.W_conflict
                            if self.g[u][t] < self.f: d_pen += self.W_sim
                            else: d_sim += self.g[u][t]
                        # Move v: c2->c1
                        for other in self.c_p[c2]:
                            if other == v: continue
                            if self.s[v][other] < self.e: d_pen -= self.W_sim
                            else: d_sim -= self.s[v][other]
                        for t in self.c_t[c2]:
                            if self.t[v] == t: d_pen -= self.W_conflict
                            if self.g[v][t] < self.f: d_pen -= self.W_sim
                            else: d_sim -= self.g[v][t]
                        for other in self.c_p[c1]:
                            if other == u: continue
                            if self.s[v][other] < self.e: d_pen += self.W_sim
                            else: d_sim += self.s[v][other]
                        for t in self.c_t[c1]:
                            if self.t[v] == t: d_pen += self.W_conflict
                            if self.g[v][t] < self.f: d_pen += self.W_sim
                            else: d_sim += self.g[v][t]
                        candidate = {'type': 'swap_proj', 'u': u, 'v': v, 'c_u': c1, 'c_v': c2, 'd_sim': d_sim, 'd_pen': d_pen}

                else: # Swap teach
                    u = random.randint(1, self.M)
                    v = random.randint(1, self.M)
                    while u == v: v = random.randint(1, self.M)
                    c1 = self.y[u]; c2 = self.y[v]
                    if c1 != c2:
                        d_sim = 0; d_pen = 0
                        # u: c1->c2
                        for p in self.c_p[c1]:
                            if self.t[p] == u: d_pen -= self.W_conflict
                            if self.g[p][u] < self.f: d_pen -= self.W_sim
                            else: d_sim -= self.g[p][u]
                        for p in self.c_p[c2]:
                            if self.t[p] == u: d_pen += self.W_conflict
                            if self.g[p][u] < self.f: d_pen += self.W_sim
                            else: d_sim += self.g[p][u]
                        # v: c2->c1
                        for p in self.c_p[c2]:
                            if self.t[p] == v: d_pen -= self.W_conflict
                            if self.g[p][v] < self.f: d_pen -= self.W_sim
                            else: d_sim -= self.g[p][v]
                        for p in self.c_p[c1]:
                            if self.t[p] == v: d_pen += self.W_conflict
                            if self.g[p][v] < self.f: d_pen += self.W_sim
                            else: d_sim += self.g[p][v]
                        candidate = {'type': 'swap_teach', 'u': u, 'v': v, 'c_u': c1, 'c_v': c2, 'd_sim': d_sim, 'd_pen': d_pen}

            if candidate:
                delta_f = (candidate['d_sim'] - candidate['d_pen'])
                accept = False
                if delta_f > 0:
                    accept = True
                else:
                    if self.T > 1e-9: # Tránh lỗi chia cho 0 hoặc overflow
                        prob = math.exp(delta_f / self.T)
                        if random.random() < prob:
                            accept = True
                
                if accept:
                    self.curr_sim += candidate['d_sim']
                    self.curr_pen += candidate['d_pen']
                    self.curr_fitness += delta_f
                    
                    if candidate['type'] == 'proj':
                        mid = candidate['id']; old = candidate['from']; new = candidate['to']
                        self.x[mid] = new
                        self.c_p[old].remove(mid); self.c_p[new].append(mid)
                        
                    elif candidate['type'] == 'teach':
                        mid = candidate['id']; old = candidate['from']; new = candidate['to']
                        self.y[mid] = new
                        self.c_t[old].remove(mid); self.c_t[new].append(mid)
                        
                    elif candidate['type'] == 'swap_proj':
                        u, v = candidate['u'], candidate['v']
                        c_u, c_v = candidate['c_u'], candidate['c_v']
                        self.x[u] = c_v; self.x[v] = c_u
                        self.c_p[c_u].remove(u); self.c_p[c_v].append(u)
                        self.c_p[c_v].remove(v); self.c_p[c_u].append(v)
                        
                    elif candidate['type'] == 'swap_teach':
                        u, v = candidate['u'], candidate['v']
                        c_u, c_v = candidate['c_u'], candidate['c_v']
                        self.y[u] = c_v; self.y[v] = c_u
                        self.c_t[c_u].remove(u); self.c_t[c_v].append(u)
                        self.c_t[c_v].remove(v); self.c_t[c_u].append(v)
                    
                    if self.curr_fitness > self.best_fitness:
                        self.best_fitness = self.curr_fitness
                        self.best_x = list(self.x)
                        self.best_y = list(self.y)
            
            # --- COOLING STEP (Giảm nhiệt độ) ---
            self.T *= self.decay

    def get_result(self):
        return self.N, self.best_x[1:], self.M, self.best_y[1:]

# =========================================================
# 4. MAIN EXECUTION
# =========================================================
if __name__ == '__main__':
    data = input_data()
    if data:
        N, M, K, a, b, c, d, e, f, s, g, t = data
        
        # 1. Chạy GRASP (Greedy Randomized) trong 5 giây
        greedy = GraspInitializer(N, M, K, a, b, c, d, e, f, s, g, t)
        init_x, init_y = greedy.solve(time_limit=5.0)
        
        # 2. Chạy Simulated Annealing
        sa = SimulatedAnnealingSolver(N, M, K, a, b, c, d, e, f, s, g, t, init_x, init_y)
        sa.solve()
        
        # 3. In kết quả cuối cùng
        out_N, out_x, out_M, out_y = sa.get_result()
        print(out_N)
        print(*(out_x))
        print(out_M)
        print(*(out_y))
import sys
import random
import math

# =========================================================
# 1. INPUT HANDLING (GIỮ NGUYÊN TEMPLATE)
# =========================================================
def input_data():
    line1 = sys.stdin.readline().split()
    if not line1: return None
    N, M, K = map(int, line1)

    a, b, c, d, e, f = map(float, sys.stdin.readline().split())
    a, b, c, d = int(a), int(b), int(c), int(d)

    s_matrix = [[0.0] * (N + 1)] 
    for _ in range(N):
        row = list(map(float, sys.stdin.readline().split()))
        s_matrix.append([0.0] + row) 

    g_matrix = [[0.0] * (M + 1)] 
    for _ in range(N):
        row = list(map(float, sys.stdin.readline().split()))
        g_matrix.append([0.0] + row)

    t_raw = list(map(int, sys.stdin.readline().split()))
    t_list = [0] + t_raw 

    return N, M, K, a, b, c, d, e, f, s_matrix, g_matrix, t_list

# =========================================================
# 2. METROPOLIS SOLVER
# =========================================================
class MetropolisSolver:
    def __init__(self, N, M, K, a, b, c, d, e, f, s_matrix, g_matrix, t_list):
        self.N, self.M, self.K = N, M, K
        self.a, self.b, self.c, self.d = a, b, c, d
        self.e, self.f = e, f
        self.s = s_matrix
        self.g = g_matrix
        self.t = t_list
        
        # Cấu hình Metropolis
        self.max_iter = 1000000  # Số vòng lặp (lớn hơn Tabu vì mỗi step nhanh hơn)
        self.T = 0.01            # Nhiệt độ không đổi (cần tinh chỉnh tùy dữ liệu)
        
        # Trọng số phạt (Giữ nguyên như Tabu để Delta calculation đúng)
        self.W_count = 12000
        self.W_conflict = 10000
        self.W_sim = 9999
        
        # Khởi tạo lời giải ngẫu nhiên
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

    # --- CÁC HÀM TÍNH DELTA (GIỮ NGUYÊN TỪ TABU BASE) ---
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
        # Metropolis Loop
        for iteration in range(self.max_iter):
            # 1. Pick ONE random neighbor (Move or Swap)
            action_type = random.randint(0, 99)
            
            candidate = None # Store proposed move
            
            if action_type < 50: # MOVE
                move_target = random.choice(['proj', 'teach'])
                if move_target == 'proj':
                    idx = random.randint(1, self.N)
                    old_c = self.x[idx]
                    new_c = random.randint(1, self.K)
                    while new_c == old_c: new_c = random.randint(1, self.K)
                    
                    d_sim, d_pen = self.calc_delta_move_proj(idx, old_c, new_c)
                    candidate = {'type': 'proj', 'id': idx, 'from': old_c, 'to': new_c, 'd_sim': d_sim, 'd_pen': d_pen}
                    
                else: # teach
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

            # 2. Check Acceptance (Metropolis Criterion)
            if candidate:
                delta_f = (candidate['d_sim'] - candidate['d_pen'])
                
                accept = False
                if delta_f > 0:
                    accept = True
                else:
                    # Prob = e^(delta / T)
                    prob = math.exp(delta_f / self.T)
                    if random.random() < prob:
                        accept = True
                
                # 3. Apply Move if Accepted
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
                    
                    # Update Global Best
                    if self.curr_fitness > self.best_fitness:
                        self.best_fitness = self.curr_fitness
                        self.best_x = list(self.x)
                        self.best_y = list(self.y)

    def get_result(self):
        return self.N, self.best_x[1:], self.M, self.best_y[1:]

if __name__ == "__main__":
    data = input_data()
    if data:
        N, M, K, a, b, c, d, e, f, s, g, t = data
        solver = MetropolisSolver(N, M, K, a, b, c, d, e, f, s, g, t)
        solver.solve()
        out_N, out_x, out_M, out_y = solver.get_result()
        print(out_N)
        print(*(out_x))
        print(out_M)
        print(*(out_y))
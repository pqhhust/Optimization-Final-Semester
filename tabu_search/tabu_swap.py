import sys
import random

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

class TabuSolver:
    def __init__(self, N, M, K, a, b, c, d, e, f, s_matrix, g_matrix, t_list):
        self.N, self.M, self.K = N, M, K
        self.a, self.b, self.c, self.d = a, b, c, d
        self.e, self.f = e, f
        self.s = s_matrix
        self.g = g_matrix
        self.t = t_list
        
        # Cấu hình Tabu
        self.max_iter = 1500
        self.tabu_tenure = 15
        self.tabu_list = {}
        self.num_neighbors = 50 
        
        # Trọng số phạt
        self.W_count = 10000
        self.W_conflict = 50000
        self.W_sim = 5000
        
        # Lời giải hiện tại
        self.x = [0] + [random.randint(1, K) for _ in range(N)] 
        self.y = [0] + [random.randint(1, K) for _ in range(M)]
        
        self.best_x = list(self.x)
        self.best_y = list(self.y)
        self.best_fitness = -float('inf')

    def evaluate(self, x_sol, y_sol):
        total_sim = 0
        penalty = 0

        # councils_projects[k] chứa list các đồ án thuộc hội đồng k
        councils_projects = [[] for _ in range(self.K + 1)]
        councils_teachers = [[] for _ in range(self.K + 1)]
        
        for i in range(1, self.N + 1):
            c = x_sol[i]
            councils_projects[c].append(i)
            
        for j in range(1, self.M + 1):
            c = y_sol[j]
            councils_teachers[c].append(j)
            
        # Duyệt từng hội đồng từ 1 đến K
        for k in range(1, self.K + 1):
            p_list = councils_projects[k]
            t_list = councils_teachers[k]
            p_len = len(p_list)
            t_len = len(t_list)
            
            # 1. Phạt số lượng (Constraint Satisfaction)
            if p_len < self.a: penalty += (self.a - p_len) * self.W_count
            if p_len > self.b: penalty += (p_len - self.b) * self.W_count
            if t_len < self.c: penalty += (self.c - t_len) * self.W_count
            if t_len > self.d: penalty += (t_len - self.d) * self.W_count
            
            # 2. Tính tương đồng & Phạt Đồ án - Đồ án
            for i in range(p_len):
                u = p_list[i]
                for j in range(i+1, p_len): # Đôi một
                    v = p_list[j]
                    sim = self.s[u][v]
                    if sim < self.e:
                        penalty += self.W_sim
                    else:
                        total_sim += sim
            
            # 3. Tính tương đồng & Phạt Đồ án - Giáo viên
            for u in p_list:     
                for v in t_list: 
                    if self.t[u] == v:
                        penalty += self.W_conflict
                    
                    sim = self.g[u][v]
                    if sim < self.f:
                        penalty += self.W_sim
                    else:
                        total_sim += sim

        return total_sim - penalty, total_sim, penalty

    def solve(self):
        # Đánh giá ban đầu
        curr_fitness, _, _ = self.evaluate(self.x, self.y)
        self.best_fitness = curr_fitness
        
        for iteration in range(self.max_iter):
            candidates = []
            
            # Lấy mẫu ngẫu nhiên láng giềng
            for _ in range(self.num_neighbors):
                action_type = random.randint(0, 99)
                if action_type < 50: 
                    move_target = random.choice(['proj', 'teach'])
                
                    if move_target == 'proj': # Chuyển ĐỒ ÁN
                        idx = random.randint(1, self.N)
                        old_council = self.x[idx]
                        
                        new_council = random.randint(1, self.K) 
                        while new_council == old_council:
                            new_council = random.randint(1, self.K)
                        
                        # Thử nước đi
                        self.x[idx] = new_council
                        fitness, sim, pen = self.evaluate(self.x, self.y)
                        self.x[idx] = old_council # Hoàn tác
                        
                        candidates.append({
                            'type': 'proj', 'id': idx, 'from': old_council, 'to': new_council,
                            'fitness': fitness, 'sim': sim, 'pen': pen
                        })
                        
                    else: # Chuyển GIÁO VIÊN
                        idx = random.randint(1, self.M) 
                        old_council = self.y[idx]
                        
                        new_council = random.randint(1, self.K)
                        while new_council == old_council:
                            new_council = random.randint(1, self.K)
                            
                        self.y[idx] = new_council
                        fitness, sim, pen = self.evaluate(self.x, self.y)
                        self.y[idx] = old_council 

                        candidates.append({
                            'type': 'teach', 'id': idx, 'from': old_council, 'to': new_council,
                            'fitness': fitness, 'sim': sim, 'pen': pen
                        })
                else:
                    swap_target = random.choice(['proj', 'teach'])

                    if swap_target == 'proj': # SWAP 2 ĐỒ ÁN
                        u = random.randint(1, self.N)
                        v = random.randint(1, self.N)
                        while u == v:
                            v = random.randint(1, self.N)                           
                        c1 = self.x[u] 
                        c2 = self.x[v] 
                        if c1 != c2:
                            # Thực hiện hoán đổi giả định
                            self.x[u] = c2
                            self.x[v] = c1
                            
                            fitness, sim, pen = self.evaluate(self.x, self.y)
                            
                            # Hoàn tác (Backtrack)
                            self.x[u] = c1
                            self.x[v] = c2
                            
                            # Lưu candidate kiểu mới: 'swap_proj'
                            # Lưu ý: ta cần lưu cả u, v và c1, c2 để lát nữa thực hiện move
                            candidates.append({
                                'type': 'swap_proj', 
                                'u': u, 'v': v, 
                                'c_u': c1, 'c_v': c2, # c_u là hội đồng cũ của u, c_v là hội đồng cũ của v
                                'fitness': fitness, 'sim': sim, 'pen': pen
                            })

                    else: # SWAP 2 GIÁO VIÊN
                        u = random.randint(1, self.M)
                        v = random.randint(1, self.M)
                        while u == v:
                            v = random.randint(1, self.M)
                            
                        c1 = self.y[u]
                        c2 = self.y[v]
                        
                        if c1 != c2:
                            self.y[u] = c2
                            self.y[v] = c1
                            
                            fitness, sim, pen = self.evaluate(self.x, self.y)
                            
                            self.y[u] = c1
                            self.y[v] = c2
                            
                            candidates.append({
                                'type': 'swap_teach', 
                                'u': u, 'v': v, 
                                'c_u': c1, 'c_v': c2,
                                'fitness': fitness, 'sim': sim, 'pen': pen
                            })


            # Sắp xếp candidate tốt nhất lên đầu
            candidates.sort(key=lambda x: x['fitness'], reverse=True)
            
            best_move = None
            for move in candidates:
                is_tabu = False
                
                if move['type'] in ['proj', 'teach']:
                    check_key = (move['type'], move['id'], move['to'])
                    
                    if check_key in self.tabu_list:
                        if self.tabu_list[check_key] > iteration:
                            is_tabu = True

                elif move['type'] in ['swap_proj', 'swap_teach']:
                    obj_type = 'proj' if move['type'] == 'swap_proj' else 'teach'
                    
                    u, v = move['u'], move['v']
                    c_u, c_v = move['c_u'], move['c_v'] 
                   
                    key1 = (obj_type, u, c_v) 
                    
                    key2 = (obj_type, v, c_u)

                    if (key1 in self.tabu_list and self.tabu_list[key1] > iteration) or \
                       (key2 in self.tabu_list and self.tabu_list[key2] > iteration):
                        is_tabu = True

                # Nếu không bị cấm HOẶC tốt hơn kỷ lục -> Chọn ngay
                if not is_tabu or move['fitness'] > self.best_fitness:
                    best_move = move
                    break
            
            if best_move is None and candidates:
                best_move = candidates[0]

            if best_move:
                if best_move['type'] == 'proj':
                    self.x[best_move['id']] = best_move['to']
                    tabu_key = ('proj', best_move['id'], best_move['from']) # Cấm quay về hội đồng cũ
                    self.tabu_list[tabu_key] = iteration + self.tabu_tenure
                    
                elif best_move['type'] == 'teach':
                    self.y[best_move['id']] = best_move['to']
                    tabu_key = ('teach', best_move['id'], best_move['from'])
                    self.tabu_list[tabu_key] = iteration + self.tabu_tenure
                    
                elif best_move['type'] == 'swap_proj':
                    u, v = best_move['u'], best_move['v']
                    c_u, c_v = best_move['c_u'], best_move['c_v']
                    
                    # Thực hiện đổi chỗ
                    self.x[u] = c_v # u sang hội đồng của v
                    self.x[v] = c_u # v sang hội đồng của u
                    
                    # Cấm u quay lại c_u VÀ cấm v quay lại c_v
                    self.tabu_list[('proj', u, c_u)] = iteration + self.tabu_tenure
                    self.tabu_list[('proj', v, c_v)] = iteration + self.tabu_tenure

                elif best_move['type'] == 'swap_teach':
                    u, v = best_move['u'], best_move['v']
                    c_u, c_v = best_move['c_u'], best_move['c_v']
                    
                    self.y[u] = c_v
                    self.y[v] = c_u
                    
                    self.tabu_list[('teach', u, c_u)] = iteration + self.tabu_tenure
                    self.tabu_list[('teach', v, c_v)] = iteration + self.tabu_tenure
                
                # Cập nhật Best Solution (Giữ nguyên)
                if best_move['fitness'] > self.best_fitness:
                    self.best_fitness = best_move['fitness']
                    self.best_x = list(self.x)
                    self.best_y = list(self.y)

    def get_result(self):
        return self.N, self.best_x[1:], self.M, self.best_y[1:]

if __name__ == "__main__":
    data = input_data()
    if data:
        N, M, K, a, b, c, d, e, f, s, g, t = data
        
        solver = TabuSolver(N, M, K, a, b, c, d, e, f, s, g, t)
        solver.solve()
        
        out_N, out_x, out_M, out_y = solver.get_result()
        
        print(out_N)
        print(*(out_x))
        print(out_M)
        print(*(out_y))
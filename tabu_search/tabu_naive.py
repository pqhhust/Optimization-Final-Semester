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
        self.max_iter = 2000
        self.tabu_tenure = 15
        self.tabu_list = {}
        self.num_neighbors = 100 
        
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
                move_type = random.choice([0, 1]) 
                
                if move_type == 0: # Chuyển ĐỒ ÁN
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

            # Sắp xếp candidate tốt nhất lên đầu
            candidates.sort(key=lambda x: x['fitness'], reverse=True)
            
            best_move = None
            for move in candidates:
                move_key = (move['type'], move['id'], move['to'])
                
                is_tabu = False
                if move_key in self.tabu_list:
                    if self.tabu_list[move_key] > iteration:
                        is_tabu = True
                
                # Nếu thực sự tốt hơn cả giá trị tốt nhất hiện tại thì phá luật cấm
                if not is_tabu or move['fitness'] > self.best_fitness:
                    best_move = move
                    break
            
            if best_move is None and candidates:
                best_move = candidates[0]

            if best_move:
                if best_move['type'] == 'proj':
                    self.x[best_move['id']] = best_move['to']
                    tabu_key = ('proj', best_move['id'], best_move['from'])
                else:
                    self.y[best_move['id']] = best_move['to']
                    tabu_key = ('teach', best_move['id'], best_move['from'])
                
                self.tabu_list[tabu_key] = iteration + self.tabu_tenure
                
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
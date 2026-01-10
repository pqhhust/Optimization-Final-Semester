import sys
import random
import time

# Tăng giới hạn đệ quy
sys.setrecursionlimit(5000)

class Council:
    def __init__(self, id):
        self.id = id
        self.theses = []   # List chứa ID đồ án (1-based)
        self.teachers = [] # List chứa ID giáo viên (1-based)

def solve():
    # 1. ĐỌC DỮ LIỆU 

    N, M, K = map(int, input().split())
    a, b, c, d, e, f = map(int, input().split())
    s = [[0] for _ in range(N+1)]
    for i in range(1, N+1):
        s[i] = [0] + list(map(int, input().split()))
    g = [[0] for _ in range(N+1)]
    for i in range(1, N+1):
        g[i] = [0] + list(map(int, input().split()))
    t = [0] + list(map(int, input().split()))


    # 2. CÁC HÀM KIỂM TRA RÀNG BUỘC

    def check_thesis(u, council_theses, council_teachers):
        # Kiểm tra Max size b
        if len(council_theses) >= b: return False
        # Kiểm tra Clique s >= e
        for eth in council_theses:
            if s[u][eth] < e: return False
        # Kiểm tra Clique g >= f
        for ete in council_teachers:
            if g[u][ete] < f: return False
        # Kiểm tra Xung đột GVHD
        for ete in council_teachers:
            if t[u] == ete: return False
        return True

    def check_teacher(v, council_theses, council_teachers):
        # Kiểm tra Max size d
        if len(council_teachers) >= d: return False
        # Kiểm tra Clique g >= f
        for eth in council_theses:
            if g[eth][v] < f: return False
        # Kiểm tra Xung đột GVHD
        for eth in council_theses:
            if t[eth] == v: return False
        return True


    # 3. HÀM CHẠY 1 LẦN (RANDOM SEED -> PURE GREEDY)
    def run_one_pass():
        curr_c_thesis = [0] * (N + 1)
        curr_c_teacher = [0] * (M + 1)
        councils = [Council(k) for k in range(1, K + 1)]
        
        # Danh sách các hội đồng để duyệt
        council_indices = list(range(K)) 

        # ĐIỀN ĐẾN MỨC TỐI THIỂU (Min a, Min c) 
        # Mục đích: Đảm bảo không hội đồng nào bị thiếu người
        for k_idx in council_indices:
            curr_council = councils[k_idx]
            
            # 1.1 Chọn SEED (CHỖ DUY NHẤT CÓ RANDOM)
            if not curr_council.theses:
                # Lấy tất cả đồ án chưa gán
                candidates = [i for i in range(1, N + 1) if curr_c_thesis[i] == 0]
                if candidates:
                    # Chọn ngẫu nhiên 1 hạt giống
                    seed = random.choice(candidates)
                    curr_council.theses.append(seed)
                    curr_c_thesis[seed] = curr_council.id
            
            # 1.3 Greedy Fill Teacher -> Min c
            while len(curr_council.teachers) < c:
                best_cand = -1
                best_gain = -1
                
                for j in range(1, M + 1):
                    if curr_c_teacher[j] == 0:
                        if check_teacher(j, curr_council.theses, curr_council.teachers):
                            # Tính Gain
                            gain = sum(g[x][j] for x in curr_council.theses)
                            if gain > best_gain:
                                best_gain = gain
                                best_cand = j
                
                if best_cand != -1:
                    curr_council.teachers.append(best_cand)
                    curr_c_teacher[best_cand] = curr_council.id
                else:
                    break
            
            # 1.2 Greedy Fill Thesis -> Min a
            while len(curr_council.theses) < a:
                best_cand = -1
                best_gain = -1
                
                # Duyệt tất cả các ứng viên khả thi
                for i in range(1, N + 1):
                    if curr_c_thesis[i] == 0:
                        if check_thesis(i, curr_council.theses, curr_council.teachers):
                            # Tính Gain: Tổng độ tương đồng với các thành viên hiện tại
                            gain = sum(s[i][x] for x in curr_council.theses)
                            # Chọn cái tốt nhất (Greedy)
                            if gain > best_gain:
                                best_gain = gain
                                best_cand = i
                
                if best_cand != -1:
                    curr_council.theses.append(best_cand)
                    curr_c_thesis[best_cand] = curr_council.id
                else:
                    break # Không còn ai hợp lệ để đạt mức a



        # ĐIỀN ĐẾN MỨC TỐI ĐA (Max b, Max d) 
        # Sau khi mọi hội đồng đã (hy vọng) đạt min, ta điền nốt phần dư
        for k_idx in council_indices:
            curr_council = councils[k_idx]
            
            # 2.1 Greedy Fill Thesis -> Max b
            while len(curr_council.theses) < b:
                best_cand = -1
                best_gain = -1
                
                for i in range(1, N + 1):
                    if curr_c_thesis[i] == 0:
                        if check_thesis(i, curr_council.theses, curr_council.teachers):
                            gain = sum(s[i][x] for x in curr_council.theses)
                            if gain > best_gain:
                                best_gain = gain
                                best_cand = i
                
                if best_cand != -1:
                    curr_council.theses.append(best_cand)
                    curr_c_thesis[best_cand] = curr_council.id
                else:
                    break

            # 2.2 Greedy Fill Teacher -> Max d
            while len(curr_council.teachers) < d:
                best_cand = -1
                best_gain = -1
                
                for j in range(1, M + 1):
                    if curr_c_teacher[j] == 0:
                        if check_teacher(j, curr_council.theses, curr_council.teachers):
                            gain = sum(g[x][j] for x in curr_council.theses)
                            if gain > best_gain:
                                best_gain = gain
                                best_cand = j
                                
                if best_cand != -1:
                    curr_council.teachers.append(best_cand)
                    curr_c_teacher[best_cand] = curr_council.id
                else:
                    break
        
        # VÉT CẠN 
        # Cố gắng nhét nốt những người còn sót vào bất kỳ đâu hợp lệ, ưu tiên nơi có gain cao nhất (Best Fit)
        
        # Vét Đồ án
        unassigned_theses = [i for i in range(1, N+1) if curr_c_thesis[i] == 0]
        for i in unassigned_theses:
            best_k = -1
            max_gain = -1
            
            for k_idx in range(K):
                if check_thesis(i, councils[k_idx].theses, councils[k_idx].teachers):
                    gain = sum(s[i][x] for x in councils[k_idx].theses)
                    if gain > max_gain:
                        max_gain = gain
                        best_k = k_idx
            
            if best_k != -1:
                councils[best_k].theses.append(i)
                curr_c_thesis[i] = councils[best_k].id

        # Vét Giáo viên
        unassigned_teachers = [j for j in range(1, M+1) if curr_c_teacher[j] == 0]
        for j in unassigned_teachers:
            best_k = -1
            max_gain = -1
            for k_idx in range(K):
                if check_teacher(j, councils[k_idx].theses, councils[k_idx].teachers):
                    gain = sum(g[x][j] for x in councils[k_idx].theses)
                    if gain > max_gain:
                        max_gain = gain
                        best_k = k_idx
            
            if best_k != -1:
                councils[best_k].teachers.append(j)
                curr_c_teacher[best_k] = councils[best_k].id

        # Này là đếm số thằng chưa được gán trong lời giải
        assigned_count = (N + 1 - curr_c_thesis.count(0)) + (M + 1 - curr_c_teacher.count(0))
        return assigned_count, curr_c_thesis, curr_c_teacher


    # 4. HÀM TÍNH ĐIỂM
    def calculate_score(res_th, res_te):
        score = 0
        local_councils = [Council(k) for k in range(1, K + 1)]
        # Tái tạo hội đồng từ danh sách hiện tại
        for idx in range(1, N + 1):
            c_id = res_th[idx]
            if c_id > 0: local_councils[c_id-1].theses.append(idx)
        for idx in range(1, M + 1):
            c_id = res_te[idx]
            if c_id > 0: local_councils[c_id-1].teachers.append(idx)
            
        for council in local_councils:
            # S
            cth = council.theses
            cte = council.teachers
            n_th = len(cth)
            for i in range(n_th):
                for j in range(i + 1, n_th):
                    score += s[cth[i]][cth[j]]
            # G
            for th in cth:
                for te in cte:
                    score += g[th][te]
        return score
    
    # 5. VÒNG LẶP CHÍNH 

    best_assigned_count = -1
    best_total_score = -1
    best_thesis_assign = [0] * (N + 1)
    best_teacher_assign = [0] * (M + 1)
    
    MAX_ITER = 200
    
    for i in range(MAX_ITER):
        curr_cnt, curr_th, curr_te = run_one_pass()
        
        # Logic so sánh:
        # Ưu tiên 1: Số lượng người được gán (Càng nhiều càng tốt, mục tiêu là N+M)
        if curr_cnt > best_assigned_count:
            best_assigned_count = curr_cnt
            best_thesis_assign = list(curr_th)
            best_teacher_assign = list(curr_te)
            best_total_score = calculate_score(curr_th, curr_te)
            
        # Ưu tiên 2: Nếu số lượng bằng nhau, chọn cái có điểm cao hơn
        elif curr_cnt == best_assigned_count:
            curr_score = calculate_score(curr_th, curr_te)
            if curr_score > best_total_score:
                best_total_score = curr_score
                best_thesis_assign = list(curr_th)
                best_teacher_assign = list(curr_te)


    # 6. IN KẾT QUẢ
    print(N)
    print(*(best_thesis_assign[1:]))
    print(M)
    print(*(best_teacher_assign[1:]))

if __name__ == '__main__':
    solve()

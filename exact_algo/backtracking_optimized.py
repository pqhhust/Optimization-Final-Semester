import time

N, M, K = map(int, input().split())
a, b, c, d, e, f = map(int, input().split())
s = [[0] for _ in range(N+1)]
for i in range(1, N+1):
    s[i] = [0] + list(map(int, input().split()))
g = [[0] for _ in range(N+1)]
for i in range(1, N+1):
    g[i] = [0] + list(map(int, input().split()))
t = [0] + list(map(int, input().split()))

# x[i] = hội đồng mà đồ án i được phân vào
# y[j] = hội đồng mà giáo viên j được phân vào
x = [0] * (N+1)
y = [0] * (M+1)

# rx, ry: lưu nghiệm tối ưu (best solution) tìm được
rx = [0] * (N+1)
ry = [0] * (M+1)

optimal_total = 0

# hda[k] = danh sách các đồ án hiện tại trong hội đồng k
# hdb[k] = danh sách các giáo viên hiện tại trong hội đồng k
hda = [[] for _ in range(K+1)]
hdb = [[] for _ in range(K+1)]

assigned_projects_count = 0
assigned_teachers_count = 0

# Kiểm tra xem có thể gán đồ án k vào hội đồng v không
def checkX(v, k):
    if len(hda[v]) >= b: return False
    for i in hda[v]:
        if s[i][k] < e: return False
    return True

# Kiểm tra xem có thể gán giáo viên k vào hội đồng v không
def checkY(v, k):
    if len(hdb[v]) >= d: return False
    for i in hda[v]:
        if t[i] == k: return False
        if g[i][k] < f: return False
    return True

# Early pruning: kiểm tra xem còn đủ khả năng đạt ràng buộc tối thiểu không
def canReachMinConstraint():
    global assigned_projects_count, assigned_teachers_count
    
    # Kiểm tra cho đồ án
    remaining_projects = N - assigned_projects_count
    
    # Tính tổng số đồ án còn thiếu để các hội đồng đạt tối thiểu a
    total_needed = 0
    for k in range(1, K+1):
        size = len(hda[k])
        if size > b:
            return False
        if size < a:
            total_needed += (a - size)
    
    if total_needed > remaining_projects:
        return False
    
    # Kiểm tra cho giáo viên (chỉ khi đã gán hết đồ án)
    if assigned_projects_count == N:
        remaining_teachers = M - assigned_teachers_count
        
        total_needed_teachers = 0
        for k in range(1, K+1):
            size = len(hdb[k]) 
            if size > d:
                return False
            if size < c:
                total_needed_teachers += (c - size)
        
        if total_needed_teachers > remaining_teachers:
            return False
    
    return True

# Kiểm tra tất cả ràng buộc khi đã gán hết đồ án và giáo viên
def checkfinal():
    for p in range(1, K+1):
        if len(hda[p]) < a or len(hda[p]) > b: 
            return False
        if len(hdb[p]) < c or len(hdb[p]) > d:  
            return False
    return True

# Tính hàm mục tiêu và cập nhật nghiệm tối ưu
def sol():
    global optimal_total, rx, ry
    if not checkfinal():
        return
    
    total = 0 
    for p in range(1, K+1):
        for i1 in range(len(hda[p])):
            for i2 in range(i1 + 1, len(hda[p])):
                total += s[hda[p][i1]][hda[p][i2]]
        for i in hda[p]:
            for j in hdb[p]:
                total += g[i][j]
    
    if total > optimal_total:
        optimal_total = total
        rx = x[:]  
        ry = y[:]

# Hàm quay lui để gán giáo viên
def TryY(k):
    global assigned_teachers_count
    
    # Early pruning: LUÔN kiểm tra (không bỏ qua khi count = 0)
    if not canReachMinConstraint():
        return
    
    for v in range(1, K+1):
        if checkY(v, k):
            y[k] = v
            hdb[v].append(k)
            assigned_teachers_count += 1
            
            if k == M:
                sol()
            else:
                TryY(k+1)
            
            hdb[v].pop() 
            assigned_teachers_count -= 1
            y[k] = 0

# Hàm quay lui để gán đồ án
def TryX(k):
    global assigned_projects_count
    
    # Early pruning: LUÔN kiểm tra (không bỏ qua khi count = 0)
    # Ví dụ: nếu K * a > N thì không thể phân bổ được
    if not canReachMinConstraint():
        return
    
    for v in range(1, K+1):
        if checkX(v, k):
            x[k] = v
            hda[v].append(k)
            assigned_projects_count += 1
            
            if k == N:
                TryY(1)
            else:
                TryX(k+1)
            
            hda[v].pop()
            assigned_projects_count -= 1
            x[k] = 0

# Bắt đầu đo thời gian
start_time = time.time()
TryX(1)
end_time = time.time()
execution_time = end_time - start_time

print(N)
for i in range(1, N + 1): 
    print(rx[i], end = " ")
print()
print(M)
for j in range(1, M + 1): 
    print(ry[j], end = " ")
print()
print(f"Objective value: {optimal_total}")
print(f"Execution time: {execution_time:.5f} seconds")

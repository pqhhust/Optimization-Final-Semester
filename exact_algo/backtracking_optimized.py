# Backtracking Optimized với Early Pruning

# Đọc dữ liệu đầu vào
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
    # Kiểm tra cho đồ án
    assigned_projects = sum(len(hda[k]) for k in range(1, K+1))
    remaining_projects = N - assigned_projects
    
    # Tính tổng số đồ án còn thiếu để các hội đồng đạt tối thiểu a
    total_needed = 0
    for k in range(1, K+1):
        if len(hda[k]) > b:
            return False
        if len(hda[k]) < a:
            total_needed += (a - len(hda[k]))
    
    if total_needed > remaining_projects:
        return False
    
    # Kiểm tra cho giáo viên (chỉ khi đã gán hết đồ án)
    if assigned_projects == N:
        assigned_teachers = sum(len(hdb[k]) for k in range(1, K+1))
        remaining_teachers = M - assigned_teachers
        
        total_needed_teachers = 0
        for k in range(1, K+1):
            if len(hdb[k]) > d:
                return False
            if len(hdb[k]) < c:
                total_needed_teachers += (c - len(hdb[k]))
        
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
        # Tối ưu: dùng index thay vì so sánh i1 < i2
        for i1 in range(len(hda[p])):
            for i2 in range(i1 + 1, len(hda[p])):
                total += s[hda[p][i1]][hda[p][i2]]
        for i in hda[p]:
            for j in hdb[p]:
                total += g[i][j]
    
    if total > optimal_total:
        optimal_total = total
        rx = x[:]  # Copy nhanh hơn list()
        ry = y[:]

# Hàm quay lui để gán giáo viên
def TryY(k):
    # Early pruning: dừng sớm nếu không thể đạt ràng buộc tối thiểu
    if not canReachMinConstraint():
        return
    
    for v in range(1, K+1):
        if checkY(v, k):
            y[k] = v
            hdb[v].append(k)
            if k == M:
                sol()
            else:
                TryY(k+1)
            hdb[v].pop()  # pop() nhanh hơn remove() với phần tử cuối
            y[k] = 0

# Hàm quay lui để gán đồ án
def TryX(k):
    # Early pruning: dừng sớm nếu không thể đạt ràng buộc tối thiểu
    if not canReachMinConstraint():
        return
    
    for v in range(1, K+1):
        if checkX(v, k):
            x[k] = v
            hda[v].append(k)
            if k == N:
                TryY(1)
            else:
                TryX(k+1)
            hda[v].pop()  # pop() nhanh hơn remove() với phần tử cuối
            x[k] = 0

TryX(1)

print(N)
for i in range(1, N + 1): 
    print(rx[i], end = " ")
print()
print(M)
for j in range(1, M + 1): 
    print(ry[j], end = " ")

# Backtracking
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
    global optimal_total
    global rx, ry
    total = 0 
    if checkfinal():
        for p in range(1, K+1):
            for i1 in hda[p]:
                for i2 in hda[p]:
                    if i1 < i2:
                        total += s[i1][i2]
            for i in hda[p]:
                for j in hdb[p]:
                    total += g[i][j]
        if total > optimal_total:
            optimal_total = total
            rx = list(x)
            ry = list(y)
    

# Hàm quay lui để gán giáo viên
def TryY(k):
    for v in range(1, K+1):
        if checkY(v, k):
            y[k] = v
            hdb[v].append(k)
            if (k == M): sol()
            else: TryY(k+1)
            hdb[v].remove(k)


# Hàm quay lui để gán đồ án
def TryX(k):
    for v in range(1, K+1):
        if checkX(v, k):
            x[k] = v
            hda[v].append(k)
            if (k == N): TryY(1)
            else: TryX(k+1)
            hda[v].remove(k)

start_time = time.time()
TryX(1)
end_time = time.time()
execution_time = end_time - start_time

print(N)
for i in range(1, N + 1): print(rx[i], end = " ")
print()
print(M)
for j in range(1, M + 1): print(ry[j], end = " ")
print()
print(f"Objective value: {optimal_total}")
print(f"Execution time: {execution_time:.5f} seconds")

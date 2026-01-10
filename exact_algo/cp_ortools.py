from ortools.sat.python import cp_model

model = cp_model.CpModel()
solver = cp_model.CpSolver()

N, M, K = map(int, input().split())
a, b, c, d, e, f = map(int, input().split())
s = [[0] for _ in range(N+1)]
for i in range(1, N+1):
    s[i] = [0] + list(map(int, input().split()))
g = [[0] for _ in range(N+1)]
for i in range(1, N+1):
    g[i] = [0] + list(map(int, input().split()))
t = [0] + list(map(int, input().split()))

MBig = 1000000

# Variables 
x = {}
for i in range(1, N + 1):
    for k in range(1, K + 1):
        x[i, k] = model.NewBoolVar(f'x{i}{k}')

y = {}
for j in range(1, M + 1):
    for k in range(1, K + 1):
        y[j, k] = model.NewBoolVar(f'y{j}{k}')

# Constraints

# Mỗi đồ án chỉ thuộc về một hội đồng
for i in range(1, N+1): model.Add(sum(x[i, k] for k in range(1, K+1)) == 1)

# Mỗi giảng viên chỉ tham gia một hội đồng
for j in range(1, M+1): model.Add(sum(y[j, k] for k in range(1, K+1)) == 1)

# Mỗi hội đồng có >=a <=b đồ án, có >=c <=d giảng viên
for k in range(1, K+1):
    model.Add(sum(x[i, k] for i in range(1, N+1)) >= a)
    model.Add(sum(x[i, k] for i in range(1, N+1)) <= b)
    model.Add(sum(y[j, k] for j in range(1, M+1)) >= c)
    model.Add(sum(y[j, k] for j in range(1, M+1)) <= d)

# Giảng viên không cùng hội đồng sinh viên mình hướng dẫn:
for i in range(1, N+1):
    for k in range(1, K+1):
        model.Add(x[i, k] + y[t[i], k] <= 1) 

# Độ tương đồng giữa các đồ án trong cùng hội đồng phải lớn hơn hoặc bằng e
for i1 in range(1, N + 1):
    for i2 in range(i1 + 1, N + 1):
        if s[i1][i2] < e:
            for k in range(1, K + 1):
                model.Add(x[i1, k] + x[i2, k] <= 1)

# Độ tương đồng giữa đồ án với giáo viên trong hội đồng phải lớn hơn hoặc bằng f
for i in range(1, N + 1):
    for j in range(1, M + 1):
        if g[i][j] < f:
            for k in range(1, K + 1):
                model.Add(x[i, k] + y[j, k] <= 1)

# Danh sách chứa các thành phần của hàm mục tiêu
obj_terms = []

for k in range(1, K + 1):
    # 1. Tổng độ tương đồng giữa các đồ án s(i, j)
    for i1 in range(1, N + 1):
        for i2 in range(i1 + 1, N + 1):
            # Chỉ xét những cặp có khả năng đứng cùng nhau (thỏa mãn e)
            if s[i1][i2] >= e:
                # Tạo biến Boolean z = (đồ án i1 và i2 cùng ở HĐ k)
                z = model.NewBoolVar(f'pair_s_{i1}_{i2}_k{k}')
                model.Add(z <= x[i1, k])
                model.Add(z <= x[i2, k])
                obj_terms.append(z * s[i1][i2])

    # 2. Tổng độ tương đồng giữa đồ án i và giáo viên j
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            # Chỉ xét nếu giáo viên không hướng dẫn và thỏa mãn f
            if t[i] != j and g[i][j] >= f:
                # Tạo biến Boolean w = (đồ án i và giáo viên j cùng ở HĐ k)
                w = model.NewBoolVar(f'pair_g_{i}_{j}_k{k}')
                model.Add(w <= x[i, k])
                model.Add(w <= y[j, k])
                obj_terms.append(w * g[i][j])

# Thiết lập hàm tối ưu
model.Maximize(sum(obj_terms))

# Giải bài toán
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(N)
    for i in range(1, N + 1):
        for k in range(1, K + 1):
            if solver.Value(x[i, k]):
                print(k, end=" ")
    print()
    print(M)
    for j in range(1, M + 1):
        for k in range(1, K + 1):
            if solver.Value(y[j, k]):
                print(k, end=" ")

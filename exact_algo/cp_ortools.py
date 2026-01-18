from ortools.sat.python import cp_model
import time

model = cp_model.CpModel()
solver = cp_model.CpSolver()

solver.parameters.max_time_in_seconds = 14400.0
solver.parameters.num_search_workers = 40
solver.parameters.log_search_progress = False
solver.parameters.linearization_level = 2
solver.parameters.cp_model_presolve = True
solver.parameters.use_optional_variables = True
solver.parameters.cp_model_probing_level = 2
solver.parameters.enumerate_all_solutions = False

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


# x[i, k] = 1 nếu đồ án i được phân vào hội đồng k
x = {}
for i in range(1, N + 1):
    for k in range(1, K + 1):
        x[i, k] = model.NewBoolVar(f'x{i}{k}')

# y[j, k] = 1 nếu giáo viên j được phân vào hội đồng k
y = {}
for j in range(1, M + 1):
    for k in range(1, K + 1):
        y[j, k] = model.NewBoolVar(f'y{j}{k}')


# Ràng buộc số lượng
for k in range(1, K+1):
    model.Add(sum(x[i, k] for i in range(1, N+1)) >= a)
    model.Add(sum(x[i, k] for i in range(1, N+1)) <= b)
    model.Add(sum(y[j, k] for j in range(1, M+1)) >= c)
    model.Add(sum(y[j, k] for j in range(1, M+1)) <= d)

# Ràng buộc phân bổ 
for i in range(1, N+1): model.Add(sum(x[i, k] for k in range(1, K+1)) == 1)
for j in range(1, M+1): model.Add(sum(y[j, k] for k in range(1, K+1)) == 1)

# Ràng buộc xung đột
for i in range(1, N+1):
    for k in range(1, K+1):
        model.Add(x[i, k] + y[t[i], k] <= 1) 

# Ràng buộc ngưỡng tương đồng đồ án
for i1 in range(1, N + 1):
    for i2 in range(i1 + 1, N + 1):
        if s[i1][i2] < e:
            for k in range(1, K + 1):
                model.Add(x[i1, k] + x[i2, k] <= 1)

# Ràng buộc ngưỡng tương đồng giáo viên
for i in range(1, N + 1):
    for j in range(1, M + 1):
        if g[i][j] < f:
            for k in range(1, K + 1):
                model.Add(x[i, k] + y[j, k] <= 1)


obj_terms = []
for k in range(1, K + 1):
    # Tổng độ tương đồng giữa các đồ án s(i, j)
    for i1 in range(1, N + 1):
        for i2 in range(i1 + 1, N + 1):
            # Chỉ xét những cặp thỏa mãn ngưỡng tương đồng e
            if s[i1][i2] >= e:
                z = model.NewBoolVar(f'pair_s_{i1}_{i2}_k{k}')
                model.Add(z <= x[i1, k])
                model.Add(z <= x[i2, k])
                model.Add(z >= x[i1, k] + x[i2, k] - 1)
                obj_terms.append(z * s[i1][i2])

    # Tổng độ tương đồng giữa đồ án i và giáo viên j
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            # Chỉ xét nếu giáo viên không hướng dẫn và thỏa mãn ngưỡng tương đồng f
            if t[i] != j and g[i][j] >= f:
                w = model.NewBoolVar(f'pair_g_{i}_{j}_k{k}')
                model.Add(w <= x[i, k])
                model.Add(w <= y[j, k])
                model.Add(w >= x[i, k] + y[j, k] - 1)
                obj_terms.append(w * g[i][j])

model.Maximize(sum(obj_terms))

# Bắt đầu đo thời gian
start_time = time.time()
status = solver.Solve(model)
end_time = time.time()
execution_time = end_time - start_time

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
    print()
    objective_value = solver.ObjectiveValue()
    print(f"Objective value: {int(objective_value)}")
    print(f"Execution time: {execution_time:.5f} seconds")
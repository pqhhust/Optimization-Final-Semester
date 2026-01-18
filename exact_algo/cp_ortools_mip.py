from ortools.linear_solver import pywraplp
import time
import os

# Sử dụng OR-Tools Linear Solver (MIP - Mixed Integer Programming)
# Sử dụng SCIP solver (có thể thay bằng CBC nếu không có SCIP)
solver = pywraplp.Solver.CreateSolver('SCIP')
if not solver:
    solver = pywraplp.Solver.CreateSolver('CBC')

num_cores = 40

N, M, K = map(int, input().split())
a, b, c, d, e, f = map(int, input().split())
s = [[0] for _ in range(N+1)]
for i in range(1, N+1):
    s[i] = [0] + list(map(int, input().split()))
g = [[0] for _ in range(N+1)]
for i in range(1, N+1):
    g[i] = [0] + list(map(int, input().split()))
t = [0] + list(map(int, input().split()))


solver.SetTimeLimit(144000000)  # 40 giờ

# Tối ưu tham số cho MIP solver dựa trên solver được sử dụng
try:
    solver_name = solver.SolverVersion()
    if 'SCIP' in solver_name:
        solver.SetSolverSpecificParametersAsString('limits/time = 144000000')
        solver.SetSolverSpecificParametersAsString(f'parallel/maxnthreads = {num_cores}')
        solver.SetSolverSpecificParametersAsString('presolving/maxrounds = 100')
        solver.SetSolverSpecificParametersAsString('separating/maxrounds = 10')
        solver.SetSolverSpecificParametersAsString(f'lp/threads = {num_cores}')
    elif 'CBC' in solver_name:
        solver.SetSolverSpecificParametersAsString(f'threads {num_cores}')
        solver.SetSolverSpecificParametersAsString('seconds 144000000')
        solver.SetSolverSpecificParametersAsString('preprocess on')
except:
    pass

# x[i, k] = 1 nếu đồ án i được phân vào hội đồng k
x = {}
for i in range(1, N + 1):
    for k in range(1, K + 1):
        x[i, k] = solver.IntVar(0, 1, f'x{i}_{k}')

# y[j, k] = 1 nếu giáo viên j được phân vào hội đồng k
y = {}
for j in range(1, M + 1):
    for k in range(1, K + 1):
        y[j, k] = solver.IntVar(0, 1, f'y{j}_{k}')

# Ràng buộc số lượng đồ án và giáo viên trong mỗi hội đồng
for k in range(1, K+1):
    # Số đồ án trong hội đồng k: a <= sum(x[i,k]) <= b
    constraint_proj_min = solver.Constraint(a, solver.infinity(), f'min_proj_k{k}')
    constraint_proj_max = solver.Constraint(-solver.infinity(), b, f'max_proj_k{k}')
    for i in range(1, N+1):
        constraint_proj_min.SetCoefficient(x[i, k], 1)
        constraint_proj_max.SetCoefficient(x[i, k], 1)
    
    # Số giáo viên trong hội đồng k: c <= sum(y[j,k]) <= d
    constraint_teach_min = solver.Constraint(c, solver.infinity(), f'min_teach_k{k}')
    constraint_teach_max = solver.Constraint(-solver.infinity(), d, f'max_teach_k{k}')
    for j in range(1, M+1):
        constraint_teach_min.SetCoefficient(y[j, k], 1)
        constraint_teach_max.SetCoefficient(y[j, k], 1)

# Ràng buộc phân bổ: mỗi đồ án và giáo viên phải thuộc đúng 1 hội đồng
for i in range(1, N+1):
    constraint = solver.Constraint(1, 1, f'unique_project_{i}')
    for k in range(1, K+1):
        constraint.SetCoefficient(x[i, k], 1)

for j in range(1, M+1):
    constraint = solver.Constraint(1, 1, f'unique_teacher_{j}')
    for k in range(1, K+1):
        constraint.SetCoefficient(y[j, k], 1)

# Ràng buộc xung đột: giáo viên không được ngồi hội đồng của sinh viên mình hướng dẫn
for i in range(1, N+1):
    for k in range(1, K+1):
        constraint = solver.Constraint(-solver.infinity(), 1, f'conflict_{i}_{k}')
        constraint.SetCoefficient(x[i, k], 1)
        constraint.SetCoefficient(y[t[i], k], 1)

# Ràng buộc ngưỡng tương đồng đồ án: áp dụng mệnh đề phản đảo
for i1 in range(1, N + 1):
    for i2 in range(i1 + 1, N + 1):
        if s[i1][i2] < e:
            for k in range(1, K + 1):
                constraint = solver.Constraint(-solver.infinity(), 1, f'sim_proj_{i1}_{i2}_k{k}')
                constraint.SetCoefficient(x[i1, k], 1)
                constraint.SetCoefficient(x[i2, k], 1)

# Ràng buộc ngưỡng tương đồng giáo viên: áp dụng mệnh đề phản đảo
for i in range(1, N + 1):
    for j in range(1, M + 1):
        if g[i][j] < f:
            for k in range(1, K + 1):
                constraint = solver.Constraint(-solver.infinity(), 1, f'sim_teach_{i}_{j}_k{k}')
                constraint.SetCoefficient(x[i, k], 1)
                constraint.SetCoefficient(y[j, k], 1)

# Xây dựng hàm mục tiêu: tối đa hóa tổng độ tương đồng
objective = solver.Objective()

# Tạo biến phụ trợ cho tích của 2 biến Boolean
# z[i1, i2, k] = x[i1, k] * x[i2, k]
z = {}
for k in range(1, K + 1):
    for i1 in range(1, N + 1):
        for i2 in range(i1 + 1, N + 1):
            if s[i1][i2] >= e:
                z[i1, i2, k] = solver.IntVar(0, 1, f'z_{i1}_{i2}_k{k}')
                # Ràng buộc: z <= x[i1, k] và z <= x[i2, k]
                constraint1 = solver.Constraint(-solver.infinity(), 0, f'z1_{i1}_{i2}_k{k}')
                constraint1.SetCoefficient(z[i1, i2, k], 1)
                constraint1.SetCoefficient(x[i1, k], -1)
                
                constraint2 = solver.Constraint(-solver.infinity(), 0, f'z2_{i1}_{i2}_k{k}')
                constraint2.SetCoefficient(z[i1, i2, k], 1)
                constraint2.SetCoefficient(x[i2, k], -1)
                
                # Thêm vào objective
                objective.SetCoefficient(z[i1, i2, k], s[i1][i2])

# w[i, j, k] = x[i, k] * y[j, k]
w = {}
for k in range(1, K + 1):
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if t[i] != j and g[i][j] >= f:
                w[i, j, k] = solver.IntVar(0, 1, f'w_{i}_{j}_k{k}')
                # Ràng buộc: w <= x[i, k] và w <= y[j, k]
                constraint1 = solver.Constraint(-solver.infinity(), 0, f'w1_{i}_{j}_k{k}')
                constraint1.SetCoefficient(w[i, j, k], 1)
                constraint1.SetCoefficient(x[i, k], -1)
                
                constraint2 = solver.Constraint(-solver.infinity(), 0, f'w2_{i}_{j}_k{k}')
                constraint2.SetCoefficient(w[i, j, k], 1)
                constraint2.SetCoefficient(y[j, k], -1)
                
                # Thêm vào objective
                objective.SetCoefficient(w[i, j, k], g[i][j])

objective.SetMaximization()

# Giải bài toán
start_time = time.time()
status = solver.Solve()
end_time = time.time()
execution_time = end_time - start_time

if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
    print(N)
    result_x = []
    for i in range(1, N + 1):
        for k in range(1, K + 1):
            if x[i, k].solution_value() > 0.5:
                result_x.append(str(k))
                break
    print(' '.join(result_x))
    
    print(M)
    result_y = []
    for j in range(1, M + 1):
        for k in range(1, K + 1):
            if y[j, k].solution_value() > 0.5:
                result_y.append(str(k))
                break
    print(' '.join(result_y))
    objective_value = solver.Objective().Value()
    if status == pywraplp.Solver.OPTIMAL:
        print(f"Objective value: {int(objective_value)} (OPTIMAL - exact solution)")
    else:
        print(f"Objective value: {int(objective_value)} (FEASIBLE - may not be optimal)")
    print(f"Execution time: {execution_time:.5f} seconds")


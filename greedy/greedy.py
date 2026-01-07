class Thesis:
    def __init(self, ID):
        self.ID = ID
        self.teacher: Teacher = None
        self.council = 0

class Teacher:
    def __init__(self, ID):
        self.ID = ID
        self.load = 0
        self.theses = []
        self.council = 0
        self.min_similarity = {}

class Council:
    def __init__(self, ID):
        self.ID = ID
        self.load = 0
        self.theses = []
        self.teachers = []

def import_data():
    s = []
    g = []
    N, M, K = map(int, input().split())

    theses = [Thesis(i) for i in range(N + 1)]
    teachers = [Teacher(i) for i in range(M + 1)]
    councils = [Council(i) for i in range(K + 1)]

    a, b, c, d, e, f = map(int, input().split())
    for _ in range(N):
        s.append(list(map(int, input().split())))

    for _ in range(M):
        g.append(list(map(int, input().split())))

    t = [0]
    t += list(map(int, input().split()))
    for i in range(1, N + 1):
        theses[i].teacher = teachers[t[i]]
        teachers[t[i]].load += 1
        teachers[t[i]].theses.append(theses[i])

    return theses, teachers, councils, a, b, c, d, e, f, s, g, N, M, K

class Solver:
    def __init__(self, theses, teachers, councils, a, b, c, d, e, f, s, g, N, M, K):
        self.theses = theses
        self.teachers = teachers
        self.councils = councils
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.s = s
        self.g = g
        self.N = N
        self.M = M
        self.K = K

    def solve(self):
        # Implementation of the greedy algorithm goes here
        pass
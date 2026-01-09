import random


class Thesis:
    def __init__(self, ID):
        self.ID = ID
        self.teacher = None
        self.council = 0


class Teacher:
    def __init__(self, ID):
        self.ID = ID
        self.load = 0
        self.thesises = []
        self.council = 0
        self.min_similarity = {}


class Council:
    def __init__(self, ID):
        self.ID = ID
        self. load = 0
        self.thesises = []
        self. teachers = []


def import_data():
    s = []
    g = []
    N, M, K = map(int, input().split())

    thesises = [Thesis(i + 1) for i in range(N)]
    teachers = [Teacher(i + 1) for i in range(M)]
    councils = [Council(i + 1) for i in range(K)]

    a, b, c, d, e, f = map(int, input().split())

    for _ in range(N):
        s.append(list(map(int, input().split())))

    for _ in range(N):
        g.append(list(map(int, input().split())))

    t = list(map(int, input().split()))

    for i in range(N):
        thesises[i].teacher = teachers[t[i] - 1]
        teachers[t[i] - 1].load += 1
        teachers[t[i] - 1].thesises.append(i + 1)

    for t1 in range(M):
        for t2 in range(t1 + 1, M):
            teacher1 = teachers[t1]
            teacher2 = teachers[t2]
            teacher1.min_similarity[teacher2] = float('inf')
            for i1 in range(len(teacher1.thesises)):
                s1 = teacher1.thesises[i1]
                for i2 in range(len(teacher2.thesises)):
                    s2 = teacher2.thesises[i2]
                    if teacher1.min_similarity[teacher2] > s[s1 - 1][s2 - 1] and s1 != s2 and s[s1 - 1][s2 - 1] > 0:
                        teacher1.min_similarity[teacher2] = s[s1 - 1][s2 - 1]
            teacher2.min_similarity[teacher1] = teacher1.min_similarity[teacher2]

    return thesises, teachers, councils, a, b, c, d, e, f, s, g


class Solver:
    def __init__(self, thesises, teachers, councils, a, b, c, d, e, f, s, g):
        self.N = len(thesises)
        self.thesises = thesises
        self.M = len(teachers)
        self.teachers = teachers
        self.K = len(councils)
        self.councils = councils
        self. a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.s = s
        self.g = g

        self.best_thesis = [0] * self.N
        self.best_teacher = [0] * self.M
        self. best_score = -float('inf')

    def can_teacher_join(self, teacher, council):
        if len(council.teachers) >= self. d:
            return False
        for th in council.thesises:
            if self.g[th. ID - 1][teacher.ID - 1] < self.f:
                return False
            if th.teacher == teacher:
                return False
        for te in council.teachers:
            if teacher.min_similarity. get(te, float('inf')) < self.e:
                return False
        return True

    def can_thesis_join(self, thesis, council):
        if len(council.thesises) >= self.b:
            return False
        for th in council.thesises:
            if self.s[thesis.ID - 1][th. ID - 1] < self. e:
                return False
        for te in council.teachers:
            if te == thesis.teacher:
                return False
            if self.g[thesis.ID - 1][te. ID - 1] < self. f:
                return False
        return True

    def thesis_score(self, thesis, council):
        score = 0
        for th in council.thesises:
            if th.ID != thesis.ID:
                score += self.s[thesis.ID - 1][th. ID - 1]
        for te in council.teachers:
            score += self.g[thesis.ID - 1][te.ID - 1]
        return score

    def teacher_score(self, teacher, council):
        return sum(self.g[th.ID - 1][teacher.ID - 1] for th in council.thesises)

    def total_score(self):
        total = 0
        for c in self.councils:
            for i, t1 in enumerate(c.thesises):
                for t2 in c.thesises[i + 1:]:
                    total += self.s[t1.ID - 1][t2.ID - 1]
                for te in c.teachers:
                    total += self.g[t1.ID - 1][te. ID - 1]
        return total

    def save_best(self):
        score = self.total_score()
        if score > self.best_score:
            self.best_score = score
            for i, th in enumerate(self. thesises):
                self.best_thesis[i] = th.council
            for i, te in enumerate(self.teachers):
                self.best_teacher[i] = te.council

    def restore_best(self):
        for c in self.councils:
            c.thesises = []
            c.teachers = []
            c.load = 0
        for i, th in enumerate(self. thesises):
            th.council = self.best_thesis[i]
            if th.council > 0:
                self.councils[th.council - 1]. thesises.append(th)
        for i, te in enumerate(self.teachers):
            te.council = self.best_teacher[i]
            if te. council > 0:
                self.councils[te.council - 1].teachers.append(te)
                self.councils[te.council - 1]. load += te.load

    def clear(self):
        for c in self.councils:
            c.thesises = []
            c.teachers = []
            c.load = 0
        for th in self.thesises:
            th.council = 0
        for te in self.teachers:
            te.council = 0

    def greedy_teachers(self, order):
        for te in order:
            best_k, best_score = -1, -float('inf')
            for k, c in enumerate(self.councils):
                if self.can_teacher_join(te, c):
                    score = self.teacher_score(te, c)
                    if len(c.teachers) < self.c:
                        score += 10000
                    if score > best_score:
                        best_score = score
                        best_k = k
            if best_k >= 0:
                te.council = best_k + 1
                self.councils[best_k]. teachers.append(te)
                self.councils[best_k]. load += te.load

    def greedy_theses(self, order):
        for th in order:
            best_k, best_score = -1, -float('inf')
            for k, c in enumerate(self.councils):
                if self.can_thesis_join(th, c):
                    score = self.thesis_score(th, c)
                    if len(c.thesises) < self.a:
                        score += 10000
                    if score > best_score:
                        best_score = score
                        best_k = k
            if best_k >= 0:
                th.council = best_k + 1
                self.councils[best_k].thesises.append(th)

    def local_search(self, max_iter=100):
        """Combined fast local search"""
        for _ in range(max_iter):
            improved = False

            # Move thesis
            for th in self.thesises:
                if th.council == 0:
                    continue
                curr = self.councils[th.council - 1]
                if len(curr.thesises) <= self.a:
                    continue

                curr_score = self.thesis_score(th, curr)
                curr.thesises.remove(th)

                best_gain, best_c = 0, None
                for c in self.councils:
                    if c. ID == th.council:
                        continue
                    if self.can_thesis_join(th, c):
                        gain = self. thesis_score(th, c) - curr_score
                        if gain > best_gain:
                            best_gain = gain
                            best_c = c

                if best_c: 
                    th.council = best_c.ID
                    best_c.thesises.append(th)
                    improved = True
                else:
                    curr. thesises.append(th)

            # Swap theses
            for i in range(self.N):
                t1 = self.thesises[i]
                if t1.council == 0:
                    continue
                for j in range(i + 1, self.N):
                    t2 = self.thesises[j]
                    if t2.council == 0 or t1.council == t2.council:
                        continue

                    c1, c2 = self.councils[t1.council - 1], self.councils[t2.council - 1]
                    old = self.thesis_score(t1, c1) + self.thesis_score(t2, c2)

                    c1.thesises.remove(t1)
                    c2.thesises.remove(t2)

                    if self. can_thesis_join(t1, c2) and self.can_thesis_join(t2, c1):
                        new = self.thesis_score(t1, c2) + self.thesis_score(t2, c1)
                        if new > old:
                            t1.council, t2.council = c2.ID, c1.ID
                            c2.thesises.append(t1)
                            c1.thesises.append(t2)
                            improved = True
                            continue

                    c1.thesises.append(t1)
                    c2.thesises.append(t2)

            # Move teacher
            for te in self.teachers:
                if te.council == 0:
                    continue
                curr = self.councils[te.council - 1]
                if len(curr.teachers) <= self.c:
                    continue

                curr_score = self.teacher_score(te, curr)
                curr.teachers.remove(te)
                curr.load -= te.load

                best_gain, best_c = 0, None
                for c in self.councils:
                    if c.ID == te.council:
                        continue
                    if self.can_teacher_join(te, c):
                        gain = self.teacher_score(te, c) - curr_score
                        if gain > best_gain:
                            best_gain = gain
                            best_c = c

                if best_c:
                    te. council = best_c.ID
                    best_c.teachers. append(te)
                    best_c.load += te.load
                    improved = True
                else: 
                    curr.teachers.append(te)
                    curr.load += te.load

            if not improved:
                break

    def get_teacher_orders(self):
        """Generate diverse teacher orderings"""
        orders = [
            sorted(self.teachers, key=lambda t: -t.load),
            sorted(self.teachers, key=lambda t: t.load),
            sorted(self.teachers, key=lambda t: -sum(self.g[i][t.ID - 1] for i in range(self.N))),
            sorted(self.teachers, key=lambda t: t.ID),
            sorted(self.teachers, key=lambda t: -t.ID),
        ]
        # Add random orderings
        for seed in range(3):
            random.seed(seed * 42)
            order = self.teachers[:]
            random.shuffle(order)
            orders.append(order)
        return orders

    def get_thesis_orders(self):
        """Generate diverse thesis orderings"""
        orders = [
            sorted(self.thesises, key=lambda t: -t.teacher.load),
            sorted(self.thesises, key=lambda t: t.teacher.load),
            sorted(self.thesises, key=lambda t: -sum(self.s[t.ID - 1])),
            sorted(self.thesises, key=lambda t: t.ID),
            sorted(self.thesises, key=lambda t: -t.ID),
        ]
        # Add random orderings
        for seed in range(3):
            random.seed(seed * 42 + 7)
            order = self.thesises[:]
            random. shuffle(order)
            orders. append(order)
        return orders

    def solve(self):
        teacher_orders = self.get_teacher_orders()
        thesis_orders = self.get_thesis_orders()

        # Limit combinations based on problem size
        if self.N <= 20:
            max_t_orders = len(teacher_orders)
            max_th_orders = len(thesis_orders)
        else:
            max_t_orders = min(5, len(teacher_orders))
            max_th_orders = min(5, len(thesis_orders))

        for t_idx, t_order in enumerate(teacher_orders[: max_t_orders]):
            self.clear()
            self.greedy_teachers(t_order)

            # Save teacher state
            teacher_state = [(te.council, [list(c.teachers) for c in self.councils],
                              [c.load for c in self.councils]) for te in self.teachers]

            for th_idx, th_order in enumerate(thesis_orders[:max_th_orders]):
                # Restore teacher state, clear theses
                for c in self.councils:
                    c.thesises = []
                for th in self.thesises:
                    th.council = 0

                self.greedy_theses(th_order)
                self.local_search(max_iter=50)
                self.save_best()

        self.restore_best()

    def print_sol(self):
        print(self.N)
        print(" ".join(str(th. council) for th in self.thesises))
        print(self.M)
        print(" ".join(str(te.council) for te in self.teachers))


def main():
    thesises, teachers, councils, a, b, c, d, e, f, s, g = import_data()
    sol = Solver(thesises, teachers, councils, a, b, c, d, e, f, s, g)
    sol.solve()
    sol.print_sol()


if __name__ == "__main__":
    main()

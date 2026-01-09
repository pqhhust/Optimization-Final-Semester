class Thesis:
    def __init__(self, ID):
        self.ID = ID
        self.teacher = None
        self.council = 0


class Teacher:
    def __init__(self, ID):
        self.ID = ID
        self. load = 0
        self. thesises = []
        self.council = 0
        self.min_similarity = {}


class Council:
    def __init__(self, ID):
        self.ID = ID
        self.load = 0
        self.thesises = []
        self.teachers = []


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
        thesises[i]. teacher = teachers[t[i] - 1]
        teachers[t[i] - 1]. load += 1
        teachers[t[i] - 1]. thesises.append(i + 1)

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
        self. M = len(teachers)
        self.teachers = teachers
        self.K = len(councils)
        self.councils = councils
        self.a = a
        self.b = b
        self. c = c
        self. d = d
        self.e = e
        self.f = f
        self.s = s
        self.g = g

    def can_teacher_join_council(self, teacher, council):
        """Check all constraints for teacher joining council"""
        # Check max teachers
        if len(council.teachers) >= self.d:
            return False

        # Check thesis-teacher similarity and supervisor conflict
        for thesis in council.thesises:
            if self. g[thesis.ID - 1][teacher.ID - 1] < self.f:
                return False
            if thesis.teacher == teacher:
                return False

        # Check teacher-teacher compatibility
        for cteacher in council.teachers:
            if teacher.min_similarity. get(cteacher, float('inf')) < self.e:
                return False

        return True

    def can_thesis_join_council(self, thesis, council):
        """Check all constraints for thesis joining council"""
        # Check max theses
        if len(council.thesises) >= self.b:
            return False

        # Check thesis-thesis similarity
        for cthesis in council. thesises:
            if self.s[thesis.ID - 1][cthesis.ID - 1] < self.e:
                return False

        # Check supervisor conflict
        for teacher in council.teachers:
            if teacher == thesis.teacher:
                return False
            # Check thesis-teacher similarity
            if self.g[thesis.ID - 1][teacher.ID - 1] < self.f:
                return False

        return True

    def thesis_score(self, thesis, council):
        """Calculate score for adding thesis to council"""
        score = 0
        for cthesis in council.thesises:
            score += self.s[thesis.ID - 1][cthesis. ID - 1]
        for teacher in council.teachers:
            score += self.g[thesis.ID - 1][teacher.ID - 1]
        return score

    def teacher_score(self, teacher, council):
        """Calculate score for adding teacher to council"""
        score = 0
        for thesis in council.thesises:
            score += self.g[thesis.ID - 1][teacher.ID - 1]
        return score

    def Teacher2Council(self):
        """Assign teachers to councils"""
        # Sort teachers by load (more students = harder to place, do first)
        sorted_teachers = sorted(self.teachers, key=lambda t: -t.load)

        for teacher in sorted_teachers:
            candidate_councils = []

            for council in self.councils:
                if self.can_teacher_join_council(teacher, council):
                    score = self.teacher_score(teacher, council)
                    # Prefer councils needing more teachers
                    balance_bonus = (self.c - len(council.teachers)) * 100 if len(council.teachers) < self.c else 0
                    candidate_councils.append((council.ID, score + balance_bonus))

            if candidate_councils:
                # Choose by score, then by load for balance
                best_council = max(candidate_councils, key=lambda x: (x[1], -self.councils[x[0] - 1].load))[0]
                teacher.council = best_council
                self. councils[best_council - 1].teachers.append(teacher)
                self.councils[best_council - 1].load += teacher. load

    def Thesis2Council(self):
        """Assign theses to councils"""
        # Sort theses by difficulty (fewer valid councils = harder)
        def count_valid_councils(thesis):
            count = 0
            for council in self.councils:
                if self.can_thesis_join_council(thesis, council):
                    count += 1
            return count

        sorted_theses = sorted(self.thesises, key=lambda t: count_valid_councils(t))

        for thesis in sorted_theses:
            candidate_councils = []

            for council in self.councils:
                if self.can_thesis_join_council(thesis, council):
                    score = self.thesis_score(thesis, council)
                    # Prefer councils needing more theses
                    balance_bonus = (self.a - len(council.thesises)) * 100 if len(council.thesises) < self.a else 0
                    candidate_councils. append((council.ID, score + balance_bonus))

            if candidate_councils:
                # Choose by score, then by count for balance
                best_council = max(candidate_councils, key=lambda x: (x[1], -len(self.councils[x[0] - 1].thesises)))[0]
                thesis.council = best_council
                self. councils[best_council - 1].thesises.append(thesis)

    def local_search_theses(self):
        """Improve thesis assignments"""
        improved = True
        iterations = 0
        max_iter = 100

        while improved and iterations < max_iter:
            improved = False
            iterations += 1

            for thesis in self.thesises:
                if thesis.council == 0:
                    continue

                current_council = self.councils[thesis.council - 1]
                current_score = self.thesis_score(thesis, current_council)

                # Skip if removing would violate minimum
                if len(current_council.thesises) <= self.a: 
                    continue

                # Try moving to another council
                for council in self. councils:
                    if council. ID == thesis.council:
                        continue

                    # Temporarily remove
                    current_council.thesises.remove(thesis)

                    if self.can_thesis_join_council(thesis, council):
                        new_score = self.thesis_score(thesis, council)
                        if new_score > current_score:
                            thesis.council = council.ID
                            council.thesises.append(thesis)
                            improved = True
                            break

                    # Revert
                    current_council. thesises.append(thesis)

                if improved:
                    break

    def local_search_swap_theses(self):
        """Try swapping theses between councils"""
        improved = True
        iterations = 0
        max_iter = 50

        while improved and iterations < max_iter:
            improved = False
            iterations += 1

            for i, thesis1 in enumerate(self.thesises):
                if thesis1.council == 0:
                    continue

                for thesis2 in self.thesises[i + 1:]:
                    if thesis2.council == 0 or thesis1.council == thesis2.council:
                        continue

                    c1 = self.councils[thesis1.council - 1]
                    c2 = self. councils[thesis2.council - 1]

                    old_score = (self.thesis_score(thesis1, c1) + self.thesis_score(thesis2, c2))

                    # Remove both
                    c1.thesises.remove(thesis1)
                    c2.thesises.remove(thesis2)

                    # Check if swap is valid
                    can_swap = (self.can_thesis_join_council(thesis1, c2) and
                                self.can_thesis_join_council(thesis2, c1))

                    if can_swap:
                        new_score = (self.thesis_score(thesis1, c2) + self.thesis_score(thesis2, c1))

                        if new_score > old_score:
                            thesis1.council = c2.ID
                            thesis2.council = c1.ID
                            c2.thesises.append(thesis1)
                            c1.thesises.append(thesis2)
                            improved = True
                            break

                    # Revert
                    c1.thesises.append(thesis1)
                    c2.thesises.append(thesis2)

                if improved:
                    break

    def local_search_teachers(self):
        """Improve teacher assignments"""
        improved = True
        iterations = 0
        max_iter = 50

        while improved and iterations < max_iter:
            improved = False
            iterations += 1

            for teacher in self.teachers:
                if teacher.council == 0:
                    continue

                current_council = self.councils[teacher.council - 1]
                current_score = self.teacher_score(teacher, current_council)

                # Skip if removing would violate minimum
                if len(current_council.teachers) <= self.c:
                    continue

                for council in self.councils:
                    if council.ID == teacher.council:
                        continue

                    # Temporarily remove
                    current_council.teachers.remove(teacher)
                    current_council.load -= teacher.load

                    if self. can_teacher_join_council(teacher, council):
                        new_score = self.teacher_score(teacher, council)
                        if new_score > current_score:
                            teacher.council = council.ID
                            council. teachers.append(teacher)
                            council.load += teacher.load
                            improved = True
                            break

                    # Revert
                    current_council.teachers. append(teacher)
                    current_council.load += teacher.load

                if improved:
                    break

    def solve(self):
        self.Teacher2Council()
        self.Thesis2Council()

        # Local search improvements
        for _ in range(3):
            self.local_search_theses()
            self.local_search_swap_theses()
            self.local_search_teachers()

    def print_sol(self):
        print(self.N)
        for thesis in self.thesises:
            print(thesis. council, end=" ")
        print()
        print(self.M)
        for teacher in self.teachers:
            print(teacher.council, end=" ")
        print()


def main():
    thesises, teachers, councils, a, b, c, d, e, f, s, g = import_data()
    sol = Solver(thesises, teachers, councils, a, b, c, d, e, f, s, g)
    sol.solve()
    sol.print_sol()


if __name__ == "__main__":
    main()

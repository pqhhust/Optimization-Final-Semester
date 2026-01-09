import random
import math


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
        self.M = len(teachers)
        self.teachers = teachers
        self. K = len(councils)
        self.councils = councils
        self.a = a
        self. b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.s = s
        self.g = g
        
        # Best solution storage
        self.best_thesis_assignment = [0] * self.N
        self.best_teacher_assignment = [0] * self.M
        self.best_score = -float('inf')

    def can_teacher_join_council(self, teacher, council):
        if len(council.teachers) >= self.d:
            return False
        for thesis in council.thesises:
            if self.g[thesis.ID - 1][teacher. ID - 1] < self. f:
                return False
            if thesis.teacher == teacher:
                return False
        for cteacher in council.teachers:
            if teacher.min_similarity.get(cteacher, float('inf')) < self.e:
                return False
        return True

    def can_thesis_join_council(self, thesis, council):
        if len(council.thesises) >= self.b:
            return False
        for cthesis in council.thesises:
            if self.s[thesis.ID - 1][cthesis.ID - 1] < self.e:
                return False
        for teacher in council.teachers:
            if teacher == thesis.teacher:
                return False
            if self. g[thesis.ID - 1][teacher.ID - 1] < self.f:
                return False
        return True

    def thesis_score_in_council(self, thesis, council):
        score = 0
        for cthesis in council. thesises:
            if cthesis.ID != thesis.ID:
                score += self.s[thesis.ID - 1][cthesis.ID - 1]
        for teacher in council.teachers:
            score += self.g[thesis.ID - 1][teacher.ID - 1]
        return score

    def teacher_score_in_council(self, teacher, council):
        score = 0
        for thesis in council.thesises:
            score += self.g[thesis.ID - 1][teacher.ID - 1]
        return score

    def calculate_total_score(self):
        total = 0
        for council in self.councils:
            theses_list = council.thesises
            for i in range(len(theses_list)):
                for j in range(i + 1, len(theses_list)):
                    total += self.s[theses_list[i]. ID - 1][theses_list[j].ID - 1]
            for thesis in theses_list:
                for teacher in council.teachers:
                    total += self.g[thesis.ID - 1][teacher. ID - 1]
        return total

    def save_best_solution(self):
        score = self.calculate_total_score()
        if score > self. best_score:
            self. best_score = score
            for i, thesis in enumerate(self.thesises):
                self.best_thesis_assignment[i] = thesis.council
            for i, teacher in enumerate(self.teachers):
                self.best_teacher_assignment[i] = teacher. council

    def restore_best_solution(self):
        # Clear councils
        for council in self.councils:
            council.thesises = []
            council.teachers = []
            council.load = 0
        
        # Restore assignments
        for i, thesis in enumerate(self.thesises):
            thesis.council = self.best_thesis_assignment[i]
            if thesis.council > 0:
                self.councils[thesis.council - 1].thesises.append(thesis)
        
        for i, teacher in enumerate(self.teachers):
            teacher.council = self.best_teacher_assignment[i]
            if teacher.council > 0:
                self.councils[teacher.council - 1]. teachers.append(teacher)
                self.councils[teacher.council - 1].load += teacher.load

    def Teacher2Council(self):
        sorted_teachers = sorted(self.teachers, key=lambda t: -t.load)
        
        for teacher in sorted_teachers: 
            candidate_councils = []
            
            for council in self.councils:
                if self.can_teacher_join_council(teacher, council):
                    score = self. teacher_score_in_council(teacher, council)
                    balance_bonus = (self.c - len(council.teachers)) * 1000 if len(council.teachers) < self.c else 0
                    candidate_councils.append((council.ID, score + balance_bonus))
            
            if candidate_councils:
                best_council = max(candidate_councils, key=lambda x: (x[1], -self.councils[x[0] - 1].load))[0]
                teacher.council = best_council
                self.councils[best_council - 1].teachers.append(teacher)
                self.councils[best_council - 1].load += teacher.load

    def Thesis2Council(self):
        def count_valid_councils(thesis):
            return sum(1 for council in self. councils if self.can_thesis_join_council(thesis, council))
        
        sorted_theses = sorted(self.thesises, key=lambda t: count_valid_councils(t))
        
        for thesis in sorted_theses:
            candidate_councils = []
            
            for council in self.councils:
                if self.can_thesis_join_council(thesis, council):
                    score = self.thesis_score_in_council(thesis, council)
                    balance_bonus = (self.a - len(council.thesises)) * 1000 if len(council.thesises) < self.a else 0
                    candidate_councils.append((council.ID, score + balance_bonus))
            
            if candidate_councils:
                best_council = max(candidate_councils, key=lambda x: (x[1], -len(self.councils[x[0] - 1].thesises)))[0]
                thesis.council = best_council
                self.councils[best_council - 1].thesises.append(thesis)

    def try_move_thesis(self, thesis):
        """Try to move a thesis to a better council"""
        if thesis.council == 0:
            return False
        
        current_council = self.councils[thesis.council - 1]
        
        if len(current_council.thesises) <= self.a:
            return False
        
        current_score = self.thesis_score_in_council(thesis, current_council)
        best_gain = 0
        best_target = None
        
        current_council.thesises.remove(thesis)
        
        for council in self.councils:
            if council.ID == thesis.council:
                continue
            
            if self.can_thesis_join_council(thesis, council):
                new_score = self.thesis_score_in_council(thesis, council)
                gain = new_score - current_score
                if gain > best_gain:
                    best_gain = gain
                    best_target = council
        
        if best_target: 
            thesis.council = best_target.ID
            best_target.thesises.append(thesis)
            return True
        else:
            current_council.thesises.append(thesis)
            return False

    def try_swap_theses(self, thesis1, thesis2):
        """Try swapping two theses between councils"""
        if thesis1.council == 0 or thesis2.council == 0:
            return False
        if thesis1.council == thesis2.council:
            return False
        
        c1 = self.councils[thesis1.council - 1]
        c2 = self.councils[thesis2.council - 1]
        
        old_score = (self.thesis_score_in_council(thesis1, c1) + 
                     self.thesis_score_in_council(thesis2, c2))
        
        c1.thesises.remove(thesis1)
        c2.thesises.remove(thesis2)
        
        can_swap = (self.can_thesis_join_council(thesis1, c2) and 
                    self.can_thesis_join_council(thesis2, c1))
        
        if can_swap:
            new_score = (self.thesis_score_in_council(thesis1, c2) + 
                         self. thesis_score_in_council(thesis2, c1))
            
            if new_score > old_score:
                thesis1.council = c2.ID
                thesis2.council = c1.ID
                c2.thesises.append(thesis1)
                c1.thesises.append(thesis2)
                return True
        
        c1.thesises.append(thesis1)
        c2.thesises.append(thesis2)
        return False

    def try_move_teacher(self, teacher):
        """Try to move a teacher to a better council"""
        if teacher.council == 0:
            return False
        
        current_council = self.councils[teacher.council - 1]
        
        if len(current_council.teachers) <= self.c:
            return False
        
        current_score = self.teacher_score_in_council(teacher, current_council)
        best_gain = 0
        best_target = None
        
        current_council.teachers.remove(teacher)
        current_council.load -= teacher.load
        
        for council in self.councils:
            if council. ID == teacher.council:
                continue
            
            if self. can_teacher_join_council(teacher, council):
                new_score = self.teacher_score_in_council(teacher, council)
                gain = new_score - current_score
                if gain > best_gain:
                    best_gain = gain
                    best_target = council
        
        if best_target:
            teacher.council = best_target.ID
            best_target.teachers. append(teacher)
            best_target.load += teacher.load
            return True
        else: 
            current_council.teachers. append(teacher)
            current_council.load += teacher.load
            return False

    def try_swap_teachers(self, teacher1, teacher2):
        """Try swapping two teachers between councils"""
        if teacher1.council == 0 or teacher2.council == 0:
            return False
        if teacher1.council == teacher2.council:
            return False
        
        c1 = self.councils[teacher1.council - 1]
        c2 = self.councils[teacher2.council - 1]
        
        old_score = (self.teacher_score_in_council(teacher1, c1) + 
                     self.teacher_score_in_council(teacher2, c2))
        
        c1.teachers.remove(teacher1)
        c1.load -= teacher1.load
        c2.teachers.remove(teacher2)
        c2.load -= teacher2.load
        
        can_swap = (self.can_teacher_join_council(teacher1, c2) and 
                    self.can_teacher_join_council(teacher2, c1))
        
        if can_swap:
            new_score = (self.teacher_score_in_council(teacher1, c2) + 
                         self.teacher_score_in_council(teacher2, c1))
            
            if new_score > old_score:
                teacher1.council = c2.ID
                teacher2.council = c1.ID
                c2.teachers.append(teacher1)
                c2.load += teacher1.load
                c1.teachers.append(teacher2)
                c1.load += teacher2.load
                return True
        
        c1.teachers.append(teacher1)
        c1.load += teacher1.load
        c2.teachers.append(teacher2)
        c2.load += teacher2.load
        return False

    def local_search(self):
        """Exhaustive local search"""
        improved = True
        while improved: 
            improved = False
            
            # Try moving each thesis
            for thesis in self.thesises:
                if self.try_move_thesis(thesis):
                    improved = True
            
            # Try swapping theses
            for i in range(self.N):
                for j in range(i + 1, self.N):
                    if self.try_swap_theses(self.thesises[i], self.thesises[j]):
                        improved = True
            
            # Try moving each teacher
            for teacher in self.teachers:
                if self.try_move_teacher(teacher):
                    improved = True
            
            # Try swapping teachers
            for i in range(self.M):
                for j in range(i + 1, self.M):
                    if self.try_swap_teachers(self.teachers[i], self.teachers[j]):
                        improved = True

    def simulated_annealing(self, initial_temp=1000, cooling_rate=0.995, min_temp=1):
        """Simulated annealing to escape local optima"""
        temp = initial_temp
        current_score = self.calculate_total_score()
        
        while temp > min_temp:
            # Random move
            move_type = random.randint(0, 3)
            
            if move_type == 0:  # Move thesis
                thesis = random.choice(self.thesises)
                if thesis.council == 0:
                    temp *= cooling_rate
                    continue
                
                current_council = self.councils[thesis.council - 1]
                if len(current_council.thesises) <= self.a:
                    temp *= cooling_rate
                    continue
                
                target_councils = [c for c in self.councils if c.ID != thesis.council]
                if not target_councils: 
                    temp *= cooling_rate
                    continue
                
                target = random.choice(target_councils)
                
                current_council.thesises.remove(thesis)
                
                if self.can_thesis_join_council(thesis, target):
                    old_score = current_score
                    thesis.council = target.ID
                    target.thesises.append(thesis)
                    new_score = self.calculate_total_score()
                    
                    delta = new_score - old_score
                    if delta > 0 or random.random() < math.exp(delta / temp):
                        current_score = new_score
                    else:
                        target.thesises.remove(thesis)
                        thesis.council = current_council.ID
                        current_council.thesises.append(thesis)
                else:
                    current_council. thesises.append(thesis)
            
            elif move_type == 1:  # Swap theses
                if self.N < 2:
                    temp *= cooling_rate
                    continue
                
                t1, t2 = random. sample(self.thesises, 2)
                if t1.council == 0 or t2.council == 0 or t1.council == t2.council:
                    temp *= cooling_rate
                    continue
                
                c1 = self.councils[t1.council - 1]
                c2 = self.councils[t2.council - 1]
                
                c1.thesises.remove(t1)
                c2.thesises.remove(t2)
                
                if self. can_thesis_join_council(t1, c2) and self.can_thesis_join_council(t2, c1):
                    old_score = current_score
                    t1.council, t2.council = c2.ID, c1.ID
                    c2.thesises.append(t1)
                    c1.thesises.append(t2)
                    new_score = self.calculate_total_score()
                    
                    delta = new_score - old_score
                    if delta > 0 or random.random() < math.exp(delta / temp):
                        current_score = new_score
                    else:
                        c2.thesises.remove(t1)
                        c1.thesises.remove(t2)
                        t1.council, t2.council = c1.ID, c2.ID
                        c1.thesises. append(t1)
                        c2.thesises.append(t2)
                else: 
                    c1.thesises.append(t1)
                    c2.thesises.append(t2)
            
            elif move_type == 2:  # Move teacher
                teacher = random.choice(self. teachers)
                if teacher.council == 0:
                    temp *= cooling_rate
                    continue
                
                current_council = self.councils[teacher.council - 1]
                if len(current_council.teachers) <= self.c:
                    temp *= cooling_rate
                    continue
                
                target_councils = [c for c in self.councils if c.ID != teacher.council]
                if not target_councils: 
                    temp *= cooling_rate
                    continue
                
                target = random.choice(target_councils)
                
                current_council.teachers.remove(teacher)
                current_council.load -= teacher.load
                
                if self.can_teacher_join_council(teacher, target):
                    old_score = current_score
                    teacher.council = target.ID
                    target.teachers.append(teacher)
                    target.load += teacher.load
                    new_score = self.calculate_total_score()
                    
                    delta = new_score - old_score
                    if delta > 0 or random.random() < math.exp(delta / temp):
                        current_score = new_score
                    else: 
                        target.teachers.remove(teacher)
                        target.load -= teacher.load
                        teacher.council = current_council.ID
                        current_council.teachers.append(teacher)
                        current_council.load += teacher.load
                else:
                    current_council.teachers. append(teacher)
                    current_council.load += teacher.load
            
            else:  # Swap teachers
                if self.M < 2:
                    temp *= cooling_rate
                    continue
                
                te1, te2 = random. sample(self.teachers, 2)
                if te1.council == 0 or te2.council == 0 or te1.council == te2.council:
                    temp *= cooling_rate
                    continue
                
                c1 = self.councils[te1.council - 1]
                c2 = self. councils[te2.council - 1]
                
                c1.teachers.remove(te1)
                c1.load -= te1.load
                c2.teachers.remove(te2)
                c2.load -= te2.load
                
                if self.can_teacher_join_council(te1, c2) and self.can_teacher_join_council(te2, c1):
                    old_score = current_score
                    te1.council, te2.council = c2.ID, c1.ID
                    c2.teachers. append(te1)
                    c2.load += te1.load
                    c1.teachers.append(te2)
                    c1.load += te2.load
                    new_score = self.calculate_total_score()
                    
                    delta = new_score - old_score
                    if delta > 0 or random.random() < math.exp(delta / temp):
                        current_score = new_score
                    else:
                        c2.teachers.remove(te1)
                        c2.load -= te1.load
                        c1.teachers.remove(te2)
                        c1.load -= te2.load
                        te1.council, te2.council = c1.ID, c2.ID
                        c1.teachers.append(te1)
                        c1.load += te1.load
                        c2.teachers.append(te2)
                        c2.load += te2.load
                else:
                    c1.teachers.append(te1)
                    c1.load += te1.load
                    c2.teachers.append(te2)
                    c2.load += te2.load
            
            self.save_best_solution()
            temp *= cooling_rate

    def solve(self):
        # Initial assignment
        self.Teacher2Council()
        self.Thesis2Council()
        
        # Local search first
        self.local_search()
        self.save_best_solution()
        
        # Simulated annealing
        self.simulated_annealing(initial_temp=500, cooling_rate=0.99, min_temp=0.1)
        
        # Final local search
        self.restore_best_solution()
        self.local_search()
        self.save_best_solution()
        
        # Restore best
        self.restore_best_solution()

    def print_sol(self):
        print(self.N)
        for thesis in self.thesises:
            print(thesis.council, end=" ")
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

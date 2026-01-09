import random


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


class Individual:
    def __init__(self, N, M, K):
        self.thesis_assignment = [0] * N  # thesis i -> council
        self.teacher_assignment = [0] * M  # teacher j -> council
        self.fitness = -float('inf')


class GASolver:
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
        
        # Supervisor mapping:  thesis_id -> teacher_id (0-indexed)
        self.supervisor = [th.teacher. ID - 1 for th in thesises]
        
        # Precompute valid pairs
        self.precompute_compatibility()
        
        # Best solution
        self.best_individual = None

    def precompute_compatibility(self):
        """Precompute which theses/teachers can be together"""
        # thesis-thesis compatibility
        self.thesis_compatible = [[True] * self.N for _ in range(self.N)]
        for i in range(self.N):
            for j in range(i + 1, self.N):
                if self.s[i][j] < self.e: 
                    self.thesis_compatible[i][j] = False
                    self.thesis_compatible[j][i] = False
        
        # thesis-teacher compatibility
        self.thesis_teacher_compatible = [[True] * self.M for _ in range(self.N)]
        for i in range(self.N):
            for j in range(self.M):
                if self. g[i][j] < self. f or self.supervisor[i] == j:
                    self.thesis_teacher_compatible[i][j] = False

    def evaluate_fitness(self, ind):
        """Calculate fitness score"""
        score = 0
        
        # Build council contents
        council_theses = [[] for _ in range(self. K)]
        council_teachers = [[] for _ in range(self.K)]
        
        for i in range(self.N):
            c = ind.thesis_assignment[i] - 1
            if c >= 0:
                council_theses[c].append(i)
        
        for j in range(self.M):
            c = ind.teacher_assignment[j] - 1
            if c >= 0:
                council_teachers[c].append(j)
        
        # Calculate score
        for k in range(self.K):
            theses = council_theses[k]
            teachers = council_teachers[k]
            
            # Thesis-thesis similarity
            for i in range(len(theses)):
                for j in range(i + 1, len(theses)):
                    score += self.s[theses[i]][theses[j]]
            
            # Thesis-teacher similarity
            for th in theses:
                for te in teachers:
                    score += self.g[th][te]
        
        ind.fitness = score
        return score

    def is_valid(self, ind):
        """Check if individual satisfies all constraints"""
        council_theses = [[] for _ in range(self.K)]
        council_teachers = [[] for _ in range(self.K)]
        
        for i in range(self.N):
            c = ind.thesis_assignment[i] - 1
            if c < 0:
                return False
            council_theses[c].append(i)
        
        for j in range(self.M):
            c = ind.teacher_assignment[j] - 1
            if c < 0:
                return False
            council_teachers[c].append(j)
        
        for k in range(self.K):
            theses = council_theses[k]
            teachers = council_teachers[k]
            
            # Size constraints
            if len(theses) < self.a or len(theses) > self.b:
                return False
            if len(teachers) < self.c or len(teachers) > self.d:
                return False
            
            # Thesis-thesis compatibility
            for i in range(len(theses)):
                for j in range(i + 1, len(theses)):
                    if not self.thesis_compatible[theses[i]][theses[j]]:
                        return False
            
            # Thesis-teacher compatibility
            for th in theses: 
                for te in teachers: 
                    if not self.thesis_teacher_compatible[th][te]: 
                        return False
        
        return True

    def create_greedy_individual(self, randomize=False):
        """Create individual using greedy heuristic"""
        ind = Individual(self.N, self.M, self.K)
        
        # Reset councils
        for c in self.councils:
            c.thesises = []
            c. teachers = []
        
        # Assign teachers first
        teacher_order = list(range(self.M))
        if randomize:
            random.shuffle(teacher_order)
        else:
            teacher_order. sort(key=lambda j: -self.teachers[j].load)
        
        for j in teacher_order:
            teacher = self.teachers[j]
            best_council = -1
            best_score = -float('inf')
            
            candidates = list(range(self.K))
            if randomize:
                random.shuffle(candidates)
            
            for k in candidates:
                council = self.councils[k]
                if len(council.teachers) >= self. d:
                    continue
                
                valid = True
                for th in council.thesises:
                    if not self.thesis_teacher_compatible[th. ID - 1][j]:
                        valid = False
                        break
                
                if valid:
                    score = sum(self.g[th.ID - 1][j] for th in council.thesises)
                    balance = (self.c - len(council.teachers)) * 1000 if len(council.teachers) < self.c else 0
                    score += balance
                    
                    if score > best_score: 
                        best_score = score
                        best_council = k
            
            if best_council >= 0:
                ind.teacher_assignment[j] = best_council + 1
                self.councils[best_council].teachers.append(teacher)
        
        # Assign theses
        thesis_order = list(range(self.N))
        if randomize:
            random.shuffle(thesis_order)
        
        for i in thesis_order: 
            thesis = self.thesises[i]
            best_council = -1
            best_score = -float('inf')
            
            candidates = list(range(self.K))
            if randomize:
                random.shuffle(candidates)
            
            for k in candidates:
                council = self.councils[k]
                if len(council.thesises) >= self.b:
                    continue
                
                valid = True
                # Check thesis compatibility
                for th in council.thesises:
                    if not self.thesis_compatible[i][th.ID - 1]: 
                        valid = False
                        break
                
                # Check teacher compatibility
                if valid:
                    for te in council.teachers:
                        if not self.thesis_teacher_compatible[i][te.ID - 1]:
                            valid = False
                            break
                
                if valid:
                    score = sum(self.s[i][th.ID - 1] for th in council.thesises)
                    score += sum(self.g[i][te.ID - 1] for te in council.teachers)
                    balance = (self.a - len(council.thesises)) * 1000 if len(council.thesises) < self.a else 0
                    score += balance
                    
                    if score > best_score:
                        best_score = score
                        best_council = k
            
            if best_council >= 0:
                ind.thesis_assignment[i] = best_council + 1
                self.councils[best_council].thesises.append(thesis)
        
        self.evaluate_fitness(ind)
        return ind

    def crossover(self, parent1, parent2):
        """Uniform crossover with repair"""
        child = Individual(self.N, self.M, self.K)
        
        # Crossover thesis assignments
        for i in range(self.N):
            if random. random() < 0.5:
                child.thesis_assignment[i] = parent1.thesis_assignment[i]
            else: 
                child.thesis_assignment[i] = parent2.thesis_assignment[i]
        
        # Crossover teacher assignments
        for j in range(self.M):
            if random.random() < 0.5:
                child.teacher_assignment[j] = parent1.teacher_assignment[j]
            else:
                child.teacher_assignment[j] = parent2.teacher_assignment[j]
        
        # Repair if invalid
        self.repair(child)
        self.evaluate_fitness(child)
        return child

    def mutate(self, ind, mutation_rate=0.1):
        """Mutation:  randomly reassign some theses/teachers"""
        mutated = Individual(self.N, self.M, self.K)
        mutated.thesis_assignment = ind.thesis_assignment[:]
        mutated.teacher_assignment = ind.teacher_assignment[:]
        
        # Mutate thesis assignments
        for i in range(self.N):
            if random.random() < mutation_rate:
                mutated.thesis_assignment[i] = random. randint(1, self.K)
        
        # Mutate teacher assignments
        for j in range(self.M):
            if random.random() < mutation_rate:
                mutated.teacher_assignment[j] = random. randint(1, self.K)
        
        self.repair(mutated)
        self.evaluate_fitness(mutated)
        return mutated

    def repair(self, ind):
        """Repair invalid individual"""
        # Build council contents
        council_theses = [[] for _ in range(self.K)]
        council_teachers = [[] for _ in range(self.K)]
        
        for i in range(self. N):
            c = ind. thesis_assignment[i] - 1
            if 0 <= c < self.K:
                council_theses[c].append(i)
        
        for j in range(self.M):
            c = ind.teacher_assignment[j] - 1
            if 0 <= c < self.K: 
                council_teachers[c].append(j)
        
        # Fix teacher assignments first
        for j in range(self.M):
            c = ind.teacher_assignment[j] - 1
            if c < 0 or c >= self.K: 
                # Find valid council
                for k in range(self.K):
                    if len(council_teachers[k]) < self.d:
                        ind.teacher_assignment[j] = k + 1
                        council_teachers[k].append(j)
                        break
        
        # Fix thesis assignments
        for i in range(self.N):
            c = ind.thesis_assignment[i] - 1
            current_valid = True
            
            if c < 0 or c >= self.K:
                current_valid = False
            elif len(council_theses[c]) > self.b:
                current_valid = False
            else:
                # Check compatibility
                for th in council_theses[c]:
                    if th != i and not self.thesis_compatible[i][th]:
                        current_valid = False
                        break
                if current_valid:
                    for te in council_teachers[c]: 
                        if not self.thesis_teacher_compatible[i][te]:
                            current_valid = False
                            break
            
            if not current_valid:
                # Remove from current council
                if c >= 0 and i in council_theses[c]: 
                    council_theses[c].remove(i)
                
                # Find valid council
                best_k = -1
                best_score = -float('inf')
                
                for k in range(self.K):
                    if len(council_theses[k]) >= self.b:
                        continue
                    
                    valid = True
                    for th in council_theses[k]:
                        if not self.thesis_compatible[i][th]:
                            valid = False
                            break
                    
                    if valid:
                        for te in council_teachers[k]: 
                            if not self.thesis_teacher_compatible[i][te]:
                                valid = False
                                break
                    
                    if valid:
                        score = sum(self.s[i][th] for th in council_theses[k])
                        score += sum(self.g[i][te] for te in council_teachers[k])
                        if score > best_score:
                            best_score = score
                            best_k = k
                
                if best_k >= 0:
                    ind.thesis_assignment[i] = best_k + 1
                    council_theses[best_k]. append(i)
                else:
                    # Fallback: assign to least full council
                    best_k = min(range(self.K), key=lambda k: len(council_theses[k]))
                    ind. thesis_assignment[i] = best_k + 1
                    council_theses[best_k].append(i)

    def local_search(self, ind, max_iter=50):
        """Quick local search to improve individual"""
        improved = True
        iterations = 0
        
        while improved and iterations < max_iter: 
            improved = False
            iterations += 1
            
            # Try moving theses
            for i in range(self.N):
                current_k = ind.thesis_assignment[i] - 1
                current_score = self.get_thesis_contribution(ind, i, current_k)
                
                for k in range(self.K):
                    if k == current_k:
                        continue
                    
                    # Check if move is valid
                    if self.can_move_thesis(ind, i, k):
                        new_score = self.get_thesis_contribution_if_moved(ind, i, k)
                        if new_score > current_score:
                            ind.thesis_assignment[i] = k + 1
                            ind.fitness += (new_score - current_score)
                            improved = True
                            break

    def get_thesis_contribution(self, ind, thesis_idx, council_idx):
        """Get contribution of thesis to its current council"""
        score = 0
        for i in range(self.N):
            if i != thesis_idx and ind.thesis_assignment[i] == council_idx + 1:
                score += self.s[thesis_idx][i]
        for j in range(self.M):
            if ind.teacher_assignment[j] == council_idx + 1:
                score += self.g[thesis_idx][j]
        return score

    def get_thesis_contribution_if_moved(self, ind, thesis_idx, new_council):
        """Get contribution if thesis moved to new council"""
        score = 0
        for i in range(self.N):
            if i != thesis_idx and ind.thesis_assignment[i] == new_council + 1:
                score += self.s[thesis_idx][i]
        for j in range(self.M):
            if ind.teacher_assignment[j] == new_council + 1:
                score += self.g[thesis_idx][j]
        return score

    def can_move_thesis(self, ind, thesis_idx, new_council):
        """Check if thesis can be moved to new council"""
        # Count theses in new council
        count = sum(1 for i in range(self.N) if ind.thesis_assignment[i] == new_council + 1)
        if count >= self.b:
            return False
        
        # Check compatibility with other theses
        for i in range(self.N):
            if i != thesis_idx and ind. thesis_assignment[i] == new_council + 1:
                if not self.thesis_compatible[thesis_idx][i]:
                    return False
        
        # Check compatibility with teachers
        for j in range(self.M):
            if ind.teacher_assignment[j] == new_council + 1:
                if not self.thesis_teacher_compatible[thesis_idx][j]:
                    return False
        
        return True

    def tournament_select(self, population, tournament_size=3):
        """Tournament selection"""
        candidates = random.sample(population, min(tournament_size, len(population)))
        return max(candidates, key=lambda x:  x.fitness)

    def solve(self):
        """Main GA loop"""
        # Adaptive parameters based on problem size
        if self.N <= 10:
            pop_size = 20
            generations = 50
            mutation_rate = 0.15
            elite_size = 2
        elif self.N <= 100:
            pop_size = 30
            generations = 80
            mutation_rate = 0.1
            elite_size = 3
        else:
            pop_size = 40
            generations = 100
            mutation_rate = 0.08
            elite_size = 4
        
        # Initialize population
        population = []
        
        # Add greedy solutions with different orderings
        for seed in range(min(pop_size // 2, 10)):
            random.seed(seed * 42)
            ind = self.create_greedy_individual(randomize=(seed > 0))
            self.local_search(ind, max_iter=20)
            population.append(ind)
        
        # Fill rest with random greedy
        while len(population) < pop_size:
            ind = self.create_greedy_individual(randomize=True)
            population.append(ind)
        
        # Track best
        self.best_individual = max(population, key=lambda x: x. fitness)
        
        # Main loop
        for gen in range(generations):
            new_population = []
            
            # Elitism: keep best individuals
            population.sort(key=lambda x: -x.fitness)
            for i in range(elite_size):
                new_population.append(population[i])
            
            # Generate offspring
            while len(new_population) < pop_size:
                parent1 = self.tournament_select(population)
                parent2 = self. tournament_select(population)
                
                child = self.crossover(parent1, parent2)
                
                if random.random() < mutation_rate:
                    child = self.mutate(child, mutation_rate)
                
                # Apply local search occasionally
                if random.random() < 0.3:
                    self.local_search(child, max_iter=10)
                
                new_population.append(child)
            
            population = new_population
            
            # Update best
            current_best = max(population, key=lambda x: x.fitness)
            if current_best.fitness > self.best_individual.fitness:
                self.best_individual = current_best
        
        # Final local search on best
        self.local_search(self.best_individual, max_iter=100)
        
        return self. best_individual

    def print_solution(self):
        """Print the best solution"""
        print(self.N)
        print(" ".join(str(x) for x in self.best_individual.thesis_assignment))
        print(self.M)
        print(" ".join(str(x) for x in self.best_individual.teacher_assignment))


def main():
    thesises, teachers, councils, a, b, c, d, e, f, s, g = import_data()
    
    solver = GASolver(thesises, teachers, councils, a, b, c, d, e, f, s, g)
    solver.solve()
    solver.print_solution()


if __name__ == "__main__": 
    main()

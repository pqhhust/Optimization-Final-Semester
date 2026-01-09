#include <bits/stdc++.h>
using namespace std;

const int INF = 1e9;

struct Thesis {
    int ID;
    int teacher;  // index into teachers array
    int council;
    
    Thesis(int id) : ID(id), teacher(-1), council(0) {}
};

struct Teacher {
    int ID;
    int load;
    vector<int> thesises;  // 1-indexed thesis IDs
    int council;
    map<int, int> min_similarity;  // teacher index -> min similarity
    
    Teacher(int id) : ID(id), load(0), council(0) {}
};

struct Council {
    int ID;
    int load;
    vector<Thesis*> thesises;
    vector<Teacher*> teachers;
    
    Council(int id) : ID(id), load(0) {}
};

// Global data
int N, M, K;
int a, b, c, d, e, f;
vector<vector<int>> s, g;
vector<Thesis*> thesises;
vector<Teacher*> teachers;
vector<Council*> councils;

void import_data() {
    cin >> N >> M >> K;
    cin >> a >> b >> c >> d >> e >> f;
    
    thesises.resize(N);
    for (int i = 0; i < N; i++) {
        thesises[i] = new Thesis(i + 1);
    }
    
    teachers. resize(M);
    for (int i = 0; i < M; i++) {
        teachers[i] = new Teacher(i + 1);
    }
    
    councils.resize(K);
    for (int i = 0; i < K; i++) {
        councils[i] = new Council(i + 1);
    }
    
    s.resize(N, vector<int>(N));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cin >> s[i][j];
        }
    }
    
    g.resize(N, vector<int>(M));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            cin >> g[i][j];
        }
    }
    
    vector<int> t(N);
    for (int i = 0; i < N; i++) {
        cin >> t[i];
        thesises[i]->teacher = t[i] - 1;  // 0-indexed
        teachers[t[i] - 1]->load++;
        teachers[t[i] - 1]->thesises.push_back(i + 1);
    }
    
    // Compute min_similarity between teachers
    for (int t1 = 0; t1 < M; t1++) {
        for (int t2 = t1 + 1; t2 < M; t2++) {
            Teacher* teacher1 = teachers[t1];
            Teacher* teacher2 = teachers[t2];
            
            teacher1->min_similarity[t2] = INF;
            
            for (int i1 = 0; i1 < (int)teacher1->thesises.size(); i1++) {
                int s1 = teacher1->thesises[i1];
                for (int i2 = 0; i2 < (int)teacher2->thesises.size(); i2++) {
                    int s2 = teacher2->thesises[i2];
                    if (teacher1->min_similarity[t2] > s[s1 - 1][s2 - 1] && s1 != s2 && s[s1 - 1][s2 - 1] > 0) {
                        teacher1->min_similarity[t2] = s[s1 - 1][s2 - 1];
                    }
                }
            }
            
            teacher2->min_similarity[t1] = teacher1->min_similarity[t2];
        }
    }
}

class Solver {
public:
    vector<int> best_thesis;
    vector<int> best_teacher;
    int best_score;
    
    Solver() {
        best_thesis.resize(N, 0);
        best_teacher. resize(M, 0);
        best_score = -INF;
    }
    
    bool can_teacher_join(Teacher* teacher, Council* council) {
        if ((int)council->teachers.size() >= d) {
            return false;
        }
        for (Thesis* th : council->thesises) {
            if (g[th->ID - 1][teacher->ID - 1] < f) {
                return false;
            }
            if (th->teacher == teacher->ID - 1) {
                return false;
            }
        }
        for (Teacher* te : council->teachers) {
            int te_idx = te->ID - 1;
            int teacher_idx = teacher->ID - 1;
            int key = (te_idx < teacher_idx) ? te_idx : teacher_idx;
            int lookup = (te_idx < teacher_idx) ? teacher_idx : te_idx;
            
            auto it = teachers[key]->min_similarity.find(lookup);
            int min_sim = (it != teachers[key]->min_similarity.end()) ? it->second : INF;
            
            if (min_sim < e) {
                return false;
            }
        }
        return true;
    }
    
    bool can_thesis_join(Thesis* thesis, Council* council) {
        if ((int)council->thesises.size() >= b) {
            return false;
        }
        for (Thesis* th : council->thesises) {
            if (s[thesis->ID - 1][th->ID - 1] < e) {
                return false;
            }
        }
        for (Teacher* te : council->teachers) {
            if (te->ID - 1 == thesis->teacher) {
                return false;
            }
            if (g[thesis->ID - 1][te->ID - 1] < f) {
                return false;
            }
        }
        return true;
    }
    
    int thesis_score(Thesis* thesis, Council* council) {
        int score = 0;
        for (Thesis* th : council->thesises) {
            if (th->ID != thesis->ID) {
                score += s[thesis->ID - 1][th->ID - 1];
            }
        }
        for (Teacher* te : council->teachers) {
            score += g[thesis->ID - 1][te->ID - 1];
        }
        return score;
    }
    
    int teacher_score(Teacher* teacher, Council* council) {
        int score = 0;
        for (Thesis* th : council->thesises) {
            score += g[th->ID - 1][teacher->ID - 1];
        }
        return score;
    }
    
    int total_score() {
        int total = 0;
        for (Council* c : councils) {
            int n = c->thesises.size();
            for (int i = 0; i < n; i++) {
                Thesis* t1 = c->thesises[i];
                for (int j = i + 1; j < n; j++) {
                    Thesis* t2 = c->thesises[j];
                    total += s[t1->ID - 1][t2->ID - 1];
                }
                for (Teacher* te : c->teachers) {
                    total += g[t1->ID - 1][te->ID - 1];
                }
            }
        }
        return total;
    }
    
    void save_best() {
        int score = total_score();
        if (score > best_score) {
            best_score = score;
            for (int i = 0; i < N; i++) {
                best_thesis[i] = thesises[i]->council;
            }
            for (int i = 0; i < M; i++) {
                best_teacher[i] = teachers[i]->council;
            }
        }
    }
    
    void restore_best() {
        for (Council* c : councils) {
            c->thesises.clear();
            c->teachers.clear();
            c->load = 0;
        }
        for (int i = 0; i < N; i++) {
            thesises[i]->council = best_thesis[i];
            if (thesises[i]->council > 0) {
                councils[thesises[i]->council - 1]->thesises.push_back(thesises[i]);
            }
        }
        for (int i = 0; i < M; i++) {
            teachers[i]->council = best_teacher[i];
            if (teachers[i]->council > 0) {
                councils[teachers[i]->council - 1]->teachers.push_back(teachers[i]);
                councils[teachers[i]->council - 1]->load += teachers[i]->load;
            }
        }
    }
    
    void clear() {
        for (Council* c :  councils) {
            c->thesises.clear();
            c->teachers.clear();
            c->load = 0;
        }
        for (Thesis* th : thesises) {
            th->council = 0;
        }
        for (Teacher* te : teachers) {
            te->council = 0;
        }
    }
    
    void greedy_teachers(vector<Teacher*>& order) {
        for (Teacher* te : order) {
            int best_k = -1;
            int best_sc = -INF;
            for (int k = 0; k < K; k++) {
                Council* c = councils[k];
                if (can_teacher_join(te, c)) {
                    int score = teacher_score(te, c);
                    if ((int)c->teachers.size() < :: c) {
                        score += 10000;
                    }
                    if (score > best_sc) {
                        best_sc = score;
                        best_k = k;
                    }
                }
            }
            if (best_k >= 0) {
                te->council = best_k + 1;
                councils[best_k]->teachers.push_back(te);
                councils[best_k]->load += te->load;
            }
        }
    }
    
    void greedy_theses(vector<Thesis*>& order) {
        for (Thesis* th : order) {
            int best_k = -1;
            int best_sc = -INF;
            for (int k = 0; k < K; k++) {
                Council* c = councils[k];
                if (can_thesis_join(th, c)) {
                    int score = thesis_score(th, c);
                    if ((int)c->thesises.size() < a) {
                        score += 10000;
                    }
                    if (score > best_sc) {
                        best_sc = score;
                        best_k = k;
                    }
                }
            }
            if (best_k >= 0) {
                th->council = best_k + 1;
                councils[best_k]->thesises.push_back(th);
            }
        }
    }
    
    void remove_thesis(Council* c, Thesis* th) {
        auto it = find(c->thesises.begin(), c->thesises.end(), th);
        if (it != c->thesises.end()) {
            c->thesises.erase(it);
        }
    }
    
    void remove_teacher(Council* c, Teacher* te) {
        auto it = find(c->teachers.begin(), c->teachers.end(), te);
        if (it != c->teachers.end()) {
            c->teachers.erase(it);
        }
    }
    
    void local_search(int max_iter) {
        for (int iter = 0; iter < max_iter; iter++) {
            bool improved = false;
            
            // Move thesis
            for (Thesis* th : thesises) {
                if (th->council == 0) continue;
                Council* curr = councils[th->council - 1];
                if ((int)curr->thesises.size() <= a) continue;
                
                int curr_score = thesis_score(th, curr);
                remove_thesis(curr, th);
                
                int best_gain = 0;
                Council* best_c = nullptr;
                
                for (Council* c : councils) {
                    if (c->ID == th->council) continue;
                    if (can_thesis_join(th, c)) {
                        int gain = thesis_score(th, c) - curr_score;
                        if (gain > best_gain) {
                            best_gain = gain;
                            best_c = c;
                        }
                    }
                }
                
                if (best_c != nullptr) {
                    th->council = best_c->ID;
                    best_c->thesises.push_back(th);
                    improved = true;
                } else {
                    curr->thesises.push_back(th);
                }
            }
            
            // Swap theses
            for (int i = 0; i < N; i++) {
                Thesis* t1 = thesises[i];
                if (t1->council == 0) continue;
                
                for (int j = i + 1; j < N; j++) {
                    Thesis* t2 = thesises[j];
                    if (t2->council == 0 || t1->council == t2->council) continue;
                    
                    Council* c1 = councils[t1->council - 1];
                    Council* c2 = councils[t2->council - 1];
                    
                    int old_score = thesis_score(t1, c1) + thesis_score(t2, c2);
                    
                    remove_thesis(c1, t1);
                    remove_thesis(c2, t2);
                    
                    if (can_thesis_join(t1, c2) && can_thesis_join(t2, c1)) {
                        int new_score = thesis_score(t1, c2) + thesis_score(t2, c1);
                        if (new_score > old_score) {
                            int tmp = t1->council;
                            t1->council = t2->council;
                            t2->council = tmp;
                            c2->thesises.push_back(t1);
                            c1->thesises.push_back(t2);
                            improved = true;
                            continue;
                        }
                    }
                    
                    c1->thesises.push_back(t1);
                    c2->thesises.push_back(t2);
                }
            }
            
            // Move teacher
            for (Teacher* te :  teachers) {
                if (te->council == 0) continue;
                Council* curr = councils[te->council - 1];
                if ((int)curr->teachers.size() <= :: c) continue;
                
                int curr_score = teacher_score(te, curr);
                remove_teacher(curr, te);
                curr->load -= te->load;
                
                int best_gain = 0;
                Council* best_c = nullptr;
                
                for (Council* c : councils) {
                    if (c->ID == te->council) continue;
                    if (can_teacher_join(te, c)) {
                        int gain = teacher_score(te, c) - curr_score;
                        if (gain > best_gain) {
                            best_gain = gain;
                            best_c = c;
                        }
                    }
                }
                
                if (best_c != nullptr) {
                    te->council = best_c->ID;
                    best_c->teachers.push_back(te);
                    best_c->load += te->load;
                    improved = true;
                } else {
                    curr->teachers.push_back(te);
                    curr->load += te->load;
                }
            }
            
            if (!improved) break;
        }
    }
    
    vector<vector<Teacher*>> get_teacher_orders() {
        vector<vector<Teacher*>> orders;
        
        // By load descending
        vector<Teacher*> order1 = teachers;
        sort(order1.begin(), order1.end(), [](Teacher* a, Teacher* b) {
            return a->load > b->load;
        });
        orders.push_back(order1);
        
        // By load ascending
        vector<Teacher*> order2 = teachers;
        sort(order2.begin(), order2.end(), [](Teacher* a, Teacher* b) {
            return a->load < b->load;
        });
        orders.push_back(order2);
        
        // By total similarity descending
        vector<Teacher*> order3 = teachers;
        sort(order3.begin(), order3.end(), [](Teacher* a, Teacher* b) {
            int sum_a = 0, sum_b = 0;
            for (int i = 0; i < N; i++) {
                sum_a += g[i][a->ID - 1];
                sum_b += g[i][b->ID - 1];
            }
            return sum_a > sum_b;
        });
        orders.push_back(order3);
        
        // By ID ascending
        vector<Teacher*> order4 = teachers;
        sort(order4.begin(), order4.end(), [](Teacher* a, Teacher* b) {
            return a->ID < b->ID;
        });
        orders.push_back(order4);
        
        // By ID descending
        vector<Teacher*> order5 = teachers;
        sort(order5.begin(), order5.end(), [](Teacher* a, Teacher* b) {
            return a->ID > b->ID;
        });
        orders.push_back(order5);
        
        // Random orderings
        for (int seed = 0; seed < 3; seed++) {
            vector<Teacher*> order = teachers;
            srand(seed * 42);
            random_shuffle(order.begin(), order.end());
            orders.push_back(order);
        }
        
        return orders;
    }
    
    vector<vector<Thesis*>> get_thesis_orders() {
        vector<vector<Thesis*>> orders;
        
        // By teacher load descending
        vector<Thesis*> order1 = thesises;
        sort(order1.begin(), order1.end(), [](Thesis* a, Thesis* b) {
            return teachers[a->teacher]->load > teachers[b->teacher]->load;
        });
        orders.push_back(order1);
        
        // By teacher load ascending
        vector<Thesis*> order2 = thesises;
        sort(order2.begin(), order2.end(), [](Thesis* a, Thesis* b) {
            return teachers[a->teacher]->load < teachers[b->teacher]->load;
        });
        orders.push_back(order2);
        
        // By total similarity descending
        vector<Thesis*> order3 = thesises;
        sort(order3.begin(), order3.end(), [](Thesis* a, Thesis* b) {
            int sum_a = 0, sum_b = 0;
            for (int j = 0; j < N; j++) {
                sum_a += s[a->ID - 1][j];
                sum_b += s[b->ID - 1][j];
            }
            return sum_a > sum_b;
        });
        orders.push_back(order3);
        
        // By ID ascending
        vector<Thesis*> order4 = thesises;
        sort(order4.begin(), order4.end(), [](Thesis* a, Thesis* b) {
            return a->ID < b->ID;
        });
        orders.push_back(order4);
        
        // By ID descending
        vector<Thesis*> order5 = thesises;
        sort(order5.begin(), order5.end(), [](Thesis* a, Thesis* b) {
            return a->ID > b->ID;
        });
        orders.push_back(order5);
        
        // Random orderings
        for (int seed = 0; seed < 3; seed++) {
            vector<Thesis*> order = thesises;
            srand(seed * 42 + 7);
            random_shuffle(order.begin(), order.end());
            orders.push_back(order);
        }
        
        return orders;
    }
    
    void solve() {
        vector<vector<Teacher*>> teacher_orders = get_teacher_orders();
        vector<vector<Thesis*>> thesis_orders = get_thesis_orders();
        
        int max_t_orders, max_th_orders;
        max_t_orders = 5;
        max_th_orders = 5;
        
        for (int t_idx = 0; t_idx < max_t_orders; t_idx++) {
            clear();
            greedy_teachers(teacher_orders[t_idx]);
            
            for (int th_idx = 0; th_idx < max_th_orders; th_idx++) {
                // Clear theses only
                for (Council* c : councils) {
                    c->thesises.clear();
                }
                for (Thesis* th : thesises) {
                    th->council = 0;
                }
                
                greedy_theses(thesis_orders[th_idx]);
                local_search(50);
                save_best();
            }
        }
        
        restore_best();
    }
    
    void print_sol() {
        cout << N << "\n";
        for (int i = 0; i < N; i++) {
            cout << thesises[i]->council;
            if (i < N - 1) cout << " ";
        }
        cout << "\n";
        
        cout << M << "\n";
        for (int i = 0; i < M; i++) {
            cout << teachers[i]->council;
            if (i < M - 1) cout << " ";
        }
        cout << "\n";
    }
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    import_data();
    
    Solver sol;
    sol.solve();
    sol.print_sol();
    
    return 0;
}

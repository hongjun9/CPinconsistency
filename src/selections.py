import setting
import random

def random_selection(candidate_individuals, N):
    new_individuals_index = []
    new_individuals = []
    for i in range(N):
        index = random.randint(0, len(candidate_individuals)-1)
        while index in new_individuals_index:
            index = random.randint(0, len(candidate_individuals)-1)
        new_individuals_index.append(index)
        new_individuals.append(candidate_individuals[index])

    return new_individuals



def tournament_selection(individuals, pool, tour):
    # input: sorted individuals with the first rank
    # output: new_individuals with the size of pool

    #pool: size of mating pool
    #tour: tournament size
    rank_index = setting.INDEX_RANK
    score_index = setting.INDEX_CPIRANK 
    parent = []
    N = len(individuals)
    print "pool:",str(pool)
    print "tour:",str(tour)
    for i in range(pool):
        candidate = [None]*tour
        # pick #tour(=2) random candidates    
        for j in range(tour):           
            new_index = random.randint(0, N-1)
            while new_index in candidate or new_index in parent:
                new_index = random.randint(0, N-1)
            candidate[j] = new_index  #0 to N-1
        print "tournament candidate:", candidate

        # find min (high rank)   the smaller number of rank, the higher rank
        best = candidate[0]
        for i in range(1,tour):
            if individuals[best][rank_index] > individuals[candidate[i]][rank_index]:       # rank
                best = candidate[i]
            elif individuals[best][rank_index] == individuals[i][rank_index] \
                    and individuals[best][score_index] > individuals[candidate[i]][score_index]:    # cpi_score
                best = candidate[i]
            
            #if individuals[best][score_index] > individuals[candidate[i]][score_index]:    # cpi_score
            #    best = candidate[i]
            #elif individuals[best][score_index] == individuals[i][score_index] \
            #        and individuals[best][rank_index] < individuals[candidate[i]][rank_index]:       # rank
            #    best = candidate[i]

        parent.append(best)

    new_individuals = []
    for i in range(pool):
        new_individuals.append(individuals[parent[i]])

    return new_individuals


def top_n_selection(candidate_individuals, N):

    #@@@ opt3
    if setting.SCORE_OPTION == 3:
        return random_selection(candidate_individuals, N)

    max_rank = max([row[setting.INDEX_RANK] for row in candidate_individuals])   # num of pareto fronts
    allocated = 0           # num of selected
    new_individuals = []
    for i in range(max_rank+1):
        num_current_pareto = [row[setting.INDEX_RANK] for row in candidate_individuals].count(i)
        if allocated + num_current_pareto <= N:
            new_individuals += candidate_individuals[allocated:allocated+num_current_pareto]
            allocated += num_current_pareto
        else:
            temp = candidate_individuals[allocated:allocated+num_current_pareto]
            temp = sorted(temp, key=lambda temp: temp[setting.INDEX_CPIRANK]) 
            available = N - allocated 
            new_individuals += temp[0:available]
            allocated += available

        if allocated == N:
            break;
    
    return new_individuals



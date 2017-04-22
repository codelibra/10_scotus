
from sklearn.neighbors import NearestNeighbors
neigh = NearestNeighbors(n_neighbors=10)
neigh.fit(tf_idf)



neighs = neigh.kneighbors(tf_idf[128], 10, return_distance=False)



neighs = neighs[0]



similar_cases = data.filter_by(neighs, 'id')['filename']



similar_cases



joined = pd.read_csv('sc_lc.csv')



joined


# # Case similarity approach
# ### Algorithms
# 1. Using tf-idf and 10 nearest neighbour search
# 2. Using cosine similarity
#
# ### Steps
# 1. Genearate tf-idf/word vector data for circuit court bloomberg text.
# 2. Map circuit court data to scbd data ie., use only those circuit court texts which were appealed in supreme court.
# 3. Train model based on Nearest neighbour model.
# 4. Predict for all cases.
# 5. Evaluate outcome
#
# ### Evaluation
# 1. Predict for all scbd cases
# 2. Since cases are justice centred, each docket will appear 8-9 times (ie., number of judges). Since *case_outcome_disposition* is same for all, use any of them.
# 3. Take majority vote of 10 nearest neighbour, and take that as predicted output.
# 4. accuracy = number of correct predictoins / total number of cases


def print_case_outcomes_for_file(file):
    # NOTE: -2 is used since the files were in .p format 2 is length of ".p"
    # If extension changes we need to change this .2
    if len(joined[joined['caseid']==file[:-2]]['case_outcome_disposition'].values) > 0:
        return joined[joined['caseid']==file[:-2]]['case_outcome_disposition'].values[0]
    else:
        print "File not found "+file
        return -1



def get_compare_case_outcomes(cases):
    d = []
    affirm = 0
    reverse = 0
    outcome = 0
    for idx,case in enumerate(cases):
        case_outcome = print_case_outcomes_for_file(case)
        if case_outcome == -1:
            continue
        d.append({'file': case, 'outcome': case_outcome})
        if case_outcome == 1:
            affirm = affirm + 1
        else:
            reverse = reverse + 1

    if affirm>reverse:
        outcome = 1
    else:
        outcome = 0
    return d,outcome



def get_overall_score_tf_idf():
    correct = 0
    incorrect = 0
    num = tf_idf.shape[0]
    nearest_neighbour_data = {}
    for idx in range(1,num):
        print idx
        neighs = neigh.kneighbors(tf_idf[idx], 10, return_distance=False)[0]
        similar_cases = data.filter_by(neighs, 'id')['filename']
        df,outcome = get_compare_case_outcomes(similar_cases)
        query_file = data[data['id']==idx]['filename'] [0]
        actual_outcome = print_case_outcomes_for_file(query_file)

        if actual_outcome == outcome:
            correct = correct + 1
        else:
            incorrect = incorrect + 1

        nearest_neighbour_data[idx] = {'query_file': query_file,
                                       'similar_cases': similar_cases,
                                       'similar_case_outcomes' : df,
                                       'correct':correct,
                                       'incorrect':incorrect
                                      }

    return correct, incorrect, nearest_neighbour_data



def get_overall_score_cosine_similarity():
    def getKey(item):
        return item[0]

    correct = 0
    incorrect = 0
    num = tf_idf.shape[0]
    nearest_neighbour_data = {}
    for idx in range(1,num):
        similarity = cosine_similarity(tf_idf[idx:idx+1], tf_idf)[0]
        indices = range(1,num)
        tuples = zip(similarity,indices)
        tuples = sorted(tuples,reverse=True,key=getKey)

        neighs = list()
        for key,val in tuples[0:10]:
            neighs.append(val)

        similar_cases = data.filter_by(neighs, 'id')['filename']
        df,outcome = get_compare_case_outcomes(similar_cases)
        if outcome == -1:
            continue
        query_file = data[data['id']==idx]['filename'] [0]
        actual_outcome = print_case_outcomes_for_file(query_file)

        if actual_outcome == outcome:
            correct = correct + 1
        else:
            incorrect = incorrect + 1

        nearest_neighbour_data[idx] = {'query_file': query_file,
                                       'similar_cases': similar_cases,
                                       'similar_case_outcomes' : df,
                                       'correct':correct,
                                       'incorrect':incorrect
                                      }

    return correct, incorrect, nearest_neighbour_data



# Some files are not found, could not download all files post 1975
overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_tf_idf()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)


# ### Tf-idf model current accuracy


accuracy



# Some files are not found, could not download all files post 1975
overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_cosine_similarity()


# #### Cosine similarity model current accuracy





accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)



accuracy



nearest_neighbour_data = pd.DataFrame(nearest_neighbour_data)



nearest_neighbour_data.transpose()







f = pd.read_csv('sc_lc_link.csv')



f
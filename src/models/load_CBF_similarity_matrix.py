import numpy as np


def load_CBF_similarity_matrix():
    sim_cosinus_CBF = np.loadtxt("./data/sim_cos_CBF_16")

    return sim_cosinus_CBF
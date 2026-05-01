import numpy as np
from scripts.algorithms.linucb import LinUCB

linucb_model = None


def init_model(n_features):
    global linucb_model
    linucb_model = LinUCB(n_features=n_features, alpha=1.0)
    print("✅ RL Model Ready")


def rank_roles_with_rl(user, roles, context_builder):
    global linucb_model

    if linucb_model is None:
        print("⚠️ RL not initialized, fallback")
        return roles

    context_vectors = [context_builder(user, r) for r in roles]
    scores = linucb_model.predict(context_vectors)

    ranked = sorted(zip(roles, scores), key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked]


def update_model(context_vector, reward):
    global linucb_model
    if linucb_model:
        linucb_model.update(context_vector, reward)
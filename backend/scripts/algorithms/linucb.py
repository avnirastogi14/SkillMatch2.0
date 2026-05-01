import numpy as np

class LinUCB:
    def __init__(self, n_features: int, alpha: float = 1.0):
        """
        n_features: dimension of context vector
        alpha: exploration parameter
        """
        self.n_features = n_features
        self.alpha = alpha

        # A = D x D identity matrix
        self.A = np.identity(n_features)
        self.b = np.zeros((n_features, 1))

    def get_theta(self):
        """Compute parameter vector θ"""
        A_inv = np.linalg.inv(self.A)
        theta = A_inv @ self.b
        return theta, A_inv

    def predict(self, context_vectors):
        """
        context_vectors: list of np.array (D x 1)
        returns: scores for each action
        """
        theta, A_inv = self.get_theta()

        scores = []
        for x in context_vectors:
            x = x.reshape(-1, 1)
            exploit = float(theta.T @ x)
            explore = self.alpha * np.sqrt(float(x.T @ A_inv @ x))
            score = exploit + explore
            scores.append(score)

        return scores

    def update(self, x, reward: float):
        """
        x: context vector (D,)
        reward: scalar
        """
        x = x.reshape(-1, 1)
        self.A += x @ x.T
        self.b += reward * x
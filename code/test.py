from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

a1 = np.arange(5).reshape(1,5)
a2 = np.arange(20).reshape(4,5)
print(cosine_similarity(a1, a2))

print(cosine_similarity(a2, a1))
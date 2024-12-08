import numpy as np
import os
from gensim.models import KeyedVectors


def load_glove_model() -> KeyedVectors:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    file_path = os.path.join(project_root, "ml-models", "glove.6B.100d.txt")
    print("Loading GloVe model...")
    glove_model = KeyedVectors.load_word2vec_format(file_path, binary=False, no_header=True)
    print(f"GloVe model loaded with {len(glove_model)} words.")
    return glove_model


# iterates sentences, splits them in words, looks for vector representation of that word in the model, brings them
# together, averaging
def compute_embedding(text: str, model: KeyedVectors) -> np.ndarray:
    words = text.split()
    embeddings = [model[word] for word in words if word in model]
    if embeddings:
        vector = np.mean(embeddings, axis=0)
        assert vector.shape[0] == model.vector_size
        return vector
    return np.zeros(model.vector_size)

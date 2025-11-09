from sentence_transformers import SentenceTransformer
#SentenceTransformer: This is the main class from the sentence-transformers library, 
# which provides easy-to-use models for converting text into dense vector embeddings 
# (numerical representations that capture semantic meaning).
import numpy as np

_model = None

def get_embedder(model_name="all-MiniLM-L6-v2"):
    #all-MiniLM-L6-v2 is a model that creates 384-dimensional embeddings.
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model

def embed_texts(texts):
    #texts is a list of string(s)
    """Return list of vectors (numpy arrays) for a list of texts."""
    model = get_embedder()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # ensure float32 for chroma
    return [vec.astype(np.float32) for vec in embeddings]
#Why float32? This is specifically for Chroma DB (a vector database), which requires float32 format for optimal storage and similarity search performance
#Returns: A list of NumPy arrays, where each array is a 384-dimensional vector for the corresponding input text
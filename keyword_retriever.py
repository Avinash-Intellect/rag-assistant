from rank_bm25 import BM25Okapi


class KeywordRetriever:

    def __init__(self, chunks):
        self.chunks = chunks
        self.texts = [chunk["text"] for chunk in chunks]
        self.tokenized_corpus = [text.split() for text in self.texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def retrieve(self, query, top_k=3):
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        top_indices = ranked_indices[:top_k]

        return [self.chunks[i] for i in top_indices]

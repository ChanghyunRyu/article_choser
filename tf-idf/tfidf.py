from sklearn.feature_extraction.text import TfidfVectorizer

tfidf_vectorizer = TfidfVectorizer(min_df=1)


def calculate_matrix(sentences):
    tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
    return tfidf_matrix


def calculate_similarity(matrix):
    doc_similarities = (matrix * matrix.T)
    temp = doc_similarities.toarray()[0]
    doc_similarities = []
    for i in range(len(temp)):
        if i == 0:
            continue
        doc_similarities.append((i, temp[i]))
    sort_similarities = sorted(doc_similarities, key=lambda doc: doc[1], reverse=True)
    similarity_index = []
    for i in range(5):
        similarity_index.append(sort_similarities[i])
    return similarity_index


def get_similarity(results):
    titles = []
    for result in results:
        titles.append(result['title'])
    matrix = calculate_matrix(titles)
    return calculate_similarity(matrix)

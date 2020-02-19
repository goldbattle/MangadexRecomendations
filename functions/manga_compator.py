from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def load_corpus_into_tfidf(corpus):
    # build a TF/IDF matrix for each paper
    # https://markhneedham.com/blog/2016/07/27/scitkit-learn-tfidf-and-cosine-similarity-for-computer-science-papers/
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english')
    return tf.fit_transform([content for file, content in corpus])


def find_similar_tfidf(tfidf_matrix, corpus_index):
    # top similar papers based on cosine similarity
    cosine_similarities = linear_kernel(tfidf_matrix[corpus_index:corpus_index + 1], tfidf_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != corpus_index]

    # return the matches (best matches to worst)
    tuple_vec = [(index, cosine_similarities[index]) for index in related_docs_indices]

    # convert to dictionary
    scores = {}
    for id1, score in tuple_vec:
        scores[id1] = score
    return scores


def find_similar_labels(manga1, labels_vec, manga_data):
    # Get the labels for the manga we want to match to
    manga1_labels = manga1.compute_xor_label_vector(labels_vec)
    count_manga1_labels = 0
    for label in manga1_labels:
        if label:
            count_manga1_labels += 1

    # return if we don't have anything to match to
    dic_matches = {}
    if count_manga1_labels < 1:
        return dic_matches

    # Lets loop through each
    for idx, manga2 in enumerate(manga_data):

        # skip if the same id
        if manga1.id == manga2.id:
            continue

        # get labels
        manga2_labels = manga2.compute_xor_label_vector(labels_vec)
        count_manga2_labels = 0
        for label in manga2_labels:
            if label:
                count_manga2_labels += 1

        # count the number of same labels between the two
        count_same = 0
        for idlc, val in enumerate(manga1_labels):
            if manga1_labels[idlc] and manga2_labels[idlc]:
                count_same += 1

        # skip if we don't have any that are the same
        if count_same < 1:
            continue

        # append the score for this manga matched to the other
        # the best it can be is 1 if they have the exact same mangas
        # we use the max number of labels since only if the both have the same count it should score 1
        dic_matches[idx] = float(count_same) / max(count_manga1_labels, count_manga2_labels)

    # return the matches (sort based on the score)
    return dic_matches

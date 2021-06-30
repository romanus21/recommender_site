import pandas as pd
from django_pandas.io import read_frame
from sklearn.metrics.pairwise import linear_kernel

from .models import Movie


def get_recommendations(title):
    movies = Movie.objects.all()
    metadata = read_frame(movies)

    from sklearn.feature_extraction.text import TfidfVectorizer

    tfidf = TfidfVectorizer(stop_words='english')

    metadata['overview'] = metadata['overview'].fillna('')

    tfidf_matrix = tfidf.fit_transform(metadata['overview'])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    indices = pd.Series(metadata.index,
                        index=metadata['title']).drop_duplicates()
    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:6]

    movie_indices = [i[0] for i in sim_scores]

    return movie_indices

import math

from mymdb.settings import FILMS_ON_PAGE, NUMBER_OF_LOOKING


def dist_cosine(vec_A, vec_B):
    def dot_product(vec_A, vec_B):
        d = 0.0
        for dim in vec_A:
            if dim in vec_B:
                d += vec_A[dim] * vec_B[dim]
        return d

    return dot_product(vec_A, vec_B) / math.sqrt(
        dot_product(vec_A, vec_A)) / math.sqrt(dot_product(vec_B, vec_B))


def make_recommendation(user_ID, user_rates):
    def __get_mark(tup: tuple):
        return tup[1]

    matches = []
    cur_user_rs = dict(
        list(user_rates.filter(user_id=user_ID).values_list('movie_id',
                                                            'rating')))
    users = [q[0] for q in user_rates.values_list('user_id').distinct()]
    for user in users:
        if user == user_ID:
            continue
        user_rs = dict(
            list(user_rates.filter(user_id=user).values_list('movie_id',
                                                             'rating')))
        matches.append(
            (
                user,
                dist_cosine(cur_user_rs, user_rs)
            )
        )

    best_matches = sorted(matches, key=__get_mark, reverse=True)[
                   :NUMBER_OF_LOOKING]

    sim = dict()

    sim_all = sum([x[1] for x in best_matches])

    best_matches = dict([x for x in best_matches if x[1] > 0.0])

    user_films = [x[0] for x in list(user_rates.filter(user_id=user_ID).values_list(
        'movie_id').distinct())]

    for related_user in best_matches:
        products = user_rates.filter(user_id=related_user).values_list(
            'movie_id', 'rating')
        for product in products:
            if product[0] not in user_films:
                if product[0] not in sim:
                    sim[product[0]] = 0.0
                sim[product[0]] += product[1] * \
                                   best_matches[related_user]
    for product in sim:
        sim[product] /= sim_all
    best_products = sorted(sim.items(), key=__get_mark, reverse=True)[
                    :FILMS_ON_PAGE]
    return [x[0] for x in best_products]

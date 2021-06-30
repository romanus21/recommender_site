from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from mymdb.settings import FILMS_ON_PAGE
from .content_based_rec import get_recommendations
from .forms import UserForm
from .models import Movie, Rating
from .user_based_rec import make_recommendation


def recommend(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_active:
        raise Http404

    current_user_id = request.user.id
    user_rates = Rating.objects.all()
    id_list = make_recommendation(user_ID=current_user_id,
                                  user_rates=user_rates)
    movie_list = list(
        Movie.objects.filter(id__in=id_list))
    return render(request, 'web/recommend.html', {'movie_list': movie_list})


def index(request):
    movies = Movie.objects.all()
    query = request.GET.get('q')
    if query == 'None':
        query = None
    if query:
        movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
    paginator = Paginator(movies, FILMS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'web/list.html', {'page': page, 'q': query})


def rated_movies(request):
    movies = Movie.objects.filter(rating__user=request.user)
    query = request.GET.get('q')
    if query == 'None':
        query = None
    if query:
        movies = movies.filter(Q(title__icontains=query)).distinct()
    paginator = Paginator(movies, FILMS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'web/user_list.html', {'page': page, 'q': query})


def detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    movie = get_object_or_404(Movie, id=movie_id)
    id_list = get_recommendations(movie.title)
    rec_movies = list(
        Movie.objects.filter(id__in=id_list))
    if request.method == "POST":
        if not Rating.objects.filter(user=request.user, movie=movie).exists():
            rating_object = Rating()
            rating_object.user = request.user
            rating_object.movie = movie
        else:
            rating_object = get_object_or_404(Rating, movie=movie,
                                              user=request.user)
        rate = request.POST['rating']
        rating_object.rating = rate
        rating_object.save()
        messages.success(request, "Your Rating is submitted")
        return redirect('detail', movie_id=movie.id)
    if Rating.objects.filter(user=request.user, movie=movie).exists():
        rating = get_object_or_404(Rating, movie=movie,
                                   user=request.user).rating
    else:
        rating = 0
    return render(request, 'web/detail.html',
                  {'movie': movie, 'rating': rating, 'rec_movies': rec_movies})


def signUp(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
    context = {
        'form': form
    }
    return render(request, 'web/signUp.html', context)


def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
            else:
                return render(request, 'web/login.html',
                              {'error_message': 'Your account disable'})
        else:
            return render(request, 'web/login.html',
                          {'error_message': 'Invalid Login'})
    return render(request, 'web/login.html')


def Logout(request):
    logout(request)
    return redirect("login")

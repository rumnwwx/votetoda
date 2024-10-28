from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Choice, UserVote
from django.db.models import Sum
from django.utils import timezone


def vote(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.is_expired():
        return redirect('expired_page')  # Редирект если пост устарел

    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        if UserVote.objects.filter(user=request.user, post=post).exists():
            return render(request, 'vote_page.html', {'post': post, 'error': "Вы уже голосовали!"})

        choice = get_object_or_404(Choice, id=choice_id, post=post)
        choice.votes += 1
        choice.save()
        UserVote.objects.create(user=request.user, post=post, choice=choice)

        return redirect('results', post_id=post_id)

    return render(request, 'vote_page.html', {'post': post})


def results(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    total_votes = post.choices.aggregate(Sum('votes'))['votes__sum'] or 1  # Защита от деления на 0
    choices_percentage = [
        (choice.text, (choice.votes / total_votes) * 100) for choice in post.choices.all()
    ]
    return render(request, 'results.html', {'post': post, 'choices_percentage': choices_percentage})


def index(request):
    return render(request, 'myapp/index.html')


def register(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('index')
    else:
        user_form = RegisterForm()
        profile_form = ProfileForm()
    return render(request, 'myapp/register.html', {'user_form': user_form, 'profile_form': profile_form})

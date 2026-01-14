from django.shortcuts import render

#def home(request):
 #   return render(request, "my_blog/home.html")
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView, CreateView
from .models import Post, Category, Comment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db import models
from django.urls import reverse_lazy
from .forms import PostForm
from django.contrib.auth.models import User
from django.http import JsonResponse
#pour les serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from .serializers import PostSerializer

class HomeView(ListView):
    model = Post
    template_name = 'my_blog/home.html'
    context_object_name = 'posts'
    ordering = ['-pub_date']
    paginate_by = 6  # optionnel

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoute les catégories avec leurs posts (préféré prefetch pour perf)
        context['categories'] = Category.objects.all().prefetch_related('posts')
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'my_blog/post_detail.html'  # on crée ce fichier après
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Bonus : on incrémente les vues à chaque visite
        post = self.object
        post.views += 1
        post.save(update_fields=['views'])
        context['comments'] = post.comments.filter(is_approved=True).order_by('-created_at')
        return context


@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)

    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('message')

    if name and email and message:
        Comment.objects.create(
            post=post,
            name=name,
            email=email,
            message=message,
            is_approved=True  # approuvé auto en dev
        )

    return redirect('post_detail', slug=slug)


@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    post.likes += 1
    post.save(update_fields=['likes'])

    # Renvoie le HTML du bouton like avec le nouveau compteur
    return render(request, 'my_blog/partials/like_button.html', {
        'post': post
    })


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'my_blog/dashboard.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Tes articles
        context['my_posts'] = Post.objects.filter(author=user).order_by('-pub_date')

        # Stats
        posts = context['my_posts']
        context['total_posts'] = posts.count()
        context['total_views'] = posts.aggregate(total=models.Sum('views'))['total'] or 0
        context['total_likes'] = posts.aggregate(total=models.Sum('likes'))['total'] or 0

        # Total commentaires reçus (tous tes posts)
        total_comments = 0
        for post in posts:
            total_comments += post.comments.count()
        context['total_comments'] = total_comments

        return context

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'my_blog/post_form.html'  # on crée ce template après
    fields = ['title', 'content', 'conclusion', 'category', 'image', 'is_published']
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'my_blog/post_confirm_delete.html'  # on crée ce template après
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'my_blog/post_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']  # on peut ajouter 'username' si tu veux le modifier
    template_name = 'my_blog/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user  # l'utilisateur connecté

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.filter(author=self.request.user).count()
        return context


    #creation d'un serializers
class PostListAPIView(generics.ListCreateAPIView):  # ← on change ListAPIView en ListCreateAPIView
    queryset = Post.objects.filter(is_published=True).order_by('-pub_date')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # ← lecture publique, création réservée aux connectés

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # ← associe automatiquement l’auteur à l’
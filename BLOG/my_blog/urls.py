from django.urls import path
from . import views
from .views import HomeView, PostDetailView, DashboardView, add_comment, like_post, PostDeleteView, PostUpdateView, PostCreateView, ProfileView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/comment/', add_comment, name='add_comment'),
    path('post/<slug:slug>/like/', like_post, name='like_post'),
    #path("", views.home, name="home"),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
# Édition et suppression
    path('post/<slug:slug>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),



]

from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    UserListCreate, UserDetail, 
    PostListCreate, PostDetail, PostLikeToggle, 
    CommentListCreate, CommentDetail, GoogleLoginCallbackApi, GoogleLoginRedirectApi,
    NewsFeedAPIView
)
from . import views
urlpatterns = [
    # User Endpoints
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'), 

    # Post Endpoints
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),  
    path('posts/<int:pk>/like/', PostLikeToggle.as_view(), name='post-like-toggle'), 

    # Comment Endpoints
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'), 

    # Google Authentication
    path('api/v1/auth/google/', GoogleLoginRedirectApi.as_view(), name='google_login'),
    path('accounts/google/login/callback/', GoogleLoginCallbackApi.as_view(), name='google_login_callback'),

    # News Feed
    path('newsfeed/', NewsFeedAPIView.as_view(), name='news-feed'),

    # Token Authentication
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    
    path("logout", views.logout_view)
]

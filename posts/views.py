from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.generics import get_object_or_404
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import redirect
from urllib.parse import urlencode
import requests
from rest_framework.permissions import AllowAny
from django.shortcuts import render, redirect
from django.contrib.auth import logout

User = get_user_model()

def home(request):
    render(request, "home.html")

def logout_view(request):
    logout(request)
    return redirect("posts/")

# User List & Create API
class UserListCreate(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serialized_users = []

        for user in users:
            user_data = UserSerializer(user).data
            try:
                token = Token.objects.get(user=user)  
                user_data["token"] = token.key
            except Token.DoesNotExist:
                user_data["token"] = None  

            serialized_users.append(user_data)

        return Response(serialized_users)


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Detail API (Supports GET, PUT, PATCH, DELETE)
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'  



# Post List & Create API
class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 


# Post Detail, Update, Delete API
class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

# Like & Unlike Post API
class PostLikeToggle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):  
        post = get_object_or_404(Post, id=pk)  
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"message": "Like removed."}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)
            return Response({"message": "Post liked."}, status=status.HTTP_201_CREATED)

# Comment List & Create API
class CommentListCreate(generics.ListCreateAPIView):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 


# Comment Detail, Update, Delete API
class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

# Personalized News Feed
class NewsFeedAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.order_by('-created_at')[:10]
    

class GoogleLoginRedirectApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        google_auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        params = {
            'response_type': 'code',
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI, 
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'select_account'
        }
        authorization_url = f"{google_auth_url}?{urlencode(params)}"
        return redirect(authorization_url)


import requests

class GoogleLoginCallbackApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Google redirects here with a GET request containing 'code'.
        Instead of failing, we should extract 'code' and exchange it for tokens.
        """
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Missing authorization code"}, status=status.HTTP_400_BAD_REQUEST)

        return self.exchange_code_for_token(code)

    def post(self, request, *args, **kwargs):
        """
        If testing with Postman, users can send 'code' via POST.
        """
        code = request.data.get("code")
        if not code:
            return Response({"error": "Missing authorization code"}, status=status.HTTP_400_BAD_REQUEST)

        return self.exchange_code_for_token(code)

    def exchange_code_for_token(self, code):
        """
        Helper function to exchange 'code' for Google access tokens.
        """
        google_token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH2_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        response = requests.post(google_token_url, data=data)
        token_data = response.json()

        if "id_token" not in token_data:
            return Response({"error": "Failed to exchange code", "details": token_data}, status=status.HTTP_400_BAD_REQUEST)

        # Decode and verify id_token
        id_token = token_data["id_token"]
        google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        google_response = requests.get(google_verify_url)

        if google_response.status_code != 200:
            return Response({"error": "Invalid ID token"}, status=status.HTTP_400_BAD_REQUEST)

        google_data = google_response.json()

        return Response({
            "message": "Google Login Successful",
            "google_data": google_data,
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token")
        }, status=status.HTTP_200_OK)

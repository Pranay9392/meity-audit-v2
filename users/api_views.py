# Project: meity_audit_portal
# App: users
# File: users/api_views.py
# Description: API views for user registration and retrieving current user details.

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import CustomUserSerializer
from .models import CustomUser

class RegisterUserAPIView(generics.CreateAPIView):
    """
    API view for user registration.
    Allows creation of new CustomUser instances.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserDetailAPIView(APIView):
    """
    API view to retrieve details of the currently authenticated user.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


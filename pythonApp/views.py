from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from django.db.models import Q, Sum, F, DecimalField, Subquery, OuterRef
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from pythonApp import serializers
from pythonApp.models import UserAccount
from pythonApp.serializers import UserAccountSerializer

User = get_user_model()

# Create your views here.


class SuperUserRegistrationView(UserViewSet):
    # Override get_permissions method to allow unauthenticated access only for create_superuser action
    def get_permissions(self):
        if self.action == "create_superuser":
            return [AllowAny()]
        return super().get_permissions()

    @action(["post"], detail=False, url_path="superuser")
    def create_superuser(self, request, *args, **kwargs):
        serializer = serializers.UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the user object using serializer.save()
        user = serializer.save(user_type='admin')  # Set the user_type to 'admin'

        if user:
            # Set user as a superuser and staff
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()

            return Response({"error": False, "message": "Admin account created and activated successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAccountUpdateView(generics.UpdateAPIView):
    serializer_class = UserAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = self.request.user

        if user_id:
            # If a user_id is provided, check if the user is an admin
            if user.is_staff:
                # Admin can edit name and phone of other users
                return get_object_or_404(User, id=user_id)

        # If no user_id or if the user is not an admin, allow users to update their own accounts
        return user

    def perform_update(self, serializer):
        user = self.request.user

        if user.is_staff:
            # Admins can update the name and phone without email uniqueness check
            serializer.save()
        else:
            # Regular users can update all fields, including email, with email uniqueness check
            email = serializer.validated_data.get('email')
            instance = serializer.instance

            if email and User.objects.exclude(pk=instance.pk).filter(email=email).exists():
                raise serializers.ValidationError("User with this email already exists.")

            serializer.save()


class UserAccountDeleteView(generics.DestroyAPIView):
    serializer_class = UserAccountSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    queryset = UserAccount.objects.all()  # Update with the correct queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # You can add additional logic here if needed

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


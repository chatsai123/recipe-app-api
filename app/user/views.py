from rest_framework import generics

from user.serializers import UserSerializer


class CreateuserView(generics.CreateAPIView):
    """Create a new use in the system"""
    serializer_class = UserSerializer

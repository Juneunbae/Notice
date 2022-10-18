from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Post, Comment
from users.models import Profile
from .permissions import CustomReadOnly
from .serializers import PostCreateSerializer, PostSerializer, CommentSerializer, CommentCreateSerializer

# Create your views here.
class CommentViewSet(viewsets.ModelViewSet) :
    queryset = Comment.objects.all()
    permission_classes = [CustomReadOnly]

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve' :
            return CommentSerializer
        return CommentCreateSerializer

    def perform_create(self, serializer) :
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(author=self.request.user, profile=profile)

class CommentViewSet(viewsets.ModelViewSet) :
    queryset = Comment.objects.all()
    permission_classes = [CustomReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve' :
            return CommentSerializer
        return CommentCreateSerializer
    
    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(author=self.request.user, profile=profile)

class PostViewSet(viewsets.ModelViewSet) :
    queryset = Post.objects.all()
    permission_classes = [CustomReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'likes']

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve' :
            return PostSerializer
        return PostCreateSerializer

    def perform_create(self, serializer) :
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(author=self.request.user, profile=profile)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def like_post(request, pk) :
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all() :
        post.likes.remove(request.user)
        messages = {
            'Delete' : '좋아요 삭제'
        }
        return Response(messages, {'status' : 'ok'})
    else :
        post.likes.add(request.user)
        messages = {
            'Add' : '좋아요'
        }
        return Response(messages, {'status' : 'ok'})
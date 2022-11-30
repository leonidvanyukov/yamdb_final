from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          OwnerAdminModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleCreateSerializer, TitleSerializer,
                          TokenSerializer, UserSerializer)

User = get_user_model()


class TitleViewSet(viewsets.ModelViewSet):
    """
    Админ может менять категории.
    Остальные могут только читать.

    titles/ - возвращает все категории
    titles/{id}/ - возвращает конкретную категорию
    """
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('rating')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Админ и модератор могут менять отзывы.
    Пользователь может менять только свои отзывы.

    /titles/{title_id}/reviews/ - возвращает все отзывы
    /titles/{title_id}/reviews/{id}/ - возвращает конкретный отзыв
    """
    serializer_class = ReviewSerializer
    permission_classes = (OwnerAdminModeratorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Админ и модератор могут менять комментарии.
    Пользователь может менять только свои комментарии.

    /titles/{title_id}/reviews/{review_id}/comments/
    Возвращает все комментарии по конкретному отзыву
    /titles/{title_id}/reviews/{review_id}/comments/{id}/
    возвращает конкретный комментарий
    """
    serializer_class = CommentSerializer
    permission_classes = (OwnerAdminModeratorOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(ListCreateDestroyViewSet):
    """
    Админ может менять жанры, а остальные только смотреть.

    /genres/ - возвращает все жанры
    /genres/{id}/ - возвращает конкретный жанр
    /genres/{slug}/ - удаляет жанр по slug
    /genres/?search=name - ищет жанр по названию
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    Админ может менять категории, а остальные только смотреть.

    /categories/ - возвращает все категории
    /categories/{id}/ - возвращает категории по id
    /categories/{slug}/ - удаляет категорию по slug
    /genres/?search=name - ищет категорию по имени
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class UserViewSet(viewsets.ModelViewSet):
    """
    /users/ - возвращает всех пользователей
    /users/{username}/ - изменение юзера по username
    /users/?search=username - поиск пользователя по username
    /users/me/ - показывает ваш профиль
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        if kwargs['partial']:
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def get_instance(self):
        return self.request.user

    @action(
        methods=["get", "patch", "delete"],
        detail=False, url_path='me', url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        subject='Confirmation code',
        message=confirmation_code,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False
    )
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomTokenViewBase(GenericAPIView):
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )

import logging

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as dj_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PageLimitPagination
from api.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly)
from api.serializers import (
    IngredientSerializer, RecipeCreateSerializer,
    RecipeSerializer, ShortRecipeSerializer,
    TagSerializer, UserWithRecipesSerializer
)
from recipes.models import (
    FavoriteRecipe, Ingredient, Recipe,
    RecipeIngredient, RecipeInShoppingCart,
    Subscription, Tag
)

User = get_user_model()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserViewSet(dj_views.UserViewSet):
    pagination_class = PageLimitPagination
    pagination_class.page_size = 6

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(subscribers__user=request.user)
        pages = self.paginate_queryset(subscriptions)
        context = {'request': request}
        serializer = UserWithRecipesSerializer(
            pages,
            many=True,
            context=context
        )
        return self.get_paginated_response(serializer.data)

    @staticmethod
    def create_relation_author_with_user(model, author, user, request):
        try:
            instance = model.objects.create(author=author, user=user)
        except Exception as ex:
            logger.debug(f'Ошибка: {ex}')
            return Response(status=status.HTTP_400_BAD_REQUEST)
        context = {'request': request}
        serializer = UserWithRecipesSerializer(
            instance.author,
            context=context
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_relation_author_with_user(model, author, user, request):
        try:
            instance = model.objects.get(author=author, user=user)
        except Exception as ex:
            logger.debug(f'Ошибка: {ex}')
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            return self.create_relation_author_with_user(
                Subscription,
                author,
                request.user,
                request,
            )
        if request.method == 'DELETE':
            return self.delete_relation_author_with_user(
                Subscription,
                author,
                request.user,
                request,
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = PageLimitPagination
    pagination_class.page_size = 6
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        actions = ['create', 'update', 'partial_update']
        if self.action in actions:
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__recipeinshoppingcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total=Sum('amount')
        ).order_by()

        output = ''
        for recipe_ingredient in recipe_ingredients:
            output += (
                f'{recipe_ingredient["ingredient__name"]}'
                f'({recipe_ingredient["ingredient__measurement_unit"]}) — '
                f'{recipe_ingredient["total"]}\n'
            )

        file_name = 'foodgram_shopping_cart'
        response = HttpResponse(output, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{file_name}.txt"'
        )
        return response

    @staticmethod
    def create_relation_recipe_with_user(model, recipe, user, request):
        try:
            instance = model.objects.create(recipe=recipe, user=user)
        except Exception as ex:
            logger.error(f'Ошибка: {ex}')
            return Response(status=status.HTTP_400_BAD_REQUEST)
        context = {'request': request}
        serializer = ShortRecipeSerializer(instance.recipe, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_relation_recipe_with_user(model, recipe, user, request):
        try:
            instance = model.objects.get(recipe=recipe, user=user)
        except Exception as ex:
            logger.error(f'Ошибка: {ex}')
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.create_relation_recipe_with_user(
                RecipeInShoppingCart, recipe, request.user, request
            )
        if request.method == 'DELETE':
            return self.delete_relation_recipe_with_user(
                RecipeInShoppingCart, recipe, request.user, request
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.create_relation_recipe_with_user(
                FavoriteRecipe, recipe, request.user, request
            )
        if request.method == 'DELETE':
            return self.delete_relation_recipe_with_user(
                FavoriteRecipe, recipe, request.user, request
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter]
    search_fields = ['^name']

from django.contrib import admin
from django.db.models import Count

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, RecipeInShoppingCart, Tag
                            )


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug', 'usage_count']

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).annotate(
            usage_count=Count('recipe')
        )

    def usage_count(self, obj):
        return obj.usage_count

    usage_count.short_description = 'Использований'
    usage_count.admin_order_field = 'usage_count'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit', 'usage_count']

    search_fields = ['name']

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).annotate(
            usage_count=Count('recipe')
        )

    def usage_count(self, obj):
        return obj.usage_count

    usage_count.short_description = 'Использований'
    usage_count.admin_order_field = 'usage_count'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class RecipeInShoppingCartInline(admin.TabularInline):
    model = RecipeInShoppingCart
    extra = 1


class FavoriteRecipeInline(admin.TabularInline):
    model = FavoriteRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author',
        'cooking_time',
        'ingredient_count',
        'favorite_count',
        'shopping_cart_count',
    ]

    search_fields = [
        'name',
        'author__username',
        'author__first_name',
        'author__last_name',
        'author__email',
    ]

    inlines = [
        RecipeIngredientInline,
        RecipeInShoppingCartInline,
        FavoriteRecipeInline,
    ]

    def get_queryset(self, *args, **kwargs):
        return (
            super().get_queryset(*args, **kwargs)
            .annotate(
                ingredient_count=Count('recipeingredient')
            )
            .annotate(
                shopping_cart_count=Count('recipeinshoppingcart')
            )
            .annotate(
                favorite_count=Count('favoriterecipe')
            )
        )

    def ingredient_count(self, obj):
        return obj.ingredient_count

    ingredient_count.short_description = 'Ингредиентов'
    ingredient_count.admin_order_field = 'ingredient_count'

    def shopping_cart_count(self, obj):
        return obj.shopping_cart_count

    shopping_cart_count.short_description = 'В корзине'
    shopping_cart_count.admin_order_field = 'shopping_cart_count'

    def favorite_count(self, obj):
        return obj.favorite_count

    favorite_count.short_description = 'В избранном'
    favorite_count.admin_order_field = 'favorite_count'


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)

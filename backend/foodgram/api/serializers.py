from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscribe, Tag, TagRecipe)
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для тегов с валидацией hex цвета'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = '__all__',

    def validate_color(self, color):
        '''Проверка введенного цвета'''
        color = str(color)[1:]
        if len(color) not in (3, 6):
            raise ValidationError(f'Недопустимая длина цвета {color}.')
        return f'#{color}'


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингредиентов'''
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientAmountSerializer(serializers.ModelSerializer):
    '''Сериализатор количества ингредиентов'''
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователей.'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        read_only_fields = ('is_subscribed',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        '''Создание, проверка и установка пароля пользователя.'''
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        '''
        Проверка подписки на конкретного пользователя.
        В зависимости от её результата возвращает True или False.
        '''
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if user == obj:
            return False
        queryset = Subscribe.objects.filter(user=user)
        if not queryset:
            return False
        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={'request': self.context.get('request')}
        )
        for subscribing in serializer.data:
            if subscribing.get('username') == obj.username:
                return True
            return False


class PasswordSerializer(serializers.Serializer):
    '''Сериализатор смены пароля пользователя.'''
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, current_password):
        '''Проверка пароля из базы на допустимую длину.'''
        if len(current_password) > 150:
            raise ValidationError('Недопустимая длина пароля.')
        return current_password

    def validate_new_password(self, new_password):
        '''Проверка введённого пароля на допустимую длину.'''
        if len(new_password) > 150:
            raise ValidationError('Недопустимая длина нового пароля.')
        return new_password


class AddIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор добавления ингредиента.'''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    '''Сериализатор для отображения рецептов'''
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        '''Получение количества ингредиентов из модели IngredientAmount.'''
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        '''Получение рецепта(obj) и проверка того, что он в Избранном.'''
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        queryset = Favorite.objects.filter(user=user)
        if not queryset:
            return False
        serializer = FavoriteSerializer(
            queryset,
            many=True,
            context={'request': self.context.get('request')}
        )
        for favorites in serializer.data:
            if favorites.get('name') == obj.name:
                return True
            return False

    def get_is_in_shopping_cart(self, obj):
        '''Получение рецепта(obj) и проверка того,
        что он в Корзине покупок.
        '''
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        queryset = ShoppingCart.objects.filter(user=user)
        if not queryset:
            return False
        serializer = ShoppingCartSerializer(
            queryset,
            many=True,
            context={'request': self.context.get('request')}
        )
        for shopping_cart in serializer.data:
            if shopping_cart.get('name') == obj.name:
                return True
            return False


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор создания и обновления рецептов с помощью PATCH.'''

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        read_only=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'tags',
            'author',
            'image',
            'ingredients',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        '''При успешном создании рецепта
        возвращает данные в представлении RecipeListSerializer.'''
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        tagrecipe_list = []
        for tag in tags:
            tagrecipe = TagRecipe(tag=tag, recipe=recipe)
            tagrecipe_list.append(tagrecipe)
        recipe.tag_recipe.bulk_create(tagrecipe_list)

        ingredients_data = []
        for ingredient in ingredients:
            one_ingredient = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_result = IngredientAmount(
                ingredients=one_ingredient,
                amount=amount,
                recipe=recipe
            )
            ingredients_data.append(ingredient_result)
        recipe.ingredient.bulk_create(ingredients_data)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.cooking_time = validated_data.get(
            'cooking_time',
            recipe.cooking_time
        )

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                IngredientAmount.objects.get_or_create(
                    recipe=recipe,
                    ingredients=ingredient['id'],
                    amount=ingredient['amount']
                )
        recipe.save()
        return recipe


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка покупок
    """
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(
            instance.recipe, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(
            instance.recipe, context=context).data


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return UserSubscribeSerializer(instance.author, context=context).data

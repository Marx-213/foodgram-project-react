from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe
from users.models import User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('author', 'name', 'text', 'image',
                  'ingredients', 'tags', 'cooking_time')
        model = Recipe


class UserSerializer(serializers.ModelSerializer):
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
        extra_kwargs = {
            'password': {'write_only': True},
        }
        read_only_fields = ('is_subscribed',)

    def create(self, validated_data):
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
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.is_subscribed.filter(id=obj.id).exists()


class PasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


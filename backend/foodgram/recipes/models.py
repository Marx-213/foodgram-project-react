from django.contrib.auth import get_user_model
from django.db import models

from .config import HEX_COLORS, MEASURMENTS_UNITS

User = get_user_model()


class Tag(models.Model):
    '''Модель для тегов.'''
    name = models.CharField(
        'Название тега',
        max_length=50,
        unique=True,
        blank=False,
        help_text='Укажите название тега'
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
        default='#ffffff',
        unique=True,
        blank=False,
        choices=HEX_COLORS,
        help_text='Выберите цвет',
    )
    slug = models.SlugField(
        'Слаг тега',
        unique=True,
        blank=False,
        help_text='Придумайте slug для тега',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модель для ингредиентов.'''
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        blank=False,
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=50,
        blank=False,
        choices=MEASURMENTS_UNITS,
        help_text='Выберите единицу измерения',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique ingredient'
            )
        ]

    def __str__(self):
        return self.name
    


class Recipe(models.Model):
    '''Модель для рецептов.'''
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        unique=True,
        help_text='Напишите название вашего рецепта.'
    )
    text = models.TextField(
        'Описание блюда',
        help_text='Введите описание блюда'
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='recipe_images/',
        help_text='Загрузите фотографию блюда',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        help_text='Выберите ингредиенты',
        related_name='recipes',
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
       Tag,
       verbose_name='Тег',
       through='TagRecipe',
       related_name='recipes',
       help_text='Выберите теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления(в минутах)',
        help_text='Укажите время приготовления блюда',
        default=1
    )
    is_favorited = models.ManyToManyField(
        User,
        verbose_name='Понравившиеся рецепты',
        related_name='favorites',
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        verbose_name='Список покупок',
        related_name='shopping_carts',
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name='Название тега',
        on_delete=models.CASCADE,
        related_name='tag_recipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
        related_name='tag_recipe',
    )

    class Meta:
        verbose_name = 'Теги и рецепт'
        verbose_name_plural = 'Теги и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_tag_recipe'
            )
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        default=1
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('ingredients', 'recipe',),
                name='unique_ingredient_amount',
            ),
        )

    def __str__(self) -> str:
        return f'{self.ingredients} {self.amount}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='carts'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self) -> str:
        return f'{self.recipe} в корзине у {self.user}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='user_favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='user_favorites'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'{self.recipe} в Избранном у {self.user}'
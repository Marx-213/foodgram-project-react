from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=50,
        unique=True,
        null=False,
        help_text='Укажите название тега'
    )
    color = models.CharField(
        max_length=7,
        default='#ffffff',
        verbose_name='Цветовой HEX-код',
        unique=True,
        null=True,
        help_text='Выберите цвет',
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
        help_text='Придумайте slug для тега',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов."""
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
        help_text='Выберите единицу измерения',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
    


class Recipe(models.Model):
    """Модель для рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        unique=True,
        help_text='Напишите название вашего рецепта.'
    )
    text = models.TextField('Текст', help_text='Введите описание рецепта')
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/',
        help_text='Загрузите фотографию блюда',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(
       Tag,
       verbose_name='Тег',
       help_text='Выберите теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        help_text='Укажите время приготовления блюда',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
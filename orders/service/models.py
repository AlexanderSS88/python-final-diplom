from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy
from django_rest_passwordreset.tokens import get_token_generator



STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
    )



USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель')
    )



"""Миксин для управления пользователями"""
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with
        the given username, email, and password."""
        if not email:
            raise ValueError('The given email must be set')
        if not password:
            raise ValueError('The given password must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)



"""Стандартная модель пользователя"""
class User(AbstractUser):
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(gettext_lazy('email address'), unique=True)
    username_validator = UnicodeUsernameValidator()
    discount_factor = models.IntegerField(default=100)
    type = models.CharField(
        verbose_name='Тип пользователя',
        choices=USER_TYPE_CHOICES,
        max_length=5,
        default='buyer'
        )
    username = models.CharField(
        gettext_lazy('username'),
        max_length=150,
        help_text=gettext_lazy('Required. 150 characters or fewer. '
                    'Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': gettext_lazy(
                "A user with that username already exists."
            ),
            },
            )
    is_active = models.BooleanField(
        gettext_lazy('active'),
        default=False,
        help_text=gettext_lazy(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
        )
    second_name = models.CharField(
        verbose_name='Отчество',
        null=True,
        max_length=40,
        blank=True,
        default=None
        )
    company = models.CharField(
        verbose_name='Компания',
        null=True,
        max_length=40,
        blank=True
        )
    position = models.CharField(
        verbose_name='Должность',
        null=True,
        max_length=40,
        blank=True
        )

    def __str__(self):
        if self.second_name is None:
            return f'{self.last_name} {self.first_name}'
        else:
            return f'{self.last_name} {self.first_name} {self.second_name}'
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)



class Shop(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название магазина'
        )
    distance = models.PositiveIntegerField()
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    filename = models.CharField(max_length=100, null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        blank=True,
        null=True,
        on_delete=models.CASCADE
        )
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name



class Category(models.Model):
    id = models.PositiveIntegerField(
        primary_key=True,
        unique=True,
        verbose_name='ID'
        )
    # category_id = models.PositiveIntegerField()
    name = models.CharField(
        max_length=50,
        verbose_name='Название категории'
        )
    shops = models.ManyToManyField(
        Shop,
        verbose_name='Магазины',
        related_name='categories',
        blank=True)
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название продукта'
        )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='products',
        blank=True,
        on_delete=models.CASCADE
        )
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name



class ProductInfo(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ключ'
    )
    model = models.CharField(
        max_length=100,
        verbose_name='Модель'
        )
    shop = models.ForeignKey(
        Shop,
        verbose_name='Магазин',
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
        )
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(
        verbose_name='Рекомендуемая розничная цена'
        )

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'shop', 'external_id'],
                name='unique_product_info'
                ),
            ]



class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = "Список названий параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name



class ProductParameter(models.Model):
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
        )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name='Параметр',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
        )
    value = models.CharField(
        verbose_name='Значение',
        max_length=100,
        blank=True
        )

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(
                fields=['product_info', 'parameter'],
                name='unique_product_parameter'
                ),
            ]



class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        related_name='orders',
        on_delete=models.CASCADE
        )
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        verbose_name='Статус',
        choices=STATE_CHOICES,
        max_length=50
        )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказ"
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)
    # @property
    # def sum(self):
    #     return self.ordered_items.aggregate(total=Sum("quantity"))["total"]



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='ordered_items',
        on_delete=models.CASCADE
        )
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='ordered_items',
        on_delete=models.CASCADE
        )
    shop = models.ForeignKey(
        Shop,
        verbose_name='Магазин',
        related_name='ordered_items',
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество'
        )

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product_info', 'shop'],
                name='unique_order_item'
                ),
            ]



class UsersContactPhone(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        related_name='contactphone',
        on_delete=models.CASCADE
        )
    value = models.CharField(
        verbose_name='Значение',
        max_length=100
        )

    class Meta:
        verbose_name = 'Телефон пользователя'
        verbose_name_plural = "Список телефонов пользователей"

    def __str__(self):
        return f'{self.value}'



class UsersContactAdress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        related_name='contactadress',
        on_delete=models.CASCADE
        )
    city = models.CharField(
        max_length=50,
        verbose_name='Город'
        )
    street = models.CharField(
        max_length=100,
        verbose_name='Улица'
        )
    house = models.CharField(
        max_length=15,
        verbose_name='Дом',
        )
    structure = models.CharField(
        max_length=15,
        verbose_name='Корпус',
        blank=True
        )
    building = models.CharField(
        max_length=15,
        verbose_name='Строение',
        blank=True
        )
    apartment = models.CharField(
        max_length=15,
        verbose_name='Квартира',
        blank=True
        )

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'



class ConfirmEmailToken(models.Model):

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=gettext_lazy(
            "The User which is associated to this password reset token"
            )
        )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=gettext_lazy("When was this token generated")
        )
    key = models.CharField(
        gettext_lazy("Key"),
        max_length=64,
        db_index=True,
        unique=True
        )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(
            user=self.user
            )


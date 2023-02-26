import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from service.models import Order, OrderItem, User, Product, Shop, Category, ProductInfo, Parameter, ProductParameter, \
    UsersContactPhone, UsersContactAdress


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user_admin():
    return User.objects.create_user('admin')

@pytest.fixture
def user():
    return User.objects.create_user(first_name='Viktor',
                                    last_name='Dyatlov',
                                    email='qwerty99@mail.de',
                                    password='gdfShi88$kjgr',
                                    password_rep='gdfShi88$kjgr'
                                    )

@pytest.fixture
def user_shop():
    return User.objects.create_user(first_name='Jack',
                                    last_name='Frolov',
                                    email='ytrewq919@mail.ua',
                                    password='u7gdfShi88$kjgr',
                                    password_rep='u7gdfShi88$kjgr',
                                    type='shop'
                                    )


@pytest.mark.django_db
def test_update_shop_products(client, user_shop):
    # Arrange
    count_shop = Shop.objects.count()
    count_products = Product.objects.count()
    # Act
    response = client.post(f'update_catalog',
                           data={'user': user_shop.id,
                                 'url': "https://github.com/netology-code/"
                                        "python-final-diplom/blob/master/"
                                        "data/shop1.yaml"
                                 }
                           )
    # Assert
    assert response.status_code == 201
    assert Shop.objects.count() == count_shop + 1
    assert Product.objects.count() == count_products + 4


@pytest.mark.django_db
def test_login_pos1(client, user):
    # Arrange
    # Act
    response = client.post(f'user/login',
                           data={'email': 'qwerty99@mail.de',
                                 'password': 'gdfShi88$kjgr'
                                 }
                           )
    # Assert
    assert response.status_code == 201


@pytest.mark.django_db
def test_register_pos2(client):
    # Arrange
    count = User.objects.count()
    # Act
    response = client.post(f'user/register', data={'first_name': 'Viktor',
                                                'last_name': 'Dyatlov',
                                                'email': 'qwerty99@mail.de',
                                                'password':'gdfShi88$kjgr',
                                                'password_rep':'gdfShi88$kjgr'
                                                }
                           )
    # Assert
    assert response.status_code == 201
    assert User.objects.count() == count + 1


@pytest.mark.django_db
def test_get_all_products_pos3(client, user, user_shop):
    # Arrange
    response = client.post(f'update_catalog',
                           data={'user': user_shop.id,
                                 'url': "https://github.com/netology-code/"
                                        "python-final-diplom/blob/master/"
                                        "data/shop1.yaml"
                                 }
                           )
    count_products = Product.objects.count()
    # Act
    response = client.get(f'user/products',
                          data={'user': user.id}
                          )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == count_products


@pytest.mark.django_db
def test_get_product_info_pos4(client, user, user_shop):
    # Arrange
    response = client.post(f'update_catalog',
                           data={'user': user_shop.id,
                                 'url': "https://github.com/netology-code/"
                                        "python-final-diplom/blob/master/"
                                        "data/shop1.yaml"
                                 }
                           )
    # Act
    response = client.get(f'user/products/1',
                          data={'user': user.id}
                          )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data[0]['left_module'][0] == 'Смартфон Apple iPhone XS Max 512GB (золотистый)'
    assert data[0]['rigth_module'][0] == 'Связной'


@pytest.mark.django_db
def test_get_basket_pos5(client, user, user_shop):
    # Arrange
    response = client.post(f'update_catalog',
                           data={'user': user_shop.id,
                                 'url': "https://github.com/netology-code/"
                                        "python-final-diplom/blob/master/"
                                        "data/shop1.yaml"
                                 }
                           )
    new_order = Order.objects.create(user=user.id,
                                     status='basket'
                                     )
    OrderItem.objects.create(order=new_order.id,
                             product_info=ProductInfo.objects.get(id=1),
                             shop=Shop.objects.get(user=user_shop.id),
                             quantity=3,
                             )
    # Act
    response = client.get(f'user/basket',
                          data={'user': user.id}
                          )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data[0]['Список товаров: '][0].name == 'Смартфон Apple iPhone XS Max 512GB (золотистый)'
    assert data[0]['Итог: ']['Сумма: '] > 110100
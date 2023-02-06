from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum, F
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, get_object_or_404
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from endpoints.serializers import UserSerializer, ProductSerializer, \
    ProductInfoSerializer, OrderSerializer, UsrAdressSerializer
from service.models import Product, ProductInfo, Order, \
    UsersContactPhone, UsersContactAdress, User



"""1. Вход покупателей. Авторизация."""
class LoginAccount(APIView):

    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(
                request,
                username=request.data['email'],
                password=request.data['password']
                )
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Status': True,
                                         'Token': token.key
                                         })
            return JsonResponse(
                {'Status': False,
                 'Errors': 'Не удалось авторизовать'}
                )
        return JsonResponse(
            {'Status': False,
             'Errors': 'Не указаны необходимые аргументы'}
            )



"""2. Регистрация покупателей"""
class RegisterAccount(APIView):

    def post(self, request, *args, **kwargs):
        # проверка обязательных аргументов
        if {'first_name',
            'last_name',
            'email',
            'password',
            'password_rep',
            }.issubset(request.data):
            if request.data['password'] == request.data['password_rep']:
                # проверяем пароль на сложность
                try:
                    validate_password(request.data['password'])
                except Exception as password_error:
                    error_array = []
                    for item in password_error:
                        error_array.append(item)
                    return JsonResponse(
                        {'Status': False,
                         'Errors': {'password': error_array}
                         }
                        )
                else:
                    # проверяем данные для уникальности имени пользователя
                    request.data._mutable = True
                    request.data.update({})
                    user_serializer = UserSerializer(data=request.data)
                    if user_serializer.is_valid():
                        # сохраняем пользователя
                        user = user_serializer.save()
                        user.set_password(request.data['password'])
                        user.save()
                        return JsonResponse({'Status': True})
                    else:
                        return JsonResponse({'Status': False,
                                             'Errors': user_serializer.errors
                                             })
            else:
                return JsonResponse({'Status': False,
                                     'Errors': 'Пароли не совпадают'}
                                    )
        return JsonResponse({'Status': False,
                             'Errors': 'Не указаны необходимые аргументы'
                             })



"""3. Список товаров"""
class ProductListView(ListAPIView):
    queryset = Product.objects.order_by('category__name', 'name')
    serializer_class = ProductSerializer



"""4. Карточка товара"""
class ProductDetailView(APIView):
    def get(self, request, *args, **kwargs):
        if {'shop_id'}.issubset(request.query_params):
            product = get_object_or_404(Product.objects.all(), pk=args).select_related('category__name')
            ser_product = ProductSerializer(product)
            left_module = json.dumps({'Наименование: ': ser_product.data['name'],
                                     'Описание: ': ser_product.data['category__name']})

            needed_product = ProductInfo.objects.all().filter(product=product.id,
                                                              shop=request.query_params.get('shop_id'),
                                                                 ).select_related('shop__name').first()
            ser_needed_product = ProductInfoSerializer(needed_product)
            rigth_module = json.dumps({'Поставщик: ': ser_needed_product.data['shop__name'],
                                       'Характеристики: ': ser_needed_product.data['product_parameters'],
                                       'Цена: ': ser_needed_product.data['price'],
                                       'Количество: ': ser_needed_product.data['quantity'],
                                       'В корзину': '',
                                       })
        else:
            return JsonResponse({'Status': False,
                                 'Errors': 'Отсутствует выбор магазина'}
                                )

        return JsonResponse({'left_module': left_module,
                             'rigth_module: ': rigth_module
                             })



"""5. Корзина"""
class BasketView(APIView):

    def delivery(self, request, *args, **kwargs):
        base_delivery = 500
        discount = User.objects.flilter(user=request.user.id).get('discount_factor')
        quantity = Order.objects.filter(
            user=request.user.id,
            status='basket').get('ordered_items__quantity')
        distan = Order.objects.filter(
            user=request.user.id,
            status='basket').get('ordered_items__shop__distance')
        if distan <= 50:
            cost_delivery = base_delivery/100*discount
        elif (distan > 50) and (distan <= 300):
            cost_delivery = distan/11*discount
        else:
            cost_delivery = distan/10.5*discount
        cost_delivery=cost_delivery*quantity*0.4
        return cost_delivery

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'Status': False, 'Error': 'Log in required'},
                status=403
                )
        basket = (Order.objects.filter(
            user=request.user.id,
            status='basket'
            ).select_related(
                'ordered_items__product_info__product__name',
                'ordered_items__shop',
                'ordered_items__shop__product_infos__price'
                'ordered_items__quantity'
                ).annotate(
                    total_price=Sum(F(
                        'ordered_items__quantity') * F('ordered_items__shop__product_infos__price')
                                    ))).exclude('id',
                                                'user',
                                                'dt',
                                                'status',
                                                'cost_delivery',
                                                'order_price',
                                                'final_price',
                                                'adress_cont',
                                                'phone_cont'
                                                ).distinct()
        posit_list = OrderSerializer(basket, many=True)

        total_list = basket.objects.annotate(
            order_price=Sum('total_price'),
            cost_delivery=self.delivery(),
            final_price='cost_delivery'+'final_price'
            )

        ser_total_list = OrderSerializer(total_list)
        total = json.dumps({
            'Сумма: ': ser_total_list.data['order_price'],
            'Стоимость доставки: ': ser_total_list.data['cost_delivery'],
            'Итог: ': ser_total_list.data['final_price']
            })

        return JsonResponse({'Список товаров: ': posit_list.data,
                             'Итог: ': total})



"""6. Подтверждение заказа."""
class AcceptOrder(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False,
                                 'Error': 'Log in required'},
                                status=403
                                )

        if {'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = UsersContactPhone(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse({'Status': False,
                                     'Errors': serializer.errors
                                     })

        if {'city', 'street', 'house'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = UsersContactAdress(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Errors': serializer.errors})
        else:
            return JsonResponse({'Status': False,
                                 'Errors': 'Не указаны  необходимые аргументы'
                                 })
        person = User.objects.filter(id=request.user.id).exclude('id',
                                                                 'company',
                                                                 'position',
                                                                 'adress_cont'
                                                                 )
        list_of_address = UsersContactAdress.object.filter(user=request.user.id)
        serializer_bio = UserSerializer(person)
        serializer_adr = UsrAdressSerializer(list_of_address, many=True)

        return JsonResponse({'Левая половина': serializer_bio.data,
                             'Правая часть': serializer_adr})




"""7. Спасибо за заказ"""
class GreetingOrder(APIView):
    def get(self, request, *args, **kwargs):

        # list_goods = Order.objects.filter(id=request.data['id'])
        # serializer_goods = OrderSerializer(list_goods, many=True)
        # adress = UsersContactAdress.objects.filter(user=request.user.id)
        # serializer_adress = UserSerializer(adress)
        # person = User.objects.filter(id=request.user.id)

        if not request.user.is_authenticated:
            return JsonResponse(
                {'Status': False, 'Error': 'Log in required'},
                status=403
                )

        order_positions = Order.objects.filter(
            user=request.user.id,
            status='confirmed'
            ).select_related(
                'ordered_items__product_info__product__name',
                'ordered_items__shop',
                'ordered_items__shop__product_infos__price'
                'ordered_items__quantity'
        ).exclude('id',
                  'user',
                  'dt',
                  'status',
                  'total_price',
                  'cost_delivery',
                  'order_price',
                  'final_price',
                  'adress_cont',
                  'phone_cont').annotate(summ=Sum(F(
            'ordered_items__quantity') * F('ordered_items__shop__product_infos__price'))).distinct()

        order_client = Order.objects.filter(
            user=request.user.id,
            status='confirmed'
        ).select_related(
            'user__email',
            'user__contactphone',
            'user__contactadress')
        ser_info = OrderSerializer(order_client)
        ser_pos = OrderSerializer(order_positions, many=True)
        upper_module = json.dumps({
            'Номер вашего заказа: ': ser_info.data['id'],
            'Наш оператор свяжется с Вами в ближайшее время для уточнения делатей заказа ': '',
            'Статус заказов вы можете посмотреть в разделе "Заказы" ': ''
            })
        main_module = json.dumps({
            'Детали заказа: ': ser_pos.data,
            'Детали получателя: ': ser_info.data['user', 'user__email', 'user__contactphone'],
            'Адрес: ': ser_info.data['user__contactadress']
            })
        return JsonResponse({'Верхний блок': upper_module,
                             'Основной блок': main_module})



"""8. Список заказов"""
class ListOrderView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'Status': False, 'Error': 'Log in required'},
                status=403,
                )
        orders = (Order.objects.filter(user=request.user.id).annotate(
            order_price=Sum(F(
                'ordered_items__quantity') * F('ordered_items__shop__product_infos__price')
                            )).distinct()).\
            exclude('user',
                    'ordered_items',
                    'summ',
                    'total_summ',
                    'cost_delivery',
                    'final_price',
                    'total',
                    'adress_cont',
                    'phone_cont'
                    )
        ser_orders = OrderSerializer(orders , many=True)
        return JsonResponse({
            'История заказов': ser_orders.data,
        })



"""9. Заказ"""
class OrderView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'Status': False, 'Error': 'Log in required'},
                status=403,
                )

        order_client = Order.objects.filter(
            id=args,
            user=request.user.id,
            status='delivered'
            ).select_related(
                'user__email',
                'user__contactphone',
                'user__contactadress')

        order_positions = Order.objects.filter(
            id=args,
            user=request.user.id,
            status='delivered'
        ).select_related(
            'ordered_items__product_info__product__name',
            'ordered_items__shop',
            'ordered_items__shop__product_infos__price'
            'ordered_items__quantity'
        ).exclude('id',
                  'user',
                  'dt',
                  'status',
                  'total_price',
                  'cost_delivery',
                  'order_price',
                  'final_price',
                  'adress_cont',
                  'phone_cont'
                  ).annotate(summ=Sum(F(
            'ordered_items__quantity') * F('ordered_items__shop__product_infos__price'))).distinct()

        ser_info = OrderSerializer(order_client)
        ser_pos = OrderSerializer(order_positions, many=True)
        upper_module = json.dumps({
            'Номер: ': ser_info.data('id'),
            'Дата: ': ser_info.data('dt'),
            'Статус: Доставлен ': ser_info.data('dt')
            })
        main_module = json.dumps({
            'Детали заказа: ': ser_pos.data,
            'Детали получателя: ': ser_info.data['user',
                                                 'user__email',
                                                 'user__contactphone'
                                                ],
            'Адрес: ': ser_info.data['user__contactadress']
             })

        return JsonResponse({
            'Верхний блок': upper_module,
            'Основной блок': main_module
            })



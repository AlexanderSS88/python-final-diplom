from idlelib.searchengine import get
from django.core.validators import URLValidator
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from yaml import load, Loader
from .models import ProductInfo, Product, Parameter, ProductParameter, Category, Shop
from celery import shared_task
from .tasks import update_price


"""Класс для обновления прайса от поставщика"""
class PartnerUpdate(APIView):

    def post(self, request, *args, **kwargs):

        update_price.delay(request, *args, **kwargs)




        # if not request.user.is_authenticated:
        #     return JsonResponse(
        #         {'Status': False, 'Error': 'Нужна авторизация'},
        #         status=403
        #         )
        #
        # if request.user.type != 'shop':
        #     return JsonResponse(
        #         {'Status': False, 'Error': 'Только для магазинов'},
        #         status=403
        #         )
        #
        # url = request.data.get('url')
        # if url:
        #     validate_url = URLValidator()
        #     try:
        #         validate_url(url)
        #     except ValidationError as e:
        #         return JsonResponse({'Status': False, 'Error': str(e)})
        #     else:
        #         stream = get(url).content
        #         data = load(stream, Loader=Loader)
        #         shop, _ = Shop.objects.get_or_create(
        #             name=data['shop'],
        #             user=request.user.id
        #             )
        #         for category in data['categories']:
        #             category_object, _ = Category.objects.get_or_create(
        #                 id=category['id'],
        #                 name=category['name']
        #                 )
        #             category_object.shops.add(shop.id)
        #             category_object.save()
        #
        #         ProductInfo.objects.filter(shop=shop.id).delete()
        #         for item in data['goods']:
        #             product, _ = Product.objects.get_or_create(
        #                 name=item['name'],
        #                 category=item['category']
        #                 )
        #             product_info = ProductInfo.objects.create(
        #                 external_id=item['id'],
        #                 model=item['model'],
        #                 shop=shop.id,
        #                 product=product.id,
        #                 quantity=item['quantity'],
        #                 price=item['price'],
        #                 price_rrc=item['price_rrc']
        #                 )
        #             for name, value in item['parameters'].items():
        #                 parameter_object, _ = Parameter.objects.get_or_create(name=name)
        #                 ProductParameter.objects.create(
        #                     product_info=product_info.id,
        #                     parameter=parameter_object.id,
        #                     value=value
        #                     )
        #         return JsonResponse({'Status': True})
        #
        # return JsonResponse(
        #     {'Status': False,
        #      'Errors': 'Не указаны все необходимые аргументы'}
        #     )
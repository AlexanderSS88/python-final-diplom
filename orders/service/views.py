from rest_framework.views import APIView
from .tasks import update_price


"""Класс для обновления прайса от поставщика"""
class PartnerUpdate(APIView):

    def post(self, request, *args, **kwargs):

        update_price.delay(request, *args, **kwargs)





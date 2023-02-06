"""orders URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from endpoints.views import LoginAccount, RegisterAccount, \
    ProductListView, ProductDetailView, BasketView, AcceptOrder, \
    GreetingOrder, ListOrderView, OrderView
from service.views import PartnerUpdate

app_name = 'orders'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/login',
         LoginAccount.as_view(),
         name='user_login_1'
         ),
    path('user/register',
         RegisterAccount.as_view(),
         name='user_register_2'
         ),
    path('user/products',
         ProductListView.as_view(),
         name='all_products_3'
         ),
    path('user/products/<int:pk>',
         ProductDetailView.as_view(),
         name='product_info_4'
         ),
    path('user/basket',
         BasketView.as_view(),
         name='basket_5'
         ),
    path('user/accept_order',
         AcceptOrder.as_view(),
         name='accept_order_6'
         ),
    path('user/greeting',
         GreetingOrder.as_view(),
         name='greeting_for_order_7'
         ),
    path('user/orders',
         ListOrderView.as_view(),
         name='orders_8'
         ),
    path('user/order',
         OrderView.as_view(),
         name='order_9'
         ),
    path('update_catalog',
         PartnerUpdate.as_view(),
         name='update_catalog'
         ),
    ]
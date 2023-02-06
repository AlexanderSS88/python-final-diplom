from rest_framework.fields import IntegerField, DecimalField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer
from service.models import User, UsersContactAdress, \
    UsersContactPhone, Product, ProductParameter,\
    ProductInfo, Shop, OrderItem, Order



class UsrAdressSerializer(ModelSerializer):

    class Meta:
        model = UsersContactAdress
        fields = ('id',
                  'user',
                  'city',
                  'street',
                  'house',
                  'structure',
                  'building',
                  'apartment')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True},
            }



class UsrPhoneSerializer(ModelSerializer):

    class Meta:
        model = UsersContactPhone
        fields = ('id', 'user', 'value')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True},
            }



class UserSerializer(ModelSerializer):
    adress_cont = UsrAdressSerializer(read_only=True, many=True)
    phone_cont = UsrPhoneSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'second_name',
                  'last_name',
                  'email',
                  'company',
                  'position',
                  'adress_cont',
                  'phone_cont'
                  )
        read_only_fields = ('id',)



class ProductSerializer(ModelSerializer):
    category = StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category',)
        extra_kwargs = {'name': {'required': False}}



class ProductParameterSerializer(ModelSerializer):
    parameter = StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('product_info', 'parameter', 'value',)




class ShopSerializer(ModelSerializer):

    class Meta:
        model = Shop
        fields = ('id', 'name', 'distance', 'url', 'filename', 'user')
        read_only_fields = ('id',)




class ProductInfoSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ('external_id',
                  'model',
                  'product',
                  'shop',
                  'quantity',
                  'price',
                  'price_rrc',
                  'product_parameters',)
        read_only_fields = ('id',)



class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order', 'shop')
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }



class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)



class OrderSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    adress_cont = UsrAdressSerializer(read_only=True)
    phone_cont = UsrPhoneSerializer(read_only=True)
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)
    cost_delivery = DecimalField(decimal_places=3, max_digits=2)
    total_price = IntegerField()
    order_price = DecimalField(decimal_places=3, max_digits=2)
    final_price = DecimalField(decimal_places=3, max_digits=2)

    class Meta:
        model = Order
        fields = ('id',
                  'user',
                  'dt',
                  'status',
                  'ordered_items',
                  'total_price',
                  'cost_delivery',
                  'order_price',
                  'final_price',
                  'adress_cont',
                  'phone_cont'
                  )
        read_only_fields = ('id',)
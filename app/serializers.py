from rest_framework import serializers
from .models import User, Product, ProductType, Purchase

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class BuyProductSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Purchase
        fields = ['telegram_id', 'product_id']

    def create(self, validated_data):
        telegram_id = validated_data['telegram_id']
        product_id = validated_data['product_id']

        try:
            buyer = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Buyer not found.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")

        seller = product.user

        return Purchase.objects.create(buyer=buyer, seller=seller, product=product)



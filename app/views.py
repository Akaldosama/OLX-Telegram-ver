from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view

from .models import Cart
from .serializers import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import send_message_to_seller


class UserRegistrationView(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        fullname = request.data.get('fullname')
        phone = request.data.get('phone')

        if not telegram_id:
            return Response({'error': 'telegram_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telegram_id=telegram_id)

            # If fullname and phone are provided, complete registration
            if fullname and phone:
                user.fullname = fullname
                user.phone = phone
                user.is_registered = True
                user.save()

                return Response({
                    'id': user.id,  # ✅ return ID
                    'message': 'User registered successfully.',
                    'is_registered': user.is_registered,
                    'fullname': user.fullname
                }, status=status.HTTP_200_OK)

            # Otherwise, just return the existing status
            return Response({
                'id': user.id,  # ✅ return ID
                'is_registered': user.is_registered,
                'fullname': user.fullname if user.is_registered else ''
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            user = User.objects.create(
                telegram_id=telegram_id,
                fullname='',
                phone='',
                is_registered=False
            )
            return Response({
                'id': user.id,  # ✅ return ID
                'is_registered': False
            }, status=status.HTTP_201_CREATED)


class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


# views.py
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']

    def get_queryset(self):
        queryset = super().get_queryset()
        product_type = self.request.query_params.get('type')

        if product_type:
            queryset = queryset.filter(type__name=product_type)  # 💡 using name, not id

        return queryset




class BuyProductView(APIView):
    def post(self, request):
        print("Received data:", request.data)  # 🔍 Add this

        serializer = BuyProductSerializer(data=request.data)
        if serializer.is_valid():
            cart = serializer.save()
            product = cart.product
            seller = product.user
            buyer = cart.buyer

            print(f"Buyer: {buyer.fullname}, Phone: {buyer.phone}")
            print(f"Seller TG ID: {seller.telegram_id}, Product: {product.title}")

            send_message_to_seller(
                seller_telegram_id=seller.telegram_id,
                buyer_name=buyer.fullname,
                buyer_phone=buyer.phone,
                product_title=product.title
            )

            return Response({'message': 'Product added to cart.'}, status=status.HTTP_201_CREATED)

        print("Serializer error:", serializer.errors)  # 🔍 Add this
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def AddToCartView(request):
    telegram_id = request.data.get('user_telegram_id')
    product_id = request.data.get('product_id')

    try:
        user = User.objects.get(telegram_id=telegram_id)
        product = Product.objects.get(id=product_id)
        Cart.objects.create(user=user, product=product)
        return Response({'message': 'Added to cart'}, status=201)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)


@api_view(['GET'])
def get_cart(request, telegram_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        cart_items = Cart.objects.filter(user=user)
        data = [
            {
                'id': item.id,
                'product': ProductSerializer(item.product).data
            }
            for item in cart_items
        ]
        return Response(data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)






@api_view(['GET'])
def get_user_by_telegram_id(request, telegram_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        return Response({'is_registered': True})
    except User.DoesNotExist:
        return Response({'is_registered': False})

@api_view(['GET'])
def list_products(request):
    seller_id = request.GET.get('user')
    if seller_id:
        products = Product.objects.filter(user__telegram_id=seller_id)
    else:
        products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


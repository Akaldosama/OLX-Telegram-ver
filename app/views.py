from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from .serializers import *
from rest_framework.views import APIView
from .utils import send_message_to_seller

from .models import Cart, Product, User
from .serializers import CartSerializer

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, User
from .serializers import ProductSerializer



class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__telegram_id']  # ✅ Fix here

    def get_queryset(self):
        queryset = Product.objects.all()
        telegram_id = self.request.query_params.get('user')
        product_type = self.request.query_params.get('type')

        if telegram_id:
            queryset = queryset.filter(user__telegram_id=telegram_id)
        if product_type:
            queryset = queryset.filter(type__name=product_type)

        return queryset

    def destroy(self, request, pk=None):
        telegram_id = self.request.query_params.get('user')
        if not telegram_id:
            return Response({'error': 'Missing user ID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(pk=pk, user=user)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found or not owned by user'}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)



# views.py
# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['user']
#     permission_classes = [AllowAny]
#
#
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         product_type = self.request.query_params.get('type')
#
#         if product_type:
#             queryset = queryset.filter(type__name=product_type)  # 💡 using name, not id
#
#         return queryset




class BuyProductView(APIView):
    permission_classes = [AllowAny]

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


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        telegram_id = request.data.get('user_telegram_id')
        product_id = request.data.get('product_id')

        try:
            user = User.objects.get(telegram_id=telegram_id)
            product = Product.objects.get(id=product_id)
            Cart.objects.create(user=user, product=product)
            return Response({'message': 'Added to cart'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<telegram_id>[^/.]+)')
    def get_cart_by_user(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
            cart_items = Cart.objects.filter(user=user)
            serializer = self.get_serializer(cart_items, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'], url_path='(?P<telegram_id>[^/.]+)/(?P<product_id>[^/.]+)')
    @method_decorator(csrf_exempt, name='dispatch')
    def remove_from_cart(self, request, telegram_id, product_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item = Cart.objects.filter(user=user, product__id=product_id).first()
        if not cart_item:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_user_by_telegram_id(request, telegram_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        return Response({
            'is_registered': True,
            'id': user.id,  # ✅ Add this line
        })
    except User.DoesNotExist:
        return Response({'is_registered': False})


# @api_view(['GET'])
# def list_products(request):
#     seller_id = request.GET.get('user')
#     if seller_id:
#         products = Product.objects.filter(user__telegram_id=seller_id)
#     else:
#         products = Product.objects.all()
#
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)
#
#
#
#
# @api_view(['DELETE'])
# @csrf_exempt
# def delete_product(request, product_id):
#     telegram_id = request.GET.get('user')
#
#     if not telegram_id:
#         return Response({'error': 'Missing user ID'}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         user = User.objects.get(telegram_id=telegram_id)
#     except User.DoesNotExist:
#         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     try:
#         product = Product.objects.get(id=product_id, user=user)
#     except Product.DoesNotExist:
#         return Response({'error': 'Product not found or not owned by user'}, status=status.HTTP_404_NOT_FOUND)
#
#     product.delete()
#     return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)

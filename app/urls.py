# from django.urls import path, include
# from .views import *
# from rest_framework.routers import DefaultRouter
#
# from django.conf import settings
# from django.conf.urls.static import static
#
# router = DefaultRouter()
# router.register(r'products', ProductViewSet)
# router.register(r'product-types', ProductTypeViewSet)
# router.register(r'cart', CartViewSet, basename='cart')
#
# from rest_framework.decorators import api_view
#
# @api_view(['DELETE'])
# def remove_from_cart(request, telegram_id, product_id):
#     try:
#         user = User.objects.get(telegram_id=telegram_id)
#         cart_item = Cart.objects.filter(user=user, product__id=product_id).first()
#         if not cart_item:
#             return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
#         cart_item.delete()
#         return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
#     except User.DoesNotExist:
#         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#
# urlpatterns = [
#     path('registration/', UserRegistrationView.as_view(), name='user_registration'),
#     path('', include(router.urls)),
#
#     # User
#     path('user/<str:telegram_id>', get_user_by_telegram_id),
#
#     # Product list (filtered)
#     path('products', list_products),
#     path('products/<int:product_id>/', delete_product, name='product_delete'),
#
#     # Cart
#     path('cart/<str:telegram_id>/<int:product_id>/', remove_from_cart),
#
#     # Buy
#     path('buy/', BuyProductView.as_view(), name='buy_product'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#


from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product-types', ProductTypeViewSet)
router.register(r'cart', CartViewSet, basename='cart')

from rest_framework.decorators import api_view

@api_view(['DELETE'])
def remove_from_cart(request, telegram_id, product_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        cart_item = Cart.objects.filter(user=user, product__id=product_id).first()
        if not cart_item:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='user_registration'),
    path('', include(router.urls)),

    # User
    path('user/<str:telegram_id>', get_user_by_telegram_id),

    # Cart
    path('cart/<str:telegram_id>/<int:product_id>/', remove_from_cart),

    # Buy
    path('buy/', BuyProductView.as_view(), name='buy_product'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# from django.urls import path, include
# from .views import *
# from rest_framework.routers import DefaultRouter
#
# from django.conf import settings
# from django.conf.urls.static import static
#
# # used router because of viewset
# router = DefaultRouter()
# router.register(r'products', ProductViewSet)
# router.register(r'product-types', ProductTypeViewSet)
#
#
# urlpatterns = [
#     path('registration/', UserRegistrationView.as_view(), name='user_registration'),
#     path('', include(router.urls)),
#     path('add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),
#     path('user/<str:telegram_id>', get_user_by_telegram_id),
#     path('products', list_products),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product-types', ProductTypeViewSet)

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='user_registration'),
    path('', include(router.urls)),

    # User
    path('user/<str:telegram_id>', get_user_by_telegram_id),

    # Product list (filtered)
    path('products', list_products),

    # Cart
    path('cart/', AddToCartView, name='add_to_cart'),  # For cart button
    path('cart/<str:telegram_id>/', get_cart, name='get_cart'),

    # Buy
    path('buy/', BuyProductView.as_view(), name='buy_product'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

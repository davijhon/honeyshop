from django.urls import path

from .views import (
	HomePageView, 
	ServicesPageView, 
	ProductDetailView, 
	CartPageView, 
	add_to_cart, 
	remove_from_cart, 
	remove_single_item_from_cart,
	CheckoutView, 
	PaymentView, 
	RequestRefundView,
	payment_complete,
	ProductListView
)

app_name = 'shop'


urlpatterns = [
	path('', HomePageView.as_view(), name='home'),
	path('cart/', CartPageView.as_view(), name='cart'),
	path('services/', ServicesPageView.as_view(), name='services'),
	path('checkout/', CheckoutView.as_view(), name='checkout'),
	path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
	path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
	path('products/', ProductListView.as_view(), name='products'),
	path('product-detail/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
	path('remove-item-from-cart/<slug>', remove_single_item_from_cart, name='remove-single-item-from-cart'),
	path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
	path('payment-complete', payment_complete, name='payment_complete'),
	path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
]
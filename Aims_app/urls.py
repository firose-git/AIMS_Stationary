from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.user_login, name='login'),
    
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('stationary/', views.stationary_view, name='stationary'),
    path('stationary_product/', views.stationary_page, name='Stationary_product'),
    path('paper/', views.paper_view, name='paper_page'),
    path('Filing/', views.Filing_view, name='Filing_page'),
    path('category/<str:category_name>/', views.category_view, name='category_page'),
    path('subcategory/<str:subcat_id>/', views.subcategory_products, name='subcategory_products'),
    path('electronics/', views.electronics_categories, name='electronics_categories'),
    path('electronics/<slug:slug>/', views.electronics_products, name='electronics_products'),
    path('message/', views.message_view, name='message'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),  # ✅ Correct pattern
    #path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Corrected URL pattern for updating cart items
    #path('cart/update/<int:cart_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/update/<str:cart_id>/<str:action>/', views.update_cart, name='update_cart'),
    # Corrected URL pattern for removing items from cart
    path('cart/remove/<str:Cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('confirm-order/', views.confirmPurchase, name='confirm_order'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('search/', views.search_products, name='search'),
    
    
    path('admin/report/download/', views.download_order_report, name='download_order_report'),
    path('admin/report/view/', views.view_report, name='view_order_report'),
    
]

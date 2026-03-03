from django.urls import path
from . import views

urlpatterns = [
    # ---------- AUTH ----------
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<str:token>/", views.reset_password, name="reset_password"),
    path("logout/", views.logout_view, name="logout"),

    # ---------- PRODUCTS ----------
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/update/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("products/<int:pk>/restock/", views.restock_product, name="product_restock"),

    # ---------- CART ----------
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/delete/", views.cart_delete, name="cart_delete"),

    # ---------- ORDER ----------
    path("checkout/", views.checkout, name="checkout"),

    # ---------- CATEGORY ----------
    path("categories/", views.category_list, name="category_list"),
]
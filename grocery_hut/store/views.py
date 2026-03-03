from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Category, CartItem, Order
import json
from django.core.mail import send_mail
import uuid
from .models import PasswordReset
from django.conf import settings


# ---------------- USER AUTH ----------------

@csrf_exempt
def signup_view(request):
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,        # ✅ THIS LINE IS CRITICAL
            password=password
        )

        return JsonResponse({"status": "ok"})


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # -------------------------------
        # Case 1: Normal login (username + password)
        # -------------------------------
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({
                    "status": "ok",
                    "username": user.username,
                    "email": user.email
                })
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=401)

        # -------------------------------
        # Case 2: Email login (forgot password flow)
        # -------------------------------
        if email and not password:
            try:
                user = User.objects.get(email=email)
                login(request, user)
                return JsonResponse({
                    "status": "ok",
                    "username": user.username,
                    "email": user.email
                })
            except User.DoesNotExist:
                return JsonResponse({"error": "Email not found"}, status=404)

        return JsonResponse({"error": "Invalid login data"}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def forgot_password(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")

            if not username or not email:
                return JsonResponse({"error": "Username and email are required"}, status=400)

            try:
                user = User.objects.get(username=username, email=email)
            except User.DoesNotExist:
                return JsonResponse({"error": "Username and email do not match"}, status=404)

            token = str(uuid.uuid4())

            PasswordReset.objects.update_or_create(
                user=user,
                defaults={"token": token}
            )

            reset_link = f"http://localhost:3000/reset-password/{token}"

            send_mail(
                "Password Reset",
                f"Click this link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return JsonResponse({"message": "Password reset link sent to your registered email"})

        except Exception as e:
            print("FORGOT PASSWORD ERROR:", e)
            return JsonResponse({"error": "Something went wrong"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)

        

@csrf_exempt
def reset_password(request, token):
    if request.method == "POST":
        data = json.loads(request.body)
        new_password = data.get("password")

        try:
            user = User.objects.get(last_name=token)
            user.set_password(new_password)
            user.last_name = ""   # clear token
            user.save()

            return JsonResponse({"message": "Password reset successful"})

        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid or expired token"}, status=400)



@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "invalid method"}, status=400)


# ---------------- PRODUCT ----------------

@csrf_exempt
def product_list(request):
    if request.method == "GET":
        category = request.GET.get("category")

        if category and category.lower() != "all":
            products = Product.objects.filter(category__name__iexact=category)
        else:
            products = Product.objects.all()

        data = [{
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "stock": p.stock,
            "category": p.category.name if p.category else None
        } for p in products]

        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data = json.loads(request.body)
        cat, _ = Category.objects.get_or_create(name=data["category"])
        product = Product.objects.create(
            name=data["name"],
            price=data["price"],
            stock=data["stock"],
            category=cat
        )
        return JsonResponse({"id": product.id})

    return JsonResponse({"error": "invalid method"}, status=400)


# additional product endpoints (update/delete/restock)
@csrf_exempt
def product_update(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        product = get_object_or_404(Product, id=pk)

        name = data.get("name")
        price = data.get("price")
        stock = data.get("stock")
        category_name = data.get("category")

        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = int(stock)
        if category_name is not None:
            cat, _ = Category.objects.get_or_create(name=category_name)
            product.category = cat

        product.save()
        return JsonResponse({"status": "updated"})

    return JsonResponse({"error": "invalid method"}, status=400)


@csrf_exempt
def product_delete(request, pk):
    if request.method == "POST":
        product = get_object_or_404(Product, id=pk)
        product.delete()
        return JsonResponse({"status": "deleted"})

    return JsonResponse({"error": "invalid method"}, status=400)


@csrf_exempt
def restock_product(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        product = get_object_or_404(Product, id=pk)

        # accept either an absolute stock value or an amount to add
        if "amount" in data:
            amount = int(data["amount"])
            if amount < 0:
                return JsonResponse({"error": "invalid amount"}, status=400)
            product.stock += amount
        elif "stock" in data:
            stock = int(data["stock"])
            if stock < 0:
                return JsonResponse({"error": "invalid stock"}, status=400)
            product.stock = stock
        else:
            return JsonResponse({"error": "missing stock data"}, status=400)

        product.save()
        return JsonResponse({"status": "restocked", "stock": product.stock})

    return JsonResponse({"error": "invalid method"}, status=400)


# ---------------- CART ----------------

@csrf_exempt
def cart_add(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        data = json.loads(request.body)
        product = get_object_or_404(Product, id=data["product_id"])
        quantity = int(data.get("quantity", 1))

        if quantity > product.stock:
            return JsonResponse({"error": "Not enough stock"}, status=400)

        cart_item, _ = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"status": "added"})

    return JsonResponse({"error": "invalid method"}, status=400)


def cart_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)

    items = CartItem.objects.filter(user=request.user)
    cart_items = []
    cart_total = 0

    for item in items:
        item_total = item.product.price * item.quantity
        cart_total += item_total

        cart_items.append({
            "id": item.id,
            "name": item.product.name,
            "quantity": item.quantity,
            "price": float(item.product.price),
            "total": float(item_total)
        })

    return JsonResponse({
        "items": cart_items,
        "cart_total": float(cart_total)
    })


@csrf_exempt
def cart_update(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        data = json.loads(request.body)
        cart_item = get_object_or_404(
            CartItem,
            id=data["cart_item_id"],
            user=request.user
        )

        quantity = int(data["quantity"])
        if quantity > cart_item.product.stock:
            return JsonResponse({"error": "Not enough stock"}, status=400)

        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"status": "updated"})

    return JsonResponse({"error": "invalid method"}, status=400)


@csrf_exempt
def cart_delete(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        data = json.loads(request.body)
        cart_item = get_object_or_404(
            CartItem,
            id=data["cart_item_id"],
            user=request.user
        )
        cart_item.delete()

        return JsonResponse({"status": "deleted"})

    return JsonResponse({"error": "invalid method"}, status=400)


# ---------------- CHECKOUT ----------------

@csrf_exempt
def checkout(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        items = CartItem.objects.filter(user=request.user)
        if not items.exists():
            return JsonResponse({"error": "Cart is empty"}, status=400)

        total = 0
        for item in items:
            if item.quantity > item.product.stock:
                return JsonResponse({"error": "Stock issue"}, status=400)

            item.product.stock -= item.quantity
            item.product.save()
            total += item.product.price * item.quantity

        order = Order.objects.create(user=request.user, total=total)
        order.items.set(items)
        items.delete()

        return JsonResponse({"status": "order placed", "total": float(total)})

    return JsonResponse({"error": "invalid method"}, status=400)


# ---------------- CATEGORY ----------------

def category_list(request):
    if request.method == "GET":
        categories = list(Category.objects.values("id", "name"))
        return JsonResponse(categories, safe=False)
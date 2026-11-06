from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Product, Order, OrderItem


from .models import Product


def shop(request):
    products = Product.objects.all().order_by("-created_at")

    search = request.GET.get("search", "")
    category = request.GET.get("category", "")

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search)
        )

    if category:
        products = products.filter(category=category)

    return render(request, "store/shop.html", {
        "products": products,
        "categories": Product.CATEGORY_CHOICES,
        "search": search,
        "selected_category": category,
    })
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get existing cart from session
    cart = request.session.get("cart", {})

    # Check product stock
    if product.stock > 0:
        product_id = str(product.id)

        # Increase quantity if product already exists
        if product_id in cart:
            if cart[product_id] < product.stock:
                cart[product_id] += 1
        else:
            cart[product_id] = 1

    # Save cart in session
    request.session["cart"] = cart
    request.session.modified = True

    return redirect("shop")



def cart(request):

    cart_items = []
    total = Decimal('0.00')

    cart_data = request.session.get('cart', {})

    for product_id, quantity in cart_data.items():

        product = Product.objects.filter(
            id=product_id
        ).first()

        if product:
            quantity = min(int(quantity), product.stock)

            if quantity <= 0:
                continue

            subtotal = product.price * quantity
            total += subtotal

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })



def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


@login_required
def dashboard(request):
    return render(request, "store/dashboard.html")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})



@login_required
def product_list(request):
    products = Product.objects.all().order_by("-created_at")

    return render(request, "store/product_list.html", {
        "products": products
    })



@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(request, "store/product_form.html", {
        "form": form,
        "title": "Add Product"
    })



@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(request, "store/product_detail.html", {
        "product": product
    })


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "store/product_form.html", {
        "form": form,
        "title": "Edit Product"
    })



@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect("product_list")

    return render(request, "store/product_confirm_delete.html", {
        "product": product
    })


def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect("dashboard")

        else:
            messages.error(
                request,
                "Invalid admin username or password."
            )

    return render(request, "registration/admin_login.html")

@login_required
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("shop")

    cart_items = []
    total = Decimal("0.00")

    for product_id, quantity in cart.items():

        product = get_object_or_404(Product, id=product_id)

        quantity = int(quantity)

        subtotal = product.price * quantity

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

        total += subtotal

    if request.method == "POST":

        customer_name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if not customer_name or not phone or not address:
            messages.error(request, "Please fill in all delivery details.")
            return render(request, "store/checkout.html", {
                "cart_items": cart_items,
                "total": total
            })

        try:
            with transaction.atomic():

              
                order_products = {}

                for product_id, quantity in cart.items():

                    product = Product.objects.select_for_update().get(
                        id=product_id
                    )

                    quantity = int(quantity)

                    if quantity <= 0 or product.stock < quantity:
                        raise ValueError(
                            f"Insufficient stock for {product.name}"
                        )

                    order_products[product_id] = (product, quantity)

               
                order = Order.objects.create(
                    user=request.user,
                    customer_name=customer_name,
                    phone=phone,
                    address=address,
                    total_amount=total
                )

                
                for product, quantity in order_products.values():

                    subtotal = product.price * quantity

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=quantity,
                        subtotal=subtotal
                    )

                   
                    product.stock -= quantity
                    product.save(update_fields=["stock"])

            request.session["cart"] = {}
            request.session.modified = True

            return redirect("order_success", order_id=order.id)

        except Product.DoesNotExist:
            messages.error(request, "A product in your cart is unavailable.")

        except ValueError as error:
            messages.error(request, str(error))

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "store/order_success.html",
        {"order": order}
    )


@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "store/my_orders.html",
        {"orders": orders}
    )
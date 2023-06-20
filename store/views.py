from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Song
from django.contrib.auth.models import User, auth
from django.contrib import messages



def home(request):
    return render(request, "store/home.html")


def about(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email == '':
            messages.info(request, 'Please fill all your details ')
            return redirect('/about')
        else:
            new_email = NewsLetter( email=email)
            new_email.save()
        
    return render(request, "store/about.html")


def music(request):
    paginator = Paginator(Song.objects.all(), 1)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}

    return render(request, "store/music.html", context)


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']

        if name == '':
            messages.info(request, 'Please fill all your details ')
            return redirect('/')
        else:
            new_contact = Contact(name=name, email=email,
                                  phone=phone, message=message)
            new_contact.save()
    return render(request, "store/contact.html")


def events(request):
    videos = Video.objects.all()
    context = {'videos': videos}
    return render(request, "store/event.html", context)


@login_required(login_url="login")
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "username Already Taken")
                return redirect("register")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Used ")
                return redirect("register")

            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()
                return redirect("login")
        else:
            messages.info(request, "Password does not  match")
            return redirect("register")
    else:
        return render(request, "store/register.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("store")
        else:
            messages.info(request, "Invalid Credentials!")
            return redirect("login")
    else:
        return render(request, "store/login.html")


def logout(request):
    auth.logout(request)
    return redirect("store")


def store(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def cart(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


def checkout(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print("Action:", action)
    print("Product:", productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("Payment submitted..", safe=False)

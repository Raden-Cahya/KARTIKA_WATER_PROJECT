from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def cart(request):
    return render(request, 'cart.html')

def checkout(request):
    return render(request, 'checkout.html')

def contact(request):
    return render(request, 'contact-us.html')

def gallery(request):
    return render(request, 'gallery.html')

def my_account(request):
    return render(request, 'my-account.html')

def shop(request):
    return render(request, 'shop.html')

def shop_detail(request):
    return render(request, 'shop-detail.html')

def wishlist(request):
    return render(request, 'wishlist.html')

def login(request):
    return render(request, 'auth/index.html')

def register(request):
    return render(request, 'auth/register.html')
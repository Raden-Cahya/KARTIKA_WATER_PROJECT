# main/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse # Import HttpResponse
from django.db import transaction
from .models import Product, Cart, CartItem, Order, OrderItem
import json

# Import untuk PDF
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.conf import settings # Untuk mengakses pengaturan seperti STATIC_ROOT jika diperlukan

# Import form kustom kita dari main/forms.py
from .forms import CustomUserCreationForm, CustomAuthenticationForm


# --- Views Halaman Statis ---

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@login_required
def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = cart.get_total_price()
    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items, 'total_price': total_price})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Keranjang Anda kosong. Silakan tambahkan produk terlebih dahulu.")
        return redirect('shop')

    subtotal = sum(item.get_total_item_price() for item in cart_items)
    discount = 0
    tax = 0
    shipping_cost = 0
    grand_total = subtotal - discount + tax + shipping_cost

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'tax': tax,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
    }
    return render(request, 'checkout.html', context)


def contact(request):
    return render(request, 'contact-us.html')

def gallery(request):
    return render(request, 'gallery.html')

@login_required
def my_account(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my-account.html', {'orders': orders})

def shop_detail(request):
    product_id = request.GET.get('product_id')
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop-detail.html', {'product': product})

def wishlist(request):
    return render(request, 'wishlist.html')


# --- Views Otentikasi ---

def login_page(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Selamat datang kembali, {username}!")
                return redirect('index')
            else:
                messages.error(request, "Username atau password salah.")
        else:
            messages.error(request, "Silakan masukkan username dan password yang valid.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth/index.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect('login')
        else:
            messages.error(request, "Terjadi kesalahan saat registrasi. Mohon periksa kembali input Anda.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "Anda telah berhasil logout.")
    return redirect('index')


# --- Views Keranjang dan Transaksi ---

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        message = ""
        if not item_created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
                message = f"Kuantitas '{product.name}' di keranjang diperbarui menjadi {cart_item.quantity}."
            else:
                message = f"Stok maksimum untuk '{product.name}' telah tercapai."
                return JsonResponse({'status': 'warning', 'message': message, 'product_name': product.name})
        else:
            message = f"'{product.name}' telah ditambahkan ke keranjang Anda."

        return JsonResponse({'status': 'success', 'message': message, 'product_name': product.name})
    
    return redirect('shop')


@login_required
def update_cart_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            new_quantity = int(request.POST.get('quantity'))
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Kuantitas tidak valid.'})

        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            product = cart_item.product

            if new_quantity < 1:
                new_quantity = 1
            if new_quantity > product.stock:
                new_quantity = product.stock

            if new_quantity == 0:
                cart_item.delete()
                cart = get_object_or_404(Cart, user=request.user)
                return JsonResponse({
                    'success': True,
                    'new_quantity': 0,
                    'new_item_total': 0,
                    'cart_total_price': f"{cart.get_total_price():.0f}"
                })
            
            if cart_item.quantity == new_quantity:
                return JsonResponse({
                    'success': True,
                    'new_quantity': new_quantity,
                    'new_item_total': f"{cart_item.get_total_item_price():.0f}",
                    'cart_total_price': f"{cart_item.cart.get_total_price():.0f}"
                })

            with transaction.atomic():
                cart_item.quantity = new_quantity
                cart_item.save()

                cart = cart_item.cart
                cart_total_price = cart.get_total_price()
                item_total_price = cart_item.get_total_item_price()

            return JsonResponse({
                'success': True,
                'new_quantity': new_quantity,
                'new_item_total': f"{item_total_price:.0f}",
                'cart_total_price': f"{cart_total_price:.0f}"
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item keranjang tidak ditemukan.'}, status=404)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Produk tidak ditemukan.'}, status=404)
        except Exception as e:
            print(f"Error in update_cart_item_quantity: {e}")
            return JsonResponse({'success': False, 'error': f'Terjadi kesalahan server: {str(e)}'}, status=500)
            
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, "Item telah dihapus dari keranjang Anda.")
    return redirect('cart')

@login_required
def checkout_process(request):
    """
    Memproses finalisasi pesanan dari keranjang belanja pengguna.
    Membuat objek Order, mengurangi stok, mengosongkan keranjang,
    mengatur status 'Pending', dan membuat invoice PDF.
    """
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Keranjang Anda kosong. Tidak dapat melanjutkan checkout.")
        return redirect('shop')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Hitung total_order_amount sebelum membuat Order
                total_order_amount = sum(item.get_total_item_price() for item in cart_items)

                order = Order.objects.create(
                    user=request.user,
                    first_name=request.user.first_name if request.user.first_name else '',
                    last_name=request.user.last_name if request.user.last_name else '',
                    email=request.user.email if request.user.email else '',
                    phone_number='', # Pastikan ini diisi jika ada di User model atau dihapus jika tidak perlu
                    shipping_address='N/A (No shipping address required)',
                    payment_method='Direct Payment',
                    total_amount=total_order_amount, # Set total_amount
                    status='Pending' # Set status order menjadi 'Pending'
                )
                
                for item in cart_items:
                    if item.product.stock >= item.quantity:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price
                        )
                        item.product.stock -= item.quantity
                        item.product.save()
                    else:
                        messages.error(request, f"Stok tidak mencukupi untuk '{item.product.name}'. Silakan sesuaikan kuantitas di keranjang.")
                        raise Exception(f"Stok tidak mencukupi untuk '{item.product.name}'")
            
                cart_items.delete() # Kosongkan keranjang setelah order berhasil

                # --- Bagian untuk membuat PDF Invoice ---
                template = get_template('invoice.html') # Mengambil template invoice
                context = {'order': order} # Data yang akan dikirim ke template
                html = template.render(context) # Render template menjadi string HTML

                # Membuat objek HTML dari string
                pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()

                # Mengembalikan PDF sebagai HttpResponse
                response = HttpResponse(pdf_file, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
                
                # Anda bisa juga menambahkan pesan sukses ke session jika ingin redirect ke halaman lain
                messages.success(request, f"Pesanan Anda (ID: {order.id}) telah berhasil dibuat dan invoice diunduh!")
                
                return response # Mengembalikan PDF sebagai respons

        except Exception as e:
            print(f"Error during checkout_process: {e}")
            messages.error(request, f"Gagal membuat pesanan: {str(e)}")
            # Jika ada error, redirect ke halaman checkout atau cart
            return redirect('checkout') # Atau JsonResponse jika menggunakan AJAX

    return redirect('checkout') # Jika request bukan POST, redirect ke checkout

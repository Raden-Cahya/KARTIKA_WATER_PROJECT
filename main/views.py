# main/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse # <-- Pastikan ini ada
from django.db import transaction # <-- Pastikan ini ada
from .models import Product, Cart, CartItem, Order, OrderItem # Pastikan semua model diimport

# Import form kustom kita dari main/forms.py
from .forms import CustomUserCreationForm, CustomAuthenticationForm


# --- Views Halaman Statis ---

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

# View untuk menampilkan daftar produk
def shop(request):
    products = Product.objects.all() # Mengambil semua produk dari database
    return render(request, 'shop.html', {'products': products})

# View untuk menampilkan isi keranjang belanja
@login_required
def cart_view(request): # Nama fungsi di views
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all() # Pastikan Anda mendapatkan semua item dari keranjang
    total_price = cart.get_total_price()
    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items, 'total_price': total_price})

# View untuk halaman checkout (sebelum proses finalisasi pesanan)
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Keranjang Anda kosong. Silakan tambahkan produk terlebih dahulu.")
        return redirect('shop') # Redirect ke halaman shop jika keranjang kosong

    # Anda bisa menambahkan logika lain di sini sebelum menampilkan halaman checkout,
    # seperti validasi alamat pengiriman, metode pembayaran, dll.

    return render(request, 'checkout.html', {'cart': cart, 'cart_items': cart_items})


def contact(request):
    return render(request, 'contact-us.html')

def gallery(request):
    return render(request, 'gallery.html')

# View untuk halaman My Account (menampilkan riwayat pesanan)
@login_required
def my_account(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my-account.html', {'orders': orders})

def shop_detail(request):
    return render(request, 'shop-detail.html')

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
            return redirect('login') # Menggunakan 'login' yang sudah ada
        else:
            messages.error(request, "Terjadi kesalahan saat registrasi. Mohon periksa kembali input Anda.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "Anda telah berhasil logout.")
    return redirect('index')


# --- Views Keranjang dan Transaksi (Fungsi Baru/Diperbarui) ---

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not item_created:
        # Tambahkan validasi stok di sini juga
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Kuantitas '{product.name}' di keranjang diperbarui menjadi {cart_item.quantity}.")
        else:
            messages.warning(request, f"Stok maksimum untuk '{product.name}' telah tercapai.")
    else:
        messages.success(request, f"'{product.name}' telah ditambahkan ke keranjang Anda.")

    return redirect('shop') # Redirect ke halaman shop setelah menambahkan

# GANTI FUNGSI update_cart LAMA DENGAN INI (AJAX-based)
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

            # Validasi sisi server untuk stok dan kuantitas minimum
            if new_quantity < 1:
                new_quantity = 1
            if new_quantity > product.stock:
                new_quantity = product.stock

            # Jika kuantitas 0, hapus item (karena kita set minimum 1 di atas, ini untuk memastikan)
            if new_quantity == 0:
                cart_item.delete()
                # Langsung kembalikan sukses jika dihapus
                cart = cart_item.cart # Dapatkan kembali keranjang setelah item dihapus
                return JsonResponse({
                    'success': True,
                    'new_quantity': 0, # Atau menunjukkan item dihapus
                    'new_item_total': 0,
                    'cart_total_price': f"{cart.get_total_price():.0f}" # Format di sini
                })
            
            # Jika kuantitas tidak berubah, tidak perlu update DB
            if cart_item.quantity == new_quantity:
                return JsonResponse({
                    'success': True,
                    'new_quantity': new_quantity,
                    'new_item_total': f"{cart_item.get_total_item_price():.0f}",
                    'cart_total_price': f"{cart_item.cart.get_total_price():.0f}"
                })

            with transaction.atomic(): # Memastikan operasi database atomik
                cart_item.quantity = new_quantity
                cart_item.save()

                cart = cart_item.cart # Dapatkan kembali objek cart setelah save
                cart_total_price = cart.get_total_price()
                item_total_price = cart_item.get_total_item_price()

            # Mengirim kembali harga yang sudah diformat ke client
            return JsonResponse({
                'success': True,
                'new_quantity': new_quantity,
                'new_item_total': f"{item_total_price:.0f}", # Format sebagai integer string
                'cart_total_price': f"{cart_total_price:.0f}" # Format sebagai integer string
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item keranjang tidak ditemukan.'}, status=404)
        except Product.DoesNotExist:
             return JsonResponse({'success': False, 'error': 'Produk tidak ditemukan.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Terjadi kesalahan server: {str(e)}'}, status=500)
            
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


@login_required
def remove_from_cart(request, item_id): # Ini adalah fungsi untuk menghapus item via form submit
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, "Item telah dihapus dari keranjang Anda.")
    return redirect('cart_view')

@login_required
def checkout_process(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Keranjang Anda kosong. Tidak dapat melanjutkan checkout.")
        return redirect('shop')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user)
                for item in cart_items:
                    # Validasi stok final sebelum membuat OrderItem
                    if item.product.stock >= item.quantity:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price # Simpan harga produk saat dipesan
                        )
                        # Kurangi stok produk
                        item.product.stock -= item.quantity
                        item.product.save()
                    else:
                        # Jika stok tidak cukup, batalkan seluruh transaksi dan beri pesan error
                        messages.error(request, f"Stok tidak mencukupi untuk '{item.product.name}'. Silakan sesuaikan kuantitas di keranjang.")
                        raise Exception("Stok tidak mencukupi") # Akan ditangkap oleh try-except
                
                cart_items.delete() # Kosongkan keranjang setelah pesanan berhasil dibuat
                messages.success(request, f"Pesanan Anda (ID: {order.id}) telah berhasil dibuat!")
                return redirect('my_account') # Redirect ke halaman riwayat pesanan
        except Exception as e:
            # Jika ada error saat transaksi (misal stok tidak cukup), redirect ke keranjang
            return redirect('cart_view')
            
    # Jika method GET (akses halaman checkout langsung tanpa POST)
    return render(request, 'checkout.html', {'cart': cart, 'cart_items': cart_items})
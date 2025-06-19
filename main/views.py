# main/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product
# Import model-model yang baru kita definisikan
from .models import Product, Cart, CartItem, Order, OrderItem

# Import form kustom kita dari main/forms.py
from .forms import CustomUserCreationForm, CustomAuthenticationForm


# --- Views Halaman Statis (Diperbarui untuk mendukung fungsionalitas e-commerce) ---

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
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
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
    # Jika Anda ingin menampilkan detail produk tertentu, Anda akan membutuhkan product_id
    # Misalnya: def shop_detail(request, product_id):
    #    product = get_object_or_404(Product, id=product_id)
    #    return render(request, 'shop-detail.html', {'product': product})
    return render(request, 'shop-detail.html')

def wishlist(request):
    return render(request, 'wishlist.html')


# --- Views Otentikasi (Tidak berubah dari sebelumnya) ---

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
            return redirect('login_page') # Pastikan ini redirect ke halaman login
        else:
            messages.error(request, "Terjadi kesalahan saat registrasi. Mohon periksa kembali input Anda.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "Anda telah berhasil logout.")
    return redirect('index')


# --- Views Keranjang dan Transaksi (Fungsi Baru) ---

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
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Kuantitas '{product.name}' di keranjang diperbarui menjadi {cart_item.quantity}.")
    else:
        messages.success(request, f"'{product.name}' telah ditambahkan ke keranjang Anda.")

    return redirect('shop') # Redirect ke halaman shop setelah menambahkan

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        try:
            new_quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Kuantitas tidak valid.")
            return redirect('cart_view')

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, "Kuantitas item di keranjang diperbarui.")
        else: # Jika kuantitas 0 atau kurang, hapus item
            cart_item.delete()
            messages.info(request, "Item telah dihapus dari keranjang.")
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
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
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            # Periksa stok sebelum membuat OrderItem
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
                messages.error(request, f"Stok tidak mencukupi untuk '{item.product.name}'. Silakan sesuaikan kuantitas.")
                order.delete() # Hapus order yang baru dibuat jika ada masalah stok
                return redirect('cart_view')

        cart_items.delete() # Kosongkan keranjang setelah pesanan berhasil dibuat
        messages.success(request, f"Pesanan Anda (ID: {order.id}) telah berhasil dibuat!")
        return redirect('my_account') # Redirect ke halaman riwayat pesanan
    
    # Jika method GET (akses halaman checkout langsung tanpa POST)
    return render(request, 'checkout.html', {'cart': cart, 'cart_items': cart_items})
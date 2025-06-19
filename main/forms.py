# main/forms.py

from django import forms
from django.contrib.auth.models import User # Tetap butuh User untuk create_user
from django.contrib.auth.forms import AuthenticationForm # Tetap gunakan ini untuk login
# from .models import UserProfile # Hapus import ini

class CustomUserCreationForm(forms.Form): # Meng-extend forms.Form
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nama Pengguna",
        help_text="Nama pengguna harus unik dan tidak terlalu panjang.",
        widget=forms.TextInput(attrs={'placeholder': 'Masukkan nama pengguna Anda'})
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Masukkan email pengguna Anda'})
    )
    # no_hp DIHAPUS karena tidak ada lagi tempat untuk menyimpannya di User bawaan

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Masukkan kata sandi Anda'}),
        label="Kata Sandi",
        help_text="Kata sandi minimal 6 karakter. Tidak ada persyaratan khusus lainnya.",
        required=True
    )

    # --- Validasi Kustom ---
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Nama pengguna ini sudah digunakan. Mohon pilih nama lain.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email ini sudah terdaftar.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("Kata sandi minimal harus 6 karakter.")
        return password

    def save(self, commit=True):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        # no_hp tidak lagi diambil dari cleaned_data

        # Membuat user baru. UserProfile tidak terlibat lagi.
        user = User.objects.create_user(username=username, email=email, password=password)

        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    # Tidak ada perubahan di sini
    pass
# main/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile # Import UserProfile yang sudah ada di models.py

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nama Pengguna",
        help_text="Nama pengguna harus unik dan tidak terlalu panjang.",
        widget=forms.TextInput(attrs={'placeholder': 'Masukkan nama pengguna Anda', 'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Masukkan email pengguna Anda', 'class': 'form-control'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Masukkan kata sandi Anda', 'class': 'form-control'}),
        label="Kata Sandi",
        help_text="Kata sandi minimal 6 karakter. Tidak ada persyaratan khusus lainnya.",
        required=True
    )

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

        user = User.objects.create_user(username=username, email=email, password=password)

        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    # Tidak ada perubahan di sini
    pass

# --- FORM BARU UNTUK MENGEDIT NAMA DEPAN/PELANGGAN PADA MODEL USER ---
class UserUpdateForm(forms.ModelForm):
    # Menggunakan first_name sebagai 'Nama Pelanggan'
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nama Pelanggan",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Pelanggan'})
    )

    class Meta:
        model = User
        fields = ['first_name'] # Hanya mengelola first_name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Menghapus field yang tidak relevan agar tidak dirender atau diproses
        if 'last_name' in self.fields:
            del self.fields['last_name']
        if 'email' in self.fields:
            del self.fields['email']

# --- FORM BARU UNTUK MENGEDIT NOMOR TELEPON PADA MODEL USERPROFILE ---
class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=20, # Sesuaikan dengan max_length di models.py
        required=False, # Nomor telepon bisa kosong
        label="Nomor Telepon",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 081234567890'})
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number'] # Hanya mengelola phone_number

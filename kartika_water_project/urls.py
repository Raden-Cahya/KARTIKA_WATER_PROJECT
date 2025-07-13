"""
URL configuration for kartika_water_project project.
...
"""
from django.contrib import admin
from django.urls import path, include
from main import views # Pastikan ini tetap ada untuk views otentikasi kustom Anda

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Mengarahkan semua URL yang tidak cocok di sini ke main/urls.py
    path('', include('main.urls')),
    
    path('admin/', admin.site.urls),

    # URL Autentikasi Kustom Anda
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login_page'), # Tetap 'login_page' agar konsisten dengan template
    path('logout/', views.user_logout, name='logout'),

    # URL Autentikasi Bawaan Django (INI YANG HARUS DITAMBAHKAN)
    # Ini akan menyediakan URL seperti /accounts/password_reset/, /accounts/password_reset/done/, dll.
    # Jika Anda ingin mengubah prefix '/accounts/', Anda bisa mengubahnya.
    # path('accounts/', include('django.contrib.auth.urls')), 
]

# Baris-baris ini untuk melayani file media dan static saat DEBUG = True
# HANYA digunakan selama pengembangan, jangan di deployment production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

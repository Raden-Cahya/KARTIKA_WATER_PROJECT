"""
URL configuration for kartika_water_project project.
...
"""
from django.contrib import admin
from django.urls import path, include
from main import views # Pastikan ini tetap ada untuk views otentikasi

from django.conf import settings # Tambahkan ini
from django.conf.urls.static import static # Tambahkan ini

urlpatterns = [
    # Mengarahkan semua URL yang tidak cocok di sini ke main/urls.py
    # Jadi, 'shop/', 'cart/', 'about/', 'index/', dll. akan ditangani oleh main.urls
    path('', include('main.urls')),
    
    path('admin/', admin.site.urls),

    # URL Otentikasi (Bisa tetap di sini atau pindah ke main.urls jika mau)
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'), # Pastikan nama 'login' konsisten
    path('logout/', views.user_logout, name='logout'),
]

# Baris-baris ini untuk melayani file media dan static saat DEBUG = True
# HANYA digunakan selama pengembangan, jangan di deployment production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Ini juga membantu memastikan statis dilayani
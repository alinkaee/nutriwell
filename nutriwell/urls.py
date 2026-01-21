from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('clients/', include('clients.urls')),
    path('nutritionist/', include('nutritionists.urls')),
    path('programs/', include('programs.urls')),
    path('diaries/', include('diaries.urls')),
    path('products/', include('products.urls')),
    path('consultations/', include('consultations.urls')),
    path('chat/', include('chat.urls')),
    path('', include('core.urls'))
]
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import home

# Только админка и системные вещи без языка
urlpatterns = [
    path('admin/', admin.site.urls),
]

# ВСЕ остальные пути, включая эндпоинт смены языка, ОБЯЗАНЫ быть внутри i18n_patterns
urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),  # <--- ПЕРЕНЕСЛИ СЮДА
    path('', home, name='home'),
    path('', include('accounts.urls')),
    path('', include('challenges.urls')),
    path('', include('ecomap.urls')),
    prefix_default_language=False,
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
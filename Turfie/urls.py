from django.contrib import admin
from django.urls import path, include
from Users import views  # ✅ Import views to directly use the landing view
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('Users.urls')),  # All URLs under /users/
    path('', views.landing, name='landing'),  # ✅ This makes http://127.0.0.1:8000/ work
    path('turfs/', include('Turfs.urls')),  # All URLs under /turfs/
    path('management/', include ('management.urls'))
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve media files in development

#  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # Serve static files in development
 
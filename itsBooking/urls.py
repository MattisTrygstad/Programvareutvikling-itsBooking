from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from itsBooking.views import Home, populate_db, LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', Home.as_view(), name='home'),
    path('populate/', populate_db, name='populate'),
    path('admin/', admin.site.urls),
    path('booking/', include('booking.urls'))
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

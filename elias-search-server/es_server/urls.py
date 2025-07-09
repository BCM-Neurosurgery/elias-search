"""
URL configuration for es_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import ssh_auth, auth_status, auth_logout, query_db, get_formdata

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/', ssh_auth),
    path('auth/status/', auth_status),
    path('auth/logout/', auth_logout),
    path('query/db', query_db),
    path('query/formdata', get_formdata)
]

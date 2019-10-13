"""wpo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import wpo_admin.views as wpo_admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uploads/', wpo_admin_views.uploads),
    path('employee_upload/', wpo_admin_views.employee_upload),
    path('view_employees/', wpo_admin_views.view_employees),
    path('get_employee_data/', wpo_admin_views.get_employee_data),
]

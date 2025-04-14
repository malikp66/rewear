"""
URL configuration for be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.http import JsonResponse
from django.urls import get_resolver

def list_urls(request):
    url_patterns = get_resolver().url_patterns
    url_list = []

    def extract_urls(patterns, prefix=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                extract_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            elif hasattr(pattern, 'pattern'):
                url = prefix + str(pattern.pattern)
                url_list.append(url.replace('^', '').replace('$', ''))

    extract_urls(url_patterns)
    return JsonResponse({'available_urls': url_list})

urlpatterns = [
    # path('', list_urls, name='url_list'),
    path("admin/", admin.site.urls),
    path("authentification/", include("authentification.urls")),
    path("api/", include("thrift.urls")),
]
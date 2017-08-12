"""chain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from ise import views as ise_views

urlpatterns = [
    url(r'^$', ise_views.index, name='index'),
    url(r'^register/', ise_views.register, name='register'),
    url(r'^showinfo/', ise_views.showinfo, name='showinfo'),
    url(r'^changepass/', ise_views.changepass, name='changepass'),
    url(r'^setsafepass/', ise_views.setsafepass, name='setsafepass'),
    url(r'^checkmail/', ise_views.checkmail, name='checkmail'),
    url(r'^addaddress/', ise_views.addaddress, name='addaddress'),
    url(r'^tibi/', ise_views.tibi, name='tibi'),
    url(r'^canceltibi/(\d+)/$', ise_views.canceltibi, name='canceltibi'),
    url(r'^sendcode/', ise_views.sendcode, name='sendcode'),
    url(r'^activate/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', ise_views.active_user, name='active_user'),
    url(r'^test/', ise_views.test, name='test'),
    url(r'^bitcoinrpc/', ise_views.bitcoinrpc, name='bitcoinrpc'),
    url(r'^login/', ise_views.login, name='login'),
    url(r'^logout/', ise_views.logout, name='logout'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', admin.site.urls),
]

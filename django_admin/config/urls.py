from django.contrib import admin
from django.urls import path

admin.site.site_header = "ByteDesk administration"
admin.site.site_title = "ByteDesk Admin"
admin.site.index_title = "Store management"
urlpatterns = [path("admin/", admin.site.urls)]

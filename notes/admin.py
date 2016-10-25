from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_header = 'Notes administration'
    site_title = 'Notes site admin'


site = AdminSite()

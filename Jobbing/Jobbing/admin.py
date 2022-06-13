from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group

from .models import Category, WorkingTime, ContractType, Offer, StandardUser, CompanyUser, AppConf

# Register your models here.


admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.site_header = 'Jobbing - Admin Panel'


class StandardUserInline(admin.StackedInline):
    model = StandardUser
    can_delete = True
    verbose_name_plural = 'Standard User'


class CompanyUserInline(admin.StackedInline):
    model = CompanyUser
    can_delete = True
    verbose_name_plural = 'Company User'


class MyAdminCategory(admin.ModelAdmin):
    exclude = ('count',)


class MyAdmin(admin.ModelAdmin):
    readonly_fields = ('conf_key',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserAdmin(BaseUserAdmin):
    inlines = (StandardUserInline, CompanyUserInline, )


admin.site.register(AppConf, MyAdmin)
admin.site.register(Category, MyAdminCategory)
admin.site.register(WorkingTime)
admin.site.register(ContractType)
admin.site.register(Offer)
admin.site.register(User, UserAdmin)
#admin.site.register(AppConf)
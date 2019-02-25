from pprint import pprint

from django import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group

admin.site.unregister(User)
admin.site.unregister(Group)


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('is_staff', 'is_superuser', 'password', 'last_login', 'date_joined')

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['groups'] = forms.ChoiceField(
            choices=form.base_fields['groups'].choices,
            label='Group',
        )
        return form


admin.site.register(User, UserAdmin)
admin.site.register(Group)

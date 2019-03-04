from django import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group

admin.site.unregister(User)
admin.site.unregister(Group)


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('is_staff', 'is_superuser', 'last_login', 'date_joined')

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)

        choices = list(form.base_fields['groups'].choices)
        if obj is not None:
            usr_group = (obj.groups.first().id, str(obj.groups.first()))
            del choices[choices.index(usr_group)]
            choices.append(usr_group)

        form.base_fields['groups'] = forms.ChoiceField(
            choices=reversed(choices),
            label='Gruppe',
        )
        return form


admin.site.register(User, UserAdmin)
admin.site.register(Group)

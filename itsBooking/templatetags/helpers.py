import calendar

from django import template

register = template.Library()


@register.filter(name='in_group')
def user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='nob_day')
def get_norwegian_day_name(day):
    nob_days = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag']
    translation = dict(zip(calendar.day_name, nob_days))
    return translation.get(day, None)

from django import forms
from django.contrib.auth.models import User

from booking.models import BookingInterval


class ReservationForm(forms.Form):
    reservation_index = forms.IntegerField(widget=forms.HiddenInput())
    booking_interval_nk = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        index = self.cleaned_data['reservation_index']
        bi = BookingInterval.objects.get(nk=self.cleaned_data['booking_interval_nk'])
        reserved_assistants = User.objects.filter(bookings__index=index)
        bi_assistants = bi.assistants.all()
        available_assistants = bi_assistants.difference(reserved_assistants)  # all assistants minus reserved ones
        if available_assistants.count() <= 0:
            raise forms.ValidationError('No assistants available for this reservation interval')

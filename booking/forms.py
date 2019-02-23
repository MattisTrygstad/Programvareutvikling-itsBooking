from django import forms


class ReservationForm(forms.Form):
    reservation_index = forms.IntegerField(widget=forms.HiddenInput())
    booking_interval_nk = forms.CharField(widget=forms.HiddenInput())

from django import forms

from assignments.models import Exercise


class ExerciseReviewForm(forms.ModelForm):

    def __init__(self):
        super().__init__()
        self.fields['id'] = forms.IntegerField()
        self.fields['id'].widget = forms.HiddenInput()

        self.fields['review_text'].widget.attrs['class'] = 'uk-form uk-textarea uk-form-small'
        self.fields['approved'].widget = forms.RadioSelect(
            choices=[
                (True, 'Godkjenn'),
                (False, 'Underkjenn')
            ],
            attrs={'class': 'uk-radio'}
        )

    class Meta:
        model = Exercise
        fields = ('review_text', 'approved', )


from django import forms

from assignments.models import Exercise


class ExerciseReviewForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['review_text'].widget.attrs['class'] = 'uk-form uk-textarea uk-form-small'
        self.fields['approved'].widget = forms.RadioSelect(
            choices=[
                (True, 'Godkjenn'),
                (False, 'Underkjenn')
            ],
            attrs={'class': 'uk-radio'},
        )
        self.fields['approved'].required = True

    class Meta:
        model = Exercise
        fields = ('review_text', 'approved', )


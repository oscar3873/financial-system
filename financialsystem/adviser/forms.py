from django import forms

class PorcentageUpdate(forms.Form):
    porcentage = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=0
    )

    def __init__(self, porcentage, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['porcentage'].initial = porcentage
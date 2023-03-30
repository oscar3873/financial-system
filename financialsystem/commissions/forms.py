from django import forms

from commissions.models import Interest

class SettingsInterestForm(forms.ModelForm):

    interest_credit = forms.DecimalField(
        label="Interes general para creditos"
    )

    interest_register = forms.DecimalField(
        label="Porcentaje de comision por registros"
    )

    interest_payment = forms.DecimalField(
        label="Porcentaje de comision por pagos"
    )

    interest_sell = forms.DecimalField(
        label="Porcentaje de comision por ventas"
    )

    points_score_refinancing = forms.DecimalField(
        label="Puntaje/Score por pago de refinanciacion"
    )

    points_score_credits = forms.DecimalField(
        label="Puntaje/Score por pago de creditos"
    )

    daily_interest = forms.DecimalField(
        label="Puntaje a disminuir por interes diario"
    )

    porcentage_daily_interest = forms.DecimalField(
        label="Porcentaje de interes por retraso diario"
    )

    class Meta:
        model = Interest
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        # Eliminar validación requerida
        for field in self.fields.values():
            field.required = True

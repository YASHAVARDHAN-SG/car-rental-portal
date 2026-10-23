from datetime import date

from django import forms


class BookingForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()})
    )
    pickup_location = forms.CharField(max_length=200)
    dropoff_location = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and start < date.today():
            self.add_error('start_date', 'The start date cannot be in the past.')
        if start and end and end < start:
            self.add_error('end_date', 'The end date must be on or after the start date.')

        return cleaned_data

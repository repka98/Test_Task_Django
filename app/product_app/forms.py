from django import forms
from django.forms import DateInput
from .models import StatusBook

class UploadFileForm(forms.Form):
    """
    Форма загрузки файла
    """
    title = forms.CharField(label='Title', max_length=100)
    file = forms.FileField(label='File')


class DateOrder(forms.Form):
    """
    Форма для выбора даты

    """
    date_start = forms.DateField(label='Выбор даты начала периода', widget=DateInput(attrs={'type': 'date'}))
    date_end = forms.DateField(label='Выбор даты окончания периода', widget=DateInput(attrs={'type': 'date'}))
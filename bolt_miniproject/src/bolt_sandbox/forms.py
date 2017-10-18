from django import forms

class ChangeTitleForm(forms.Form):
    title = forms.CharField(label='Условие',
                            required=True,
                            widget=forms.Textarea(
        attrs={'rows':7, 'class':'form-control', 'placeholder':'Введите условие задачи'}
    ))
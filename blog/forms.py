from django import forms
from blog.models import Contacto



class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        exclude = ('estado',)

        widgets = {
            'nombre':forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Please enter your name.',
                }
            ),
            'correo':forms.EmailInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Please enter your email address.',
                }
            ),
            'asunto':forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Please enter the subject',
                }
            ),
            'mensaje':forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Please enter your message',
                }
            ),
        }
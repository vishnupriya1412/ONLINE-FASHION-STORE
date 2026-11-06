from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'name',
            'category',
            'description',
            'price',
            'stock',
            'image_url'
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'description': forms.Textarea(
                attrs={'class': 'form-control'}
            ),

            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0.01'}
            ),

            'stock': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),

            'image_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter product image URL'
                }
            ),
        }
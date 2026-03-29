from django import forms
from .models import Problem
from django.core.validators import MinValueValidator, MaxValueValidator

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'correct_answer', 'difficulty']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Вычисление интеграла'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Условие задачи...'
            }),
            'correct_answer': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Введите число'
            }),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Название задачи',
            'description': 'Условие',
            'correct_answer': 'Правильный ответ (число)',
            'difficulty': 'Сложность',
        }
    
    def clean_correct_answer(self):
        answer = self.cleaned_data['correct_answer']
        if answer < -1000000 or answer > 1000000:
            raise forms.ValidationError('Ответ должен быть в диапазоне от -1,000,000 до 1,000,000')
        return answer

class AnswerForm(forms.Form):
    user_answer = forms.FloatField(
        label='Ваш ответ',
        validators=[MinValueValidator(-1000000), MaxValueValidator(1000000)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 'any',
            'placeholder': 'Введите число'
        })
    )
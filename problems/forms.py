from django import forms
from .models import Problem, Tag
from django.core.validators import MinValueValidator, MaxValueValidator

class ProblemForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label='Tags',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by space or comma...'
        })
    )

    class Meta:
        model = Problem
        fields = ['title', 'description', 'correct_answer', 'tolerance', 'difficulty']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Calculate the integral'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Problem description...'
            }),
            'correct_answer': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Enter a number'
            }),
            'tolerance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'e.g. 0.01'
            }),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Problem Title',
            'description': 'Description',
            'correct_answer': 'Correct Answer (Number)',
            'tolerance': 'Tolerance (margin of error)',
            'difficulty': 'Difficulty',
        }
    
    def clean_correct_answer(self):
        answer = self.cleaned_data['correct_answer']
        if answer < -1000000 or answer > 1000000:
            raise forms.ValidationError('Answer must be between -1,000,000 and 1,000,000')
        return answer

class AnswerForm(forms.Form):
    user_answer = forms.FloatField(
        label='Your Answer',
        validators=[MinValueValidator(-1000000), MaxValueValidator(1000000)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 'any',
            'placeholder': 'Enter a number'
        })
    )
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкая'),
        ('medium', 'Средняя'),
        ('hard', 'Сложная'),
    ]
    
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Условие задачи')
    correct_answer = models.FloatField(
        'Правильный ответ',
        validators=[MinValueValidator(-1000000), MaxValueValidator(1000000)]
    )
    difficulty = models.CharField(
        'Сложность',
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('problems:problem_detail', args=[str(self.id)])

class Attempt(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Задача'
    )
    user_answer = models.FloatField('Ответ пользователя')
    is_correct = models.BooleanField('Правильно?', default=False)
    timestamp = models.DateTimeField('Время попытки', auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'
    
    def __str__(self):
        return f"{self.problem.title} - {'✓' if self.is_correct else '✗'}"
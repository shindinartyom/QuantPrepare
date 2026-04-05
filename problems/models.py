from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField('Theme Name', max_length=50, unique=True)
    
    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'
        
    def __str__(self):
        return self.name

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField('Title', max_length=200)
    description = models.TextField('Problem Description')
    correct_answer = models.FloatField(
        'Correct Answer',
        validators=[MinValueValidator(-1000000), MaxValueValidator(1000000)]
    )
    difficulty = models.CharField(
        'Difficulty',
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    tolerance = models.FloatField(
        'Tolerance (margin of error)',
        default=0.0,
        help_text="Allowed difference for float numerical answers"
    )
    created_at = models.DateTimeField('Creation Date', auto_now_add=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='problems', 
        verbose_name='Author'
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Themes')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Problem'
        verbose_name_plural = 'Problems'
    
    def __str__(self):
        return str(self.title)
    
    def get_absolute_url(self):
        return reverse('problems:problem_detail', args=[str(self.id)])
        
    @property
    def success_rate(self):
        total = self.attempts.count()
        if total == 0:
            return 0
        correct = self.attempts.filter(is_correct=True).count()
        return round((correct / total) * 100, 1)

class Attempt(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Problem'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='User'
    )
    user_answer = models.CharField('User Answer', max_length=100)
    is_correct = models.BooleanField('Is correct?', default=False)
    timestamp = models.DateTimeField('Attempt Timestamp', auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Attempt'
        verbose_name_plural = 'Attempts'
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {'✓' if self.is_correct else '✗'}"
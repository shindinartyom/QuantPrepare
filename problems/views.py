from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from .models import Problem, Attempt
from .forms import ProblemForm, AnswerForm

class IndexView(TemplateView):
    template_name = 'problems/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_problems'] = Problem.objects.count()
        context['total_attempts'] = Attempt.objects.count()
        
        correct_attempts = Attempt.objects.filter(is_correct=True).count()
        if context['total_attempts'] > 0:
            context['success_rate'] = round(correct_attempts / context['total_attempts'] * 100, 1)
        else:
            context['success_rate'] = 0
        
        return context

class ProblemListView(ListView):
    model = Problem
    template_name = 'problems/problem_list.html'
    context_object_name = 'problems'
    paginate_by = 10

class ProblemDetailView(DetailView):
    model = Problem
    template_name = 'problems/problem_detail.html'
    context_object_name = 'problem'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AnswerForm()
        context['last_attempts'] = self.object.attempts.all()[:5]
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AnswerForm(request.POST)
        
        if form.is_valid():
            user_answer = form.cleaned_data['user_answer']
            is_correct = abs(user_answer - self.object.correct_answer) < 0.0001
            
            Attempt.objects.create(
                problem=self.object,
                user_answer=user_answer,
                is_correct=is_correct
            )
            
            if is_correct:
                messages.success(request, f'✅ Правильно! Ответ {user_answer} верный.')
            else:
                messages.warning(
                    request,
                    f'❌ Неверно. Правильный ответ: {self.object.correct_answer}'
                )
            
            return redirect('problems:problem_detail', pk=self.object.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

class ProblemCreateView(CreateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'problems/problem_form.html'
    success_url = reverse_lazy('problems:problem_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Задача "{form.instance.title}" успешно создана!')
        return super().form_valid(form)

class ProblemUpdateView(UpdateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'problems/problem_form.html'
    success_url = reverse_lazy('problems:problem_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Задача "{form.instance.title}" обновлена!')
        return super().form_valid(form)

class ProblemDeleteView(DeleteView):
    model = Problem
    template_name = 'problems/problem_confirm_delete.html'
    success_url = reverse_lazy('problems:problem_list')
    
    def delete(self, request, *args, **kwargs):
        problem = self.get_object()
        messages.success(request, f'Задача "{problem.title}" удалена!')
        return super().delete(request, *args, **kwargs)

class StatisticsView(TemplateView):
    template_name = 'problems/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        total_attempts = Attempt.objects.count()
        correct_attempts = Attempt.objects.filter(is_correct=True).count()
        
        context['total_attempts'] = total_attempts
        context['correct_attempts'] = correct_attempts
        context['accuracy'] = round(correct_attempts / total_attempts * 100, 1) if total_attempts > 0 else 0
        
        problems_stats = []
        for problem in Problem.objects.all():
            attempts = problem.attempts.all()
            total = attempts.count()
            correct = attempts.filter(is_correct=True).count()
            problems_stats.append({
                'problem': problem,
                'total_attempts': total,
                'correct_attempts': correct,
                'success_rate': round(correct / total * 100, 1) if total > 0 else 0,
            })
        
        context['problems_stats'] = problems_stats
        return context
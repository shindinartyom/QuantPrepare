from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic import TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from .models import Problem, Attempt, Tag
from .forms import ProblemForm, AnswerForm

def parse_fraction(s):
    s = str(s).strip()
    if '/' in s:
        parts = s.split('/')
        if len(parts) == 2:
            try:
                return float(parts[0]) / float(parts[1])
            except ValueError:
                return None
    try:
        return float(s)
    except ValueError:
        return None

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

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

class ProblemListView(LoginRequiredMixin, ListView):
    model = Problem
    template_name = 'problems/problem_list.html'
    context_object_name = 'problems'
    paginate_by = 10
    
    def get_queryset(self):
        qs = super().get_queryset()
        search_q = self.request.GET.get('search', '')
        difficulty_q = self.request.GET.get('difficulty', '')
        theme_q = self.request.GET.get('theme', '')
        
        if search_q:
            qs = qs.filter(title__icontains=search_q)
        if difficulty_q:
            qs = qs.filter(difficulty=difficulty_q)
        if theme_q:
            qs = qs.filter(tags__name__icontains=theme_q)
        return qs.distinct()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['difficulty'] = self.request.GET.get('difficulty', '')
        context['theme'] = self.request.GET.get('theme', '')
        return context

class ProblemDetailView(LoginRequiredMixin, DetailView):
    model = Problem
    template_name = 'problems/problem_detail.html'
    context_object_name = 'problem'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AnswerForm()
        context['last_attempts'] = self.object.attempts.filter(user=self.request.user)[:5]
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AnswerForm(request.POST)
        
        if form.is_valid():
            user_answer_str = form.cleaned_data['user_answer']
            numeric_val = parse_fraction(user_answer_str)
            
            if numeric_val is None:
                messages.error(request, 'Invalid input. Please enter a valid number or fraction.')
                return redirect('problems:problem_detail', pk=self.object.pk)
                
            is_correct = abs(numeric_val - self.object.correct_answer) <= self.object.tolerance
            
            Attempt.objects.create(
                problem=self.object,
                user=self.request.user,
                user_answer=user_answer_str,
                is_correct=is_correct
            )
            
            return redirect('problems:problem_detail', pk=self.object.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

class ProblemCreateView(LoginRequiredMixin, CreateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'problems/problem_form.html'
    success_url = reverse_lazy('problems:problem_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        tags_input = form.cleaned_data.get('tags_input', '')
        if tags_input:
            raw_tags = [t.strip() for t in tags_input.split(',')]
            for t in raw_tags:
                tag_name = t.lower()
                if tag_name:
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    self.object.tags.add(tag_obj)
        return response

class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'problems/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_q = self.request.GET.get('search', '')
        difficulty_q = self.request.GET.get('difficulty', '')
        tag_q = self.request.GET.get('theme', '')
        
        user_attempts = Attempt.objects.filter(user=self.request.user)
        
        if search_q:
            user_attempts = user_attempts.filter(problem__title__icontains=search_q)
        if difficulty_q:
            user_attempts = user_attempts.filter(problem__difficulty=difficulty_q)
        if tag_q:
            user_attempts = user_attempts.filter(problem__tags__name__icontains=tag_q)
        
        total_attempts = user_attempts.count()
        correct_attempts = user_attempts.filter(is_correct=True).count()
        
        context['total_attempts'] = total_attempts
        context['correct_attempts'] = correct_attempts
        context['accuracy'] = round(correct_attempts / total_attempts * 100, 1) if total_attempts > 0 else 0
        
        context['recent_attempts'] = user_attempts.order_by('-timestamp')[:50]
        context['search'] = search_q
        context['difficulty'] = difficulty_q
        context['theme'] = tag_q
        
        return context

class ProblemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'problems/problem_form.html'
    
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('problems:problem_detail', kwargs={'pk': self.object.pk})
    
    def get_initial(self):
        initial = super().get_initial()
        initial['tags_input'] = ",".join([t.name for t in self.object.tags.all()])
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        tags_input = form.cleaned_data.get('tags_input', '')
        self.object.tags.clear()
        if tags_input:
            raw_tags = [t.strip() for t in tags_input.split(',')]
            for t in raw_tags:
                tag_name = t.lower()
                if tag_name:
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    self.object.tags.add(tag_obj)
        return response

class ProblemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Problem
    template_name = 'problems/problem_confirm_delete.html'
    success_url = reverse_lazy('problems:problem_list')

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
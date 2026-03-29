from django.urls import path
from . import views

app_name = 'problems'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('problems/', views.ProblemListView.as_view(), name='problem_list'),
    path('problem/<int:pk>/', views.ProblemDetailView.as_view(), name='problem_detail'),
    path('problem/create/', views.ProblemCreateView.as_view(), name='problem_create'),
    path('problem/<int:pk>/update/', views.ProblemUpdateView.as_view(), name='problem_update'),
    path('problem/<int:pk>/delete/', views.ProblemDeleteView.as_view(), name='problem_delete'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]
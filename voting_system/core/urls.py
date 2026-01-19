from django.urls import path
from . import views
from .views import profile_view
from .views import custom_logout

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('vote/', views.vote_view, name='vote'),
    path('results/', views.results, name='results'),
    path('profile/', profile_view, name='profile'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('already-voted/', views.already_voted, name='already_voted'),
    path('admin/vote-history/', views.vote_history, name='vote_history'),
    path('ajax/vote-data/', views.ajax_vote_data, name='ajax_vote_data'),
    path('api/vote-data/', views.api_vote_data, name='api_vote_data'),
    path('register/', views.register_view, name='register'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('toggle-voting/', views.toggle_voting, name='toggle_voting'),
]

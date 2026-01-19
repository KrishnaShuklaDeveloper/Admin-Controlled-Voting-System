from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.template.loader import get_template
from django.templatetags.static import static
from django.db.models import Count
from django.contrib.auth.models import User
from .models import Candidate, Vote, VotingStatus, VoteLog, Profile
from .forms import CustomUserCreationForm, ProfileUpdateForm, ProfileImageForm

import openpyxl
from xhtml2pdf import pisa


# ================== Helpers ==================

def is_admin(user):
    return user.is_superuser


# ================== Home & Auth ==================

def home(request):
    context = {}

    if request.user.is_authenticated:
        context['total_users'] = User.objects.count()
        context['total_votes'] = Vote.objects.count()
        context['voting_status'] = VotingStatus.objects.first()
        context['recent_votes'] = Vote.objects.select_related('user', 'candidate').order_by('-timestamp')[:5]

    return render(request, 'core/templates/core/home.html', context)


def register(request):
    return render(request, 'core/templates/core/register.html')


def custom_logout(request):
    logout(request)
    return redirect('home')


# ================== Registration ==================

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # create blank profile
            login(request, user)
            return redirect('vote')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/templates/core/register.html', {'form': form})


# ================== Profile ==================

@login_required
def profile_view(request):
    vote = Vote.objects.filter(user=request.user).select_related('candidate').first()
    profile = Profile.objects.get_or_create(user=request.user)[0]

    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=request.user)
        image_form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and image_form.is_valid():
            user_form.save()
            image_form.save()
            messages.success(request, "✅ Profile updated successfully.")
            return redirect('profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        image_form = ProfileImageForm(instance=profile)

    return render(request, 'core/templates/core/profile.html', {
        'vote': vote,
        'user_form': user_form,
        'image_form': image_form,
        'profile': profile,
    })


# ================== Voting ==================

@login_required
def vote_view(request):
    status = VotingStatus.objects.first()
    if not status or not status.is_open:
        messages.error(request, "⚠️ Voting is currently closed.")
        return redirect('dashboard')

    if Vote.objects.filter(user=request.user).exists():
        messages.warning(request, "❗ You have already voted.")
        return redirect('dashboard')

    candidates = Candidate.objects.all()

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        if candidate_id:
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                Vote.objects.create(user=request.user, candidate=candidate)
                VoteLog.objects.create(user=request.user)
                messages.success(request, "✅ Your vote has been submitted!")
                return redirect('dashboard')
            except Candidate.DoesNotExist:
                messages.error(request, "❌ Invalid candidate selected.")
        else:
            messages.error(request, "⚠️ Please select a candidate before submitting.")

    return render(request, 'core/templates/core/vote.html', {'candidates': candidates})


# ================== Dashboard ==================

@login_required
def dashboard_view(request):
    candidates = Candidate.objects.all()
    vote_data = {
        candidate.name: Vote.objects.filter(candidate=candidate).count()
        for candidate in candidates
    }

    context = {
        'candidates': candidates,
        'vote_data': vote_data,
        'total_votes': Vote.objects.count(),
        'total_users': User.objects.count(),
        'voting_status': VotingStatus.objects.first(),
    }

    return render(request, 'core/templates/core/admin_dashboard.html', context)


@user_passes_test(is_admin)
def ajax_vote_data(request):
    candidates = Candidate.objects.all()
    vote_data = {
        candidate.name: Vote.objects.filter(candidate=candidate).count()
        for candidate in candidates
    }
    total_votes = Vote.objects.count()
    return JsonResponse({'vote_data': vote_data, 'total_votes': total_votes})


@login_required
def api_vote_data(request):
    candidates = Candidate.objects.all()

    vote_data = {
        candidate.name: Vote.objects.filter(candidate=candidate).count()
        for candidate in candidates
    }

    candidate_list = [
        {
            'name': candidate.name,
            'votes': Vote.objects.filter(candidate=candidate).count(),
            'image_url': candidate.image.url if candidate.image else static('images/no-image.png')
        }
        for candidate in candidates
    ]

    total_votes = Vote.objects.count()

    return JsonResponse({
        'vote_data': vote_data,
        'total_votes': total_votes,
        'candidates': candidate_list
    })


# ================== Results ==================

def results(request):
    candidates = Candidate.objects.annotate(vote_count=Count('vote'))
    total_votes = sum(c.vote_count for c in candidates)
    max_votes = max((c.vote_count for c in candidates), default=0)

    for candidate in candidates:
        candidate.percentage = round((candidate.vote_count / total_votes) * 100, 2) if total_votes > 0 else 0

    return render(request, 'core/templates/core/results.html', {
        'candidates': candidates,
        'total_votes': total_votes,
        'max_votes': max_votes,
    })


# ================== Voting History ==================

@login_required
def vote_history(request):
    vote = Vote.objects.filter(user=request.user).select_related('candidate').first()
    return render(request, 'core/templates/core/vote_history.html', {'vote': vote})


# ================== Static Pages ==================

def thank_you(request):
    return render(request, 'thanks.html')


def already_voted(request):
    return render(request, 'already_voted.html')


# ================== Admin Controls ==================

@user_passes_test(is_admin)
def toggle_voting(request):
    status = VotingStatus.objects.first()
    if status:
        status.is_open = not status.is_open
        status.save()
    else:
        VotingStatus.objects.create(is_open=False)
    return redirect('dashboard')


@user_passes_test(is_admin)
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vote Logs"
    ws.append(['Username', 'Candidate', 'Timestamp'])

    for vote in Vote.objects.select_related('user', 'candidate'):
        ws.append([vote.user.username, vote.candidate.name, vote.timestamp.strftime('%d-%m-%Y %H:%M')])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="vote_logs.xlsx"'
    wb.save(response)
    return response


@user_passes_test(is_admin)
def export_pdf(request):
    logs = Vote.objects.select_related('user', 'candidate')
    template = get_template('core/templates/core/pdf_template.html')
    html = template.render({'logs': logs})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vote_logs.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

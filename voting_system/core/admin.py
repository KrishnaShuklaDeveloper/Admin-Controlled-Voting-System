from django.contrib import admin
from .models import Candidate, Category, Vote, VotingStatus, VoteLog
from django.utils.html import format_html


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'category', 'created_at')
    list_filter = ('category',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(VotingStatus)
class VotingStatusAdmin(admin.ModelAdmin):
    list_display = ('is_open',)

class VotingStatusAdmin(admin.ModelAdmin):
    list_display = ('status_display',)

    def status_display(self, obj):
        color = 'green' if obj.is_open else 'red'
        text = "Voting is OPEN" if obj.is_open else "Voting is CLOSED"
        return format_html(f'<strong style="color: {color};">{text}</strong>')

    status_display.short_description = "Voting Status"

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'timestamp')


class VotingStatusAdmin(admin.ModelAdmin):
    list_display = ('is_open',)


@admin.register(VoteLog)
class VoteLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'voted_at')

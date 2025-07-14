from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Category for candidates (optional)
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Candidate model
class Candidate(models.Model):
    name = models.CharField(max_length=100)
    party = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='candidates/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.party})"


# Merged Voting Status model
class VotingStatus(models.Model):
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return "Voting is OPEN" if self.is_open else "Voting is CLOSED"

    class Meta:
        verbose_name = "Voting Status (Toggle)"
        verbose_name_plural = "Voting Status (Toggle)"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', default='default-avatar.png')

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Vote model – 1 vote per user
class Vote(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} voted for {self.candidate.name}"


# Log for Admin to see "who voted & when" (without candidate info)
class VoteLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} voted on {self.voted_at.strftime('%d-%m-%Y %H:%M')}"

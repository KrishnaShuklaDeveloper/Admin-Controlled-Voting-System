from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting_system.core.models import Candidate, Vote, VoteLog
import random

class Command(BaseCommand):
    help = 'Generate bulk votes for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20, help='Number of test users to vote')

    def handle(self, *args, **options):
        count = options['count']
        candidates = Candidate.objects.all()

        if not candidates.exists():
            self.stdout.write(self.style.ERROR("No candidates found. Please add candidates first."))
            return

        for i in range(count):
            username = f'testuser_{i}'
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('password')
                user.save()

            # Avoid double voting
            if Vote.objects.filter(user=user).exists():
                continue

            candidate = random.choice(candidates)
            Vote.objects.create(user=user, candidate=candidate)
            VoteLog.objects.create(user=user)

        self.stdout.write(self.style.SUCCESS(f'Successfully cast {count} test votes!'))

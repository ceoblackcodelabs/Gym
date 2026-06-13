# management/commands/seed_testimonials.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from home.models import Testimonial  # Change 'home' to your app name

class Command(BaseCommand):
    help = 'Seed testimonials data into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting testimonial seeding...'))

        # Clear existing testimonials (optional)
        # Uncomment if you want to replace existing data
        # Testimonial.objects.all().delete()
        # self.stdout.write('Cleared existing testimonials.')

        # Static testimonials data from your HTML
        testimonials_data = [
            {
                'name': 'Marcus Reed',
                'initials': 'MR',
                'content': '"Atomic Gym completely changed my life. In 8 months I lost 45 lbs and gained more confidence than I\'ve had in years. The coaches here aren\'t just trainers — they\'re invested in your success."',
                'rating': 5,
                'member_since': 'Member for 2 years',
                'membership_plan': 'Warrior Plan',
                'is_active': True,
                'is_featured': True,
                'display_order': 1,
            },
            {
                'name': 'Sarah Langford',
                'initials': 'SL',
                'content': '"I\'ve been to gyms all over the country and nothing comes close to Atomic. The equipment is immaculate, the vibe is electric, and the personal training program took my performance to a completely different level."',
                'rating': 5,
                'member_since': 'Member for 3 years',
                'membership_plan': 'Elite Plan',
                'is_active': True,
                'is_featured': True,
                'display_order': 2,
            },
            {
                'name': 'Darius Knight',
                'initials': 'DK',
                'content': '"The combat sports program here is elite. My coach helped me drop two weight classes and sharpen my technique. The community is what keeps you coming back — everyone pushes each other."',
                'rating': 5,
                'member_since': 'Member for 18 months',
                'membership_plan': 'Elite Plan',
                'is_active': True,
                'is_featured': True,
                'display_order': 3,
            },
            {
                'name': 'Jessica Park',
                'initials': 'JP',
                'content': '"Joined on the Rookie plan and within three months I upgraded to Warrior. The nutrition coaching alone was worth every penny — I finally understand how to fuel my workouts properly."',
                'rating': 5,
                'member_since': 'Member for 1 year',
                'membership_plan': 'Warrior Plan',
                'is_active': True,
                'is_featured': True,
                'display_order': 4,
            },
            {
                'name': 'Michael Chen',
                'initials': 'MC',
                'content': '"Best decision I ever made. The 24/7 access fits my crazy schedule perfectly, and the equipment is always well-maintained. The community here is like family."',
                'rating': 5,
                'member_since': 'Member for 3 years',
                'membership_plan': 'Rookie Plan',
                'is_active': True,
                'is_featured': False,
                'display_order': 5,
            },
            {
                'name': 'Emma Rodriguez',
                'initials': 'ER',
                'content': '"The yoga and mobility classes transformed my recovery. I used to always be sore, but now I\'m training harder than ever with less pain. The coaches are world-class."',
                'rating': 5,
                'member_since': 'Member for 1.5 years',
                'membership_plan': 'Elite Plan',
                'is_active': True,
                'is_featured': False,
                'display_order': 6,
            },
            {
                'name': 'David Kim',
                'initials': 'DK',
                'content': '"Lost 30 pounds in 6 months. The HIIT classes are intense but so worth it. The nutrition coaching helped me understand what I was doing wrong with my diet."',
                'rating': 5,
                'member_since': 'Member for 8 months',
                'membership_plan': 'Warrior Plan',
                'is_active': True,
                'is_featured': False,
                'display_order': 7,
            },
            {
                'name': 'Rachel Stevens',
                'initials': 'RS',
                'content': '"From a complete beginner to half-marathon ready in 4 months. The personal training program is worth every penny. The trainers actually care about your progress."',
                'rating': 5,
                'member_since': 'Member for 2 years',
                'membership_plan': 'Warrior Plan',
                'is_active': True,
                'is_featured': False,
                'display_order': 8,
            },
            {
                'name': 'Tom Williams',
                'initials': 'TW',
                'content': '"The recovery suite with sauna and ice bath is a game changer. I recover twice as fast now and can train harder more frequently. Best gym in the city hands down."',
                'rating': 5,
                'member_since': 'Member for 1 year',
                'membership_plan': 'Elite Plan',
                'is_active': True,
                'is_featured': False,
                'display_order': 9,
            },
            {
                'name': 'Lisa Thompson',
                'initials': 'LT',
                'content': '"As a competitive powerlifter, I need serious equipment. Atomic has Eleiko bars, competition plates, and mono lifts. The atmosphere pushes you to be better."',
                'rating': 5,
                'member_since': 'Member for 2 years',
                'membership_plan': 'Elite Plan',
                'is_active': True,
                'is_featured': False,
                'display_order': 10,
            },
        ]

        # Create testimonials
        created_count = 0
        updated_count = 0

        for data in testimonials_data:
            # Check if testimonial with same name and content exists
            obj, created = Testimonial.objects.get_or_create(
                name=data['name'],
                content=data['content'],
                defaults=data
            )

            if not created:
                # Update existing testimonial
                for key, value in data.items():
                    setattr(obj, key, value)
                obj.save()
                updated_count += 1
            else:
                created_count += 1

            self.stdout.write(f"{'Created' if created else 'Updated'}: {obj.name}")

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✓ Seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'  - Created: {created_count} testimonials'))
        self.stdout.write(self.style.SUCCESS(f'  - Updated: {updated_count} testimonials'))
        self.stdout.write(self.style.SUCCESS(f'  - Total: {Testimonial.objects.count()} testimonials in database'))

class CommandWithClear(BaseCommand):
    """Alternative command that clears existing testimonials first"""
    help = 'Clear and reseed testimonials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing testimonials before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Testimonial.objects.count()
            Testimonial.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing testimonials.'))

        # Call the main seeding command
        command = Command()
        command.handle(*args, **options)
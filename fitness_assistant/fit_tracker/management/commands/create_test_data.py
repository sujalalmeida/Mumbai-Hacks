import datetime
import random
from django.core.management.base import BaseCommand
from fitness_assistant.fit_tracker.models import FitnessData


class Command(BaseCommand):
    help = 'Create test fitness data for the last 7 days'

    def handle(self, *args, **kwargs):
        # Delete existing data if it exists
        self.stdout.write(self.style.WARNING('Clearing existing recent test data...'))
        
        # Get dates for the last 7 days
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=7)
        
        # Delete any data that might exist for these dates
        FitnessData.objects.filter(
            activity_date__gte=start_date,
            activity_date__lte=end_date
        ).delete()
        
        # Create sample data for the last 7 days
        self.stdout.write(self.style.SUCCESS('Creating new test data...'))
        
        # User ID to use for test data
        user_id = 12345
        
        # Generate data for each day
        current_date = start_date
        while current_date <= end_date:
            # Create random but realistic fitness data
            # Vary the step count to show a trend
            day_number = (current_date - start_date).days + 1
            base_steps = 8000  # Base number of steps
            
            # Add some randomness but also a slight upward trend
            steps = base_steps + random.randint(-1500, 1500) + (day_number * 100)
            
            # Create distance based on steps (rough approximation)
            distance = steps / 1300  # Approx conversion from steps to km
            
            # Create activity minutes
            very_active = random.randint(20, 60)
            lightly_active = random.randint(100, 240)
            
            # Create calories based on activity and steps
            calories = int(steps * 0.04) + random.randint(-100, 100)
            
            # Create the fitness data entry
            FitnessData.objects.create(
                id_from_fitbit=user_id,
                activity_date=current_date,
                total_steps=steps,
                total_distance=distance,
                very_active_minutes=very_active,
                lightly_active_minutes=lightly_active,
                calories=calories
            )
            
            # Move to the next day
            current_date += datetime.timedelta(days=1)
        
        # Print success message
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created test data for {(end_date - start_date).days + 1} days')
        ) 
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from pathlib import Path
from fitness_assistant.fit_tracker.models import FitnessData


class Command(BaseCommand):
    help = 'Import Fitbit data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='data/mock_fitbit_data.csv',
            help='Path to the CSV file containing Fitbit data'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        full_path = base_dir / file_path
        
        if not full_path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {full_path}'))
            return
            
        self.stdout.write(self.style.SUCCESS(f'Importing data from {full_path}'))
        
        try:
            # Read CSV file with pandas
            df = pd.read_csv(full_path)
            
            # Count records before import
            before_count = FitnessData.objects.count()
            
            # Import each record
            imported = 0
            skipped = 0
            
            for _, row in df.iterrows():
                try:
                    FitnessData.objects.create(
                        id_from_fitbit=row['Id'],
                        activity_date=row['ActivityDate'],
                        total_steps=row['TotalSteps'],
                        total_distance=row['TotalDistance'],
                        very_active_minutes=row['VeryActiveMinutes'],
                        lightly_active_minutes=row['LightlyActiveMinutes'],
                        calories=row['Calories']
                    )
                    imported += 1
                except IntegrityError:
                    # Skip duplicate entries
                    skipped += 1
                    
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported {imported} records, skipped {skipped} duplicates.'
            ))
            
            after_count = FitnessData.objects.count()
            self.stdout.write(self.style.SUCCESS(
                f'Database now contains {after_count} records (was {before_count} before import).'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {e}')) 
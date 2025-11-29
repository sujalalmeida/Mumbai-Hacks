from django.db import models

class FitnessData(models.Model):
    """
    Model to store fitness data imported from Fitbit CSV.
    """
    id_from_fitbit = models.IntegerField()
    activity_date = models.DateField()
    total_steps = models.IntegerField()
    total_distance = models.FloatField()
    very_active_minutes = models.IntegerField()
    lightly_active_minutes = models.IntegerField()
    calories = models.IntegerField()
    
    class Meta:
        # Create a unique constraint to prevent duplicate entries
        unique_together = ('id_from_fitbit', 'activity_date')
        
    def __str__(self):
        return f"Fitness Data for User {self.id_from_fitbit} on {self.activity_date}" 
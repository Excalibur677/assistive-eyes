from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100)
    uses = models.TextField()
    dosage = models.TextField()
    side_effects = models.TextField()
    warnings = models.TextField(blank=True)

    def __str__(self):
        return self.name
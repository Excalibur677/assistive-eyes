from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100)
    uses = models.TextField()
    dosage = models.TextField()
    side_effects = models.TextField()
    warnings = models.TextField(blank=True)

class ScanHistory(models.Model):

    medicine_name = models.CharField(max_length=200)
    generic_name  = models.CharField(max_length=200, blank=True)
    category      = models.CharField(max_length=100, blank=True)
    success       = models.BooleanField(default=False)
    message       = models.CharField(max_length=500, blank=True)
    scanned_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} - {self.scanned_at}"
    
    def __str__(self):
        return self.name
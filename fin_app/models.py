from django.db import models

class Company(models.Model):
    ticker = models.CharField(max_length=10)
    short_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.short_name}: {self.ticker}"
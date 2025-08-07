from django.db import models

# Create your models here.
class Companydetails(models.Model):
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    company_type = models.CharField(max_length=100)
    directory = models.CharField(max_length=100)
    directory_url = models.URLField()
    company_profile_url = models.URLField()
    scrapped_at = models.DateTimeField()

    def __str__(self):
        return f"{self.company_name} based on {self.location} {self.company_type} {self.directory}"


class RecentCount(models.Model):
    recent_company_id = models.ForeignKey(Companydetails, on_delete=models.CASCADE)

    def __str__(self):
        return f"this company {self.recent_company_id} is seen"

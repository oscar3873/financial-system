from django.db import models

# Create your models here.
class PhoneNumber(models.Model):
    PHONETYPE = (
        ('C', 'Celular'), 
        ('F', 'Fijo'), 
        ('A', 'Alternativo')
    )
    
    phone_number = models.CharField(null=True, blank=True, max_length=50, help_text="Phone number")
    phone_type = models.CharField(max_length=20, help_text="Type of phone", choices=PHONETYPE, blank=True)
    
    def __str__(self) -> str:
        return self.phone_number
    
class Client(models.Model):
    
    CivilStatus = (
        ('S','Soltero'),
        ('C', 'Casado'),
        ('V', 'Viudo'),
        ('D', 'Divorciado')
    )
    
    first_name = models.CharField(max_length=50, help_text="First name")
    last_name = models.CharField(max_length=50, help_text="Last name")
    email = models.EmailField(max_length=254, blank=False, help_text="Email address")
    civil_status = models.CharField(blank=True, choices=CivilStatus, max_length=10)
    dni = models.PositiveIntegerField(null=False, help_text="dni number", blank=False)
    phone_numbers = models.ManyToManyField(PhoneNumber)
    profession = models.CharField(max_length=50, help_text="Profession")
    address = models.CharField(max_length=250, help_text="Address")
    job_address = models.CharField(max_length=250, help_text="Job address")
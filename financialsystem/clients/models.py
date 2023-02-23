from django.db import models
from django.contrib.auth.models import User

# Create your models here.    
class Client(models.Model):
    
    CivilStatus = (
        ('S','Soltero'),
        ('C', 'Casado'),
        ('V', 'Viudo'),
        ('D', 'Divorciado')
    )
    
    SCORE = [
        (600 , 'Bueno (600)'),
        (400 , 'Regular (400)'),
        (200 , 'Riesgoso (200)')
    ]

    first_name = models.CharField(max_length=50, help_text="First name", verbose_name="Nombre")
    last_name = models.CharField(max_length=50, help_text="Last name", verbose_name="Apellido")
    adviser = models.ForeignKey(User, on_delete=models.SET_DEFAULT, blank=True, null=True, default=None, help_text="Clientes del usuario", related_name="user_clients")
    email = models.EmailField(max_length=254, blank=False, help_text="Email address", verbose_name="Correo electronico")
    civil_status = models.CharField(blank=True, choices=CivilStatus, max_length=10, verbose_name="Estado civil")
    dni = models.PositiveIntegerField(null=False, help_text="dni number", blank=False, verbose_name="DNI")
    profession = models.CharField(max_length=50, help_text="Profession", verbose_name="Profesion")
    address = models.CharField(max_length=250, help_text="Address", verbose_name="Direccion")
    score = models.PositiveIntegerField(choices=SCORE, default=200 , null=True)
    job_address = models.CharField(max_length=250, help_text="Job address", verbose_name="Direccion laboral")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
 
class PhoneNumber(models.Model):
    
    PHONETYPE = (
        ('C', 'Celular'), 
        ('F', 'Fijo'),
        ('A', 'Alternativo')
    )
    
    phone_number = models.CharField(null=True, blank=True, max_length=50, help_text="Phone number", verbose_name="Numero de Telefono")
    phone_type = models.CharField(max_length=20, help_text="Type of phone", choices=PHONETYPE, verbose_name="Tipo de Telefono")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, default="Some String",)
    
    def __str__(self) -> str:
        return self.phone_number
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from adviser.models import Adviser


class Client(models.Model):
    
    CivilStatus = (
        ('S','Soltero'),
        ('C', 'Casado'),
        ('V', 'Viudo'),
        ('D', 'Divorciado')
    )
    
    SCORE = [
        ('Exelente','Exelente'),
        ('Muy Bueno', 'Muy bueno'),
        ('Bueno' , 'Bueno'),
        ('Regular' , 'Regular'),
        ('Riesgoso' , 'Riesgoso')
    ]
    is_legals = models.BooleanField(blank=True, default=False, null=True, verbose_name="Legales")
    has_pay_stub = models.BooleanField(blank=True, default=False, null=True, verbose_name="Recibo de sueldo")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, help_text="First name", verbose_name="Nombre")
    last_name = models.CharField(max_length=50, help_text="Last name", verbose_name="Apellido")
    adviser = models.ForeignKey(Adviser, on_delete=models.SET_NULL, blank=True, null=True, default=None, help_text="Clientes del usuario")
    email = models.EmailField(max_length=254, blank=False, help_text="Email address", verbose_name="Correo electronico")
    civil_status = models.CharField(blank=True, choices=CivilStatus, max_length=10, verbose_name="Estado civil")
    dni = models.PositiveIntegerField(null=False, help_text="dni number", blank=False, verbose_name="DNI")
    profession = models.CharField(max_length=50, help_text="Profession", verbose_name="Profesion")
    address = models.CharField(max_length=250, help_text="Address", verbose_name="Direccion")
    score = models.PositiveIntegerField(default=0, null=True, validators=[MinValueValidator(0), MaxValueValidator(1500)])
    score_label = models.CharField(blank=True, choices=SCORE, max_length=10, verbose_name="Estado del score", null=True)
    job_address = models.CharField(max_length=250, help_text="Job address", verbose_name="Direccion laboral")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
    def set_score_label(self):
        if self.score <= 200:
            self.score_label = 'Riesgoso'
        elif self.score <= 400:
            self.score_label = 'Regular'
        elif self.score <= 800:
            self.score_label = 'Bueno'
        elif self.score <= 1200:
            self.score_label = 'Muy Bueno'
        else:
            self.score_label = 'Exelente'

    def save(self, *args, **kwargs):
        self.set_score_label()
        super(Client, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ["created_at"]


class PhoneNumberClient(models.Model):
    
    PHONETYPE = (
        ('C', 'Celular'), 
        ('F', 'Fijo'),
        ('A', 'Alternativo')
    )
    
    phone_number_c = models.CharField(null=True, blank=True, max_length=50, help_text="Phone number", verbose_name="Numero de Telefono")
    phone_type_c = models.CharField(max_length=20, help_text="Type of phone", choices=PHONETYPE, verbose_name="Tipo de Telefono")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True, default="Some String",)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.phone_number_c or ""
    
from django.db import models

# Create your models here.
class Transactions(models.Model):

    id = models.UUIDField(primary_key= True)
    id_movement = models.UUIDField()
    id_transaction = models.UUIDField()
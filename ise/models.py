from django.db import models

# Create your models here.
# python3 manage.py makemigrations
# python3 manage.py migrate

class UserAddress(models.Model):
    uid = models.IntegerField()
    type = models.IntegerField()
    addr = models.CharField(max_length=50)
    money = models.DecimalField(max_digits=20,decimal_places=8)
    status = models.IntegerField()

    def __str__(self):
        return self.uid
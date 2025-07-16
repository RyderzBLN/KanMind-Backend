from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class KanbanUser(AbstractUser):
    fullname = models.CharField(max_length=150, unique=False)
    email = models.EmailField(unique=True)


    USERNAME_FIELD = 'email'  # 🔑 Login erfolgt mit Email!
    REQUIRED_FIELDS = ['fullname']  # Wird bei createsuperuser abgefragt
   

    def __str__(self):
        return self.username
#
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

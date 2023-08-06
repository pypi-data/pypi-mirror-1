from django.db import models

from django.contrib.auth.models import User


class Visitor(models.Model):
    name=models.CharField(max_length=100, blank=False, db_index=True,unique=True)

    
##     class Meta:
##         abstract = True

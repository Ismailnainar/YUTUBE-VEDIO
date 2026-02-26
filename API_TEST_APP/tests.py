from django.db import models

class Token(models.Model):
    token = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
bbbb Ismail
aaaaaaaa Main 

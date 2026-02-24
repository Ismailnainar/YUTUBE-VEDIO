from django.db import models

class Token(models.Model):
    token = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class INVOICE_RETURN_ID_Models(models.Model):
    INVOICE_RETURN_ID=  models.CharField(max_length=200, default="",unique=True)
    TOCKEN=  models.CharField(max_length=200, default="")
    class Meta:
        db_table = "INVOICE_REUTRN_ID_TBL"
        ordering = ["id"] 

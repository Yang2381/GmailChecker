from django.db import models


# Create your models here.
class User(models.Model):
	email = models.CharField(max_length=128, db_index=True)
	password = models.CharField(max_length=64)
	nick = models.CharField(max_length=128, null=True)
	created_at = models.DateTimeField(auto_now_add=True)


class Email(models.Model):

    sha1 = models.CharField(max_length=64, db_index=True)
    create_user = models.CharField(max_length=128, db_index=True)
    src_email = models.CharField(max_length=128)
    tar_email = models.CharField(max_length=128)
    message_id = models.CharField(max_length=64, null=True)
    detail = models.CharField(max_length=256, null=True)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

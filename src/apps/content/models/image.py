from django.db import models


class Image(models.Model):
    image = models.ImageField(upload_to="images/", verbose_name="Изображение")


class File(models.Model):
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to="files/", verbose_name="Файл")

from django.db import models

class HomepagePhoto(models.Model):
    image = models.ImageField(upload_to='images', blank=False, null=False)
    display = models.BooleanField(default=False)
    order = models.IntegerField(blank=False, null=False, editable=True, unique=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"發表照片: {self.image}"
    class Meta:
        db_table = 'HomepagePhoto'

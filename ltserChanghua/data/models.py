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

class Tag(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'Tag'

class LatestEvent(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200)
    activityTime = models.DateTimeField()
    tags = models.ManyToManyField(Tag)
    views = models.IntegerField(default=0)
    display = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"活動主題: {self.title}"
    class Meta:
        db_table = 'LatestEvent'

class CrabSite(models.Model):
    title = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"螃蟹觀測點位: {self.title}"
    class Meta:
        db_table = 'CrabSite'

class WaterQualityManualSite(models.Model):
    title = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"水質人工觀測點位: {self.title}"
    class Meta:
        db_table = 'WaterQualityManualSite'
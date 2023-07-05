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
    latitude = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"水質人工觀測點位: {self.title}"
    class Meta:
        db_table = 'WaterQualityManualSite'

class BenthicOrganism(models.Model):
    year = models.CharField(max_length=6)
    site = models.CharField(max_length=10)
    month = models.CharField(max_length=6)
    cw = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    mm = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, editable=False)
    sc = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True, editable=False)
    co = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, editable=False)
    s_temp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, editable=False)
    t_sal = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, editable=False)
    s_ph = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, editable=False)
    w_temp = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    w_ph = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, editable=False)
    cond = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    do = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, editable=False)
    w_sal = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    tds = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    turb = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, editable=False)
    orp = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, editable=False)

    class Meta:
        db_table = 'BenthicOrganism'

class CrabData(models.Model):
    year = models.CharField(max_length=6)
    site = models.CharField(max_length=10)
    month = models.CharField(max_length=6)
    Mbr = models.IntegerField(blank=False, null=False, editable=True,default=0)
    Mb = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Ma = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Hf = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Hd = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Hp = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Me = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Sb = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Sl = models.IntegerField(blank=False, null=False, editable=True, default=0)
    It = models.IntegerField(blank=False, null=False, editable=True, default=0)
    If = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Oc = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Al = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Ta = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Gb = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Xf = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Pa = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Pp = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Tc = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Ppi = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Mv = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Charybids_sp = models.IntegerField(blank=False, null=False, editable=True, default=0)
    Mt = models.IntegerField(blank=False, null=False, editable=True, default=0)
    class Meta:
        db_table = 'Crab'
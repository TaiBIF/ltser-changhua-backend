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

class LatestEventTag(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'LatestEventTag'

class LatestEvent(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200)
    activityTime = models.DateTimeField()
    tags = models.ManyToManyField(LatestEventTag)
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
    latitude = models.FloatField(null=True, blank=True)
    longitude =  models.FloatField(null=True, blank=True)
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

class Crab(models.Model):
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

class WaterQualityManual(models.Model):
    year = models.CharField(max_length=6)
    site = models.CharField(max_length=10)
    month = models.CharField(max_length=6)
    w_temp = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    w_ph = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, editable=False)
    phmv = models.DecimalField(max_digits=7, decimal_places=3 , null=True, blank=True, editable=False)
    orp = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, editable=False)
    cond = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    turb = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, editable=False)
    do = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, editable=False)
    tds = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    w_sal = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)
    sg = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, editable=False)

    class Meta:
        db_table = 'WaterQualityManual'

class InterviewTag1(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewTag1'


class InterviewTag2(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interview_tag1 = models.ForeignKey(InterviewTag1, on_delete=models.CASCADE, related_name='interviewtag2_set')
    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewTag2'

class InterviewTag3(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interview_tag2 = models.ForeignKey(InterviewTag2, on_delete=models.CASCADE, related_name='interviewtag3_set')
    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewTag3'

class InterviewStakeholder(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewStakeholder'

class InterviewPeople(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interview_stakeholder = models.ForeignKey(InterviewStakeholder, on_delete=models.CASCADE,
                                              related_name='interviewpeople_set')
    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewPeople'

class InterviewContent(models.Model):
    content = models.TextField()
    interview_tag2 = models.ManyToManyField(InterviewTag2)
    interview_tag3 = models.ManyToManyField(InterviewTag3)
    interview_date = models.DateField()
    interview_people = models.ManyToManyField(InterviewPeople)
    interview_stakeholder = models.ManyToManyField(InterviewStakeholder)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.content}"

    class Meta:
        db_table = 'InterviewContent'


class Literature(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    date = models.IntegerField()
    refID = models.CharField(max_length=255)
    link = models.URLField()
    is_ebook = models.BooleanField(max_length=2)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Literature'

class NewsTag(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'NewsTag'


class News(models.Model):
    title = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    reporter = models.CharField(max_length=255)
    photographer = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField()
    link = models.URLField()
    views = models.IntegerField(default=0)
    tags = models.ManyToManyField('NewsTag', related_name='news')

    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'News'

class ResearchTag(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'ResearchTag'

class Research(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year = models.PositiveIntegerField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField()
    views = models.IntegerField(default=0)
    tags = models.ManyToManyField('ResearchTag', related_name='research')

    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'Research'
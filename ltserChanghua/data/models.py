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
        verbose_name = '首頁照片'
        verbose_name_plural = '首頁照片'

class LatestEventTag(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'LatestEventTag'
        verbose_name = '最新消息-標籤'
        verbose_name_plural = '最新消息-標籤'

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
        verbose_name = '最新消息-內容'
        verbose_name_plural = '最新消息-內容'

class CrabSite(models.Model):
    title = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude =  models.FloatField(null=True, blank=True)
    def __str__(self):
        return f"螃蟹觀測點位: {self.title}"
    class Meta:
        db_table = 'CrabSite'
        verbose_name = '底棲生物-人工點位'
        verbose_name_plural = '底棲生物-人工點位'

class WaterQualityManualSite(models.Model):
    title = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    def __str__(self):
        return f"水質人工觀測點位: {self.title}"
    class Meta:
        db_table = 'WaterQualityManualSite'
        verbose_name = '水質觀測-人工點位'
        verbose_name_plural = '水質觀測-人工點位'

class BenthicOrganismData(models.Model):
    year = models.CharField(max_length=6)
    site = models.CharField(max_length=10)
    month = models.CharField(max_length=6)
    cw = models.FloatField(null=True,blank=True)
    mm = models.FloatField(null=True,blank=True)
    sc = models.FloatField(null=True,blank=True)
    co = models.FloatField(null=True,blank=True)
    s_temp = models.FloatField(null=True,blank=True)
    t_sal = models.FloatField(null=True,blank=True)
    s_ph = models.FloatField(null=True,blank=True)
    w_temp = models.FloatField(null=True,blank=True)
    w_ph = models.FloatField(null=True,blank=True)
    cond = models.FloatField(null=True,blank=True)
    do = models.FloatField(null=True,blank=True)
    w_sal = models.FloatField(null=True,blank=True)
    tds = models.FloatField(null=True,blank=True)
    turb = models.FloatField(null=True,blank=True)
    orp = models.FloatField(null=True,blank=True)

    class Meta:
        db_table = 'BenthicOrganismData'
        verbose_name = '底棲生物-人工數據-底質資料'
        verbose_name_plural = '底棲生物-人工數據-底質資料'

class CrabData(models.Model):
    year = models.CharField(max_length=6)
    site = models.CharField(max_length=10)
    month = models.CharField(max_length=6)
    Mbr = models.IntegerField(blank=True, null=True, default=0)
    Mb = models.IntegerField(blank=True, null=True, default=0)
    Ma = models.IntegerField(blank=True, null=True, default=0)
    Hf = models.IntegerField(blank=True, null=True, default=0)
    Hd = models.IntegerField(blank=True, null=True, default=0)
    Hp = models.IntegerField(blank=True, null=True, default=0)
    Me = models.IntegerField(blank=True, null=True, default=0)
    Sb = models.IntegerField(blank=True, null=True, default=0)
    Sl = models.IntegerField(blank=True, null=True, default=0)
    It = models.IntegerField(blank=True, null=True, default=0)
    Oc = models.IntegerField(blank=True, null=True, default=0)
    Al = models.IntegerField(blank=True, null=True, default=0)
    Ta = models.IntegerField(blank=True, null=True, default=0)
    Gb = models.IntegerField(blank=True, null=True, default=0)
    Xf = models.IntegerField(blank=True, null=True, default=0)
    Pa = models.IntegerField(blank=True, null=True, default=0)
    Pp = models.IntegerField(blank=True, null=True, default=0)
    Tc = models.IntegerField(blank=True, null=True, default=0)
    Ppi = models.IntegerField(blank=True, null=True, default=0)
    Mv = models.IntegerField(blank=True, null=True, default=0)
    Charybids_sp = models.IntegerField(blank=True, null=True, default=0)
    Mt = models.IntegerField(blank=True, null=True, default=0)
    Pb = models.IntegerField(blank=True, null=True, default=0)
    class Meta:
        db_table = 'Crab'
        verbose_name = '底棲生物-人工數據-螃蟹資料'
        verbose_name_plural = '底棲生物-人工數據-螃蟹資料'

class WaterQualityManualData(models.Model):
    year = models.CharField(max_length=6)
    site = models.CharField(max_length=10)
    month = models.CharField(max_length=6)
    w_temp = models.FloatField(blank=True, null=True)
    w_ph = models.FloatField(blank=True, null=True)
    phmv = models.FloatField(blank=True, null=True)
    orp = models.FloatField(blank=True, null=True)
    cond = models.FloatField(blank=True, null=True)
    turb = models.FloatField(blank=True, null=True)
    do = models.FloatField(blank=True, null=True)
    tds = models.FloatField(blank=True, null=True)
    w_sal = models.FloatField(blank=True, null=True)
    sg = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'WaterQualityManualData'
        verbose_name = '水質觀測-人工數據'
        verbose_name_plural = '水質觀測-人工數據'

class InterviewTag1(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewTag1'
        verbose_name = '訪談資料-標籤1'
        verbose_name_plural = '訪談資料-標籤1'


class InterviewTag2(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    search_volume = models.IntegerField(blank=True, null=True, default=0, editable=False)
    download_volume = models.IntegerField(blank=True, null=True, default=0, editable=False)
    interview_tag1 = models.ForeignKey(InterviewTag1, on_delete=models.CASCADE, related_name='interviewtag2_set')
    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewTag2'
        verbose_name = '訪談資料-標籤2'
        verbose_name_plural = '訪談資料-標籤2'

class InterviewTag3(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    search_volume = models.IntegerField(blank=True, null=True, default=0, editable=False)
    download_volume = models.IntegerField(blank=True, null=True, default=0, editable=False)
    interview_tag2 = models.ForeignKey(InterviewTag2, on_delete=models.CASCADE, related_name='interviewtag3_set')
    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewTag3'
        verbose_name = '訪談資料-標籤3'
        verbose_name_plural = '訪談資料-標籤3'

class InterviewStakeholder(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    optionId = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewStakeholder'
        verbose_name = '訪談資料-受訪對象'
        verbose_name_plural = '訪談資料-受訪對象'

class InterviewPeople(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    interview_stakeholder = models.ForeignKey(InterviewStakeholder, on_delete=models.CASCADE,
                                              related_name='interviewpeople_set')
    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'InterviewPeople'
        verbose_name = '訪談資料-受訪者'
        verbose_name_plural = '訪談資料-受訪者'

class InterviewContent(models.Model):
    content = models.TextField()
    interview_tag2 = models.ManyToManyField(InterviewTag2, blank=True)
    interview_tag3 = models.ManyToManyField(InterviewTag3, blank=True)
    interview_date = models.DateField()
    interview_people = models.ManyToManyField(InterviewPeople)
    interview_stakeholder = models.ManyToManyField(InterviewStakeholder)

    def __str__(self):
        return f"{self.content}"

    class Meta:
        db_table = 'InterviewContent'
        verbose_name = '訪談資料-內容'
        verbose_name_plural = '訪談資料-內容'


class Literature(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    date = models.IntegerField()
    refID = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    is_ebook = models.BooleanField(max_length=2)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Literature'
        verbose_name = '地方文獻'
        verbose_name_plural = '地方文獻'

class NewsTag(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'NewsTag'
        verbose_name = '新聞報導-標籤'
        verbose_name_plural = '新聞報導-標籤'


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
        verbose_name = '新聞報導-內容'
        verbose_name_plural = '新聞報導-內容'

class ResearchTag(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'ResearchTag'
        verbose_name = '相關研究-標籤'
        verbose_name_plural = '相關研究-標籤'

class Research(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year = models.PositiveIntegerField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    views = models.IntegerField(default=0)
    tags = models.ManyToManyField('ResearchTag', related_name='research')

    def __str__(self):
        return f"標籤: {self.title}"
    class Meta:
        db_table = 'Research'
        verbose_name = '相關研究-內容'
        verbose_name_plural = '相關研究-內容'


class Staff(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    duty = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    image = models.ImageField(upload_to='images', blank=False, null=False)
    order = models.IntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'Staff'
        verbose_name = '人員職務'
        verbose_name_plural = '人員職務'
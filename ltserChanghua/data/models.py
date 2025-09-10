from django.db import models


class HomepagePhoto(models.Model):
    image = models.ImageField(upload_to="images", blank=False, null=False)
    display = models.BooleanField(default=False)
    order = models.IntegerField(
        blank=False, null=False, editable=True, unique=True, default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"發表照片: {self.image}"

    class Meta:
        db_table = "HomepagePhoto"
        verbose_name = "首頁照片"
        verbose_name_plural = "首頁照片"


class LatestEventTag(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"標籤: {self.title}"

    class Meta:
        db_table = "LatestEventTag"
        verbose_name = "最新消息-標籤"
        verbose_name_plural = "最新消息-標籤"


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
        db_table = "LatestEvent"
        verbose_name = "最新消息-內容"
        verbose_name_plural = "最新消息-內容"


class CrabSite(models.Model):
    title = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"螃蟹觀測點位: {self.title}"

    class Meta:
        db_table = "CrabSite"
        verbose_name = "底棲生物-人工點位"
        verbose_name_plural = "底棲生物-人工點位"


class WaterQualityManualSite(models.Model):
    title = models.CharField(max_length=200)
    latitude = models.DecimalField(
        max_digits=15, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=15, decimal_places=8, null=True, blank=True
    )

    def __str__(self):
        return f"水質人工觀測點位: {self.title}"

    class Meta:
        db_table = "WaterQualityManualSite"
        verbose_name = "水質觀測-人工點位"
        verbose_name_plural = "水質觀測-人工點位"


class BenthicOrganismData(models.Model):
    year = models.CharField(max_length=6)
    site = models.CharField(max_length=10)
    month = models.CharField(max_length=6)
    cw = models.FloatField(null=True, blank=True)
    mm = models.FloatField(null=True, blank=True)
    sc = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    s_temp = models.FloatField(null=True, blank=True)
    t_sal = models.FloatField(null=True, blank=True)
    s_ph = models.FloatField(null=True, blank=True)
    w_temp = models.FloatField(null=True, blank=True)
    w_ph = models.FloatField(null=True, blank=True)
    cond = models.FloatField(null=True, blank=True)
    do = models.FloatField(null=True, blank=True)
    w_sal = models.FloatField(null=True, blank=True)
    tds = models.FloatField(null=True, blank=True)
    turb = models.FloatField(null=True, blank=True)
    orp = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "BenthicOrganismData"
        verbose_name = "底棲生物-人工數據-底質資料"
        verbose_name_plural = "底棲生物-人工數據-底質資料"


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
    Mth = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = "Crab"
        verbose_name = "底棲生物-人工數據-螃蟹資料"
        verbose_name_plural = "底棲生物-人工數據-螃蟹資料"


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
        db_table = "WaterQualityManualData"
        verbose_name = "水質觀測-人工數據"
        verbose_name_plural = "水質觀測-人工數據"


class InterviewTag1(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "InterviewTag1"
        verbose_name = "訪談資料-標籤1"
        verbose_name_plural = "訪談資料-標籤1"


class InterviewTag2(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    search_volume = models.IntegerField(
        blank=True, null=True, default=0, editable=False
    )
    download_volume = models.IntegerField(
        blank=True, null=True, default=0, editable=False
    )
    interview_tag1 = models.ForeignKey(
        InterviewTag1, on_delete=models.CASCADE, related_name="interviewtag2_set"
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "InterviewTag2"
        verbose_name = "訪談資料-標籤2"
        verbose_name_plural = "訪談資料-標籤2"


class InterviewTag3(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    search_volume = models.IntegerField(
        blank=True, null=True, default=0, editable=False
    )
    download_volume = models.IntegerField(
        blank=True, null=True, default=0, editable=False
    )
    interview_tag2 = models.ForeignKey(
        InterviewTag2, on_delete=models.CASCADE, related_name="interviewtag3_set"
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "InterviewTag3"
        verbose_name = "訪談資料-標籤3"
        verbose_name_plural = "訪談資料-標籤3"


class InterviewStakeholder(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    optionId = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "InterviewStakeholder"
        verbose_name = "訪談資料-受訪對象"
        verbose_name_plural = "訪談資料-受訪對象"


class InterviewPeople(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    interview_stakeholder = models.ForeignKey(
        InterviewStakeholder,
        on_delete=models.CASCADE,
        related_name="interviewpeople_set",
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "InterviewPeople"
        verbose_name = "訪談資料-受訪者"
        verbose_name_plural = "訪談資料-受訪者"


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
        db_table = "InterviewContent"
        verbose_name = "訪談資料-內容"
        verbose_name_plural = "訪談資料-內容"


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
        db_table = "Literature"
        verbose_name = "地方文獻"
        verbose_name_plural = "地方文獻"


class NewsTag(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"標籤: {self.title}"

    class Meta:
        db_table = "NewsTag"
        verbose_name = "新聞報導-標籤"
        verbose_name_plural = "新聞報導-標籤"


class News(models.Model):
    title = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    reporter = models.CharField(max_length=255)
    photographer = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField()
    link = models.URLField()
    views = models.IntegerField(default=0)
    tags = models.ManyToManyField("NewsTag", related_name="news")

    def __str__(self):
        return f"標籤: {self.title}"

    class Meta:
        db_table = "News"
        verbose_name = "新聞報導-內容"
        verbose_name_plural = "新聞報導-內容"


class ResearchTag(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"標籤: {self.title}"

    class Meta:
        db_table = "ResearchTag"
        verbose_name = "相關研究-標籤"
        verbose_name_plural = "相關研究-標籤"


class Research(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year = models.PositiveIntegerField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    views = models.IntegerField(default=0)
    tags = models.ManyToManyField("ResearchTag", related_name="research")

    def __str__(self):
        return f"標籤: {self.title}"

    class Meta:
        db_table = "Research"
        verbose_name = "相關研究-內容"
        verbose_name_plural = "相關研究-內容"


class Staff(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    duty = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    image = models.ImageField(upload_to="images", blank=False, null=False)
    order = models.IntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "Staff"
        verbose_name = "人員職務"
        verbose_name_plural = "人員職務"


class ResearchesIssue(models.Model):
    title = models.CharField(max_length=255, verbose_name="問題描述")
    identity = models.CharField(
        max_length=255,
        verbose_name="提問人身份",
        help_text="例如：治理機關、研究單位、生產者",
    )
    link = models.URLField(max_length=500, verbose_name="連結")
    is_display = models.BooleanField(
        default=True,
        verbose_name="是否顯示於前端",
        help_text="（勾選後，該主題將顯示於前端頁面；未勾選則不顯示）",
    )
    hits = models.IntegerField(
        default=0,
        verbose_name="點擊數",
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "ResearchesIssue"
        verbose_name = "聚焦主題"
        verbose_name_plural = "聚焦主題"


class PopulationStats(models.Model):
    year = models.CharField(max_length=4, verbose_name="資料年份")
    county_code = models.CharField(max_length=10, verbose_name="縣市代碼")
    county_name = models.CharField(max_length=20, verbose_name="縣市名稱")
    town_code = models.CharField(max_length=10, verbose_name="鄉鎮市區代碼")
    town_name = models.CharField(max_length=20, verbose_name="鄉鎮市區名稱")
    village_code = models.CharField(max_length=20, verbose_name="村里代碼")
    village_name = models.CharField(max_length=20, verbose_name="村里名稱")

    household_count = models.CharField(max_length=10, verbose_name="戶數")
    population_total = models.CharField(max_length=10, verbose_name="人口數")
    population_density = models.CharField(max_length=10, verbose_name="人口密度")
    sex_ratio = models.CharField(max_length=10, verbose_name="性別比")
    dependency_ratio = models.CharField(max_length=10, verbose_name="扶養比")
    child_dependency_ratio = models.CharField(max_length=10, verbose_name="扶幼比")
    elderly_dependency_ratio = models.CharField(max_length=10, verbose_name="扶老比")
    aging_index = models.CharField(max_length=10, verbose_name="老化指數")

    crude_birth_rate = models.CharField(max_length=10, verbose_name="粗出生率")
    crude_death_rate = models.CharField(max_length=10, verbose_name="粗死亡率")
    natural_increase_rate = models.CharField(max_length=10, verbose_name="自然增加率")
    social_increase_rate = models.CharField(max_length=10, verbose_name="社會增加率")
    population_growth_rate = models.CharField(max_length=10, verbose_name="人口增加率")

    age_0_14 = models.CharField(max_length=10, verbose_name="0-14歲人口數")
    age_15_64 = models.CharField(max_length=10, verbose_name="15-64歲人口數")
    age_65_up = models.CharField(max_length=10, verbose_name="65歲以上人口數")

    data_collection_time = models.CharField(max_length=20, verbose_name="資料時間")

    def __str__(self):
        return f"{self.county_name} {self.town_name} {self.village_name}"

    class Meta:
        db_table = "PopulationStats"
        verbose_name = "人口統計"
        verbose_name_plural = "人口統計"


class OysterFarmingStats(models.Model):
    year = models.CharField("年份", max_length=10, blank=True, null=True)

    # 平掛式
    horizontal_facilities_nation = models.CharField(
        "全國 - 平掛式設施(組)", max_length=20
    )
    horizontal_farmers_nation = models.CharField(
        "全國 - 平掛式養殖（戶）", max_length=20
    )
    horizontal_facilities_fangyuan = models.CharField(
        "芳苑鄉 - 平掛式設施(組)", max_length=20
    )
    horizontal_farmers_fangyuan = models.CharField(
        "芳苑鄉 - 平掛式養殖（戶）", max_length=20
    )
    horizontal_facilities_changhua = models.CharField(
        "彰化縣 - 平掛式設施(組)", max_length=20
    )
    horizontal_farmers_changhua = models.CharField(
        "彰化縣 - 平掛式養殖（戶）", max_length=20
    )

    # 插篊式
    stake_facilities_nation = models.CharField("全國 - 插篊式設施(組)", max_length=20)
    stake_farmers_nation = models.CharField("全國 - 插篊式養殖（戶）", max_length=20)
    stake_facilities_fangyuan = models.CharField(
        "芳苑鄉 - 插篊式設施(組)", max_length=20
    )
    stake_farmers_fangyuan = models.CharField(
        "芳苑鄉 - 插篊式養殖（戶）", max_length=20
    )
    stake_facilities_changhua = models.CharField(
        "彰化縣 - 插篊式設施(組)", max_length=20
    )
    stake_farmers_changhua = models.CharField(
        "彰化縣 - 插篊式養殖（戶）", max_length=20
    )

    # 垂下式
    hanging_facilities_nation = models.CharField("全國 - 垂下式設施(棚)", max_length=20)
    hanging_farmers_nation = models.CharField("全國 - 垂下式養殖（戶）", max_length=20)
    hanging_facilities_fangyuan = models.CharField(
        "芳苑鄉 - 垂下式設施(棚)", max_length=20
    )
    hanging_farmers_fangyuan = models.CharField(
        "芳苑鄉 - 垂下式養殖（戶）", max_length=20
    )
    hanging_facilities_changhua = models.CharField(
        "彰化縣 - 垂下式設施(棚)", max_length=20
    )
    hanging_farmers_changhua = models.CharField(
        "彰化縣 - 垂下式養殖（戶）", max_length=20
    )

    # 浮筏式
    raft_facilities_nation = models.CharField("全國 - 浮筏式設施(棚)", max_length=20)
    raft_farmers_nation = models.CharField("全國 - 浮筏式養殖（戶）", max_length=20)
    raft_facilities_fangyuan = models.CharField(
        "芳苑鄉 - 浮筏式設施(棚)", max_length=20
    )
    raft_farmers_fangyuan = models.CharField("芳苑鄉 - 浮筏式養殖（戶）", max_length=20)
    raft_facilities_changhua = models.CharField(
        "彰化縣 - 浮筏式設施(棚)", max_length=20
    )
    raft_farmers_changhua = models.CharField("彰化縣 - 浮筏式養殖（戶）", max_length=20)

    # 延繩式
    longline_facilities_nation = models.CharField(
        "全國 - 延繩式設施(組)", max_length=20
    )
    longline_farmers_nation = models.CharField("全國 - 延繩式養殖（戶）", max_length=20)
    longline_facilities_fangyuan = models.CharField(
        "芳苑鄉 - 延繩式設施(組)", max_length=20
    )
    longline_farmers_fangyuan = models.CharField(
        "芳苑鄉 - 延繩式養殖（戶）", max_length=20
    )
    longline_facilities_changhua = models.CharField(
        "彰化縣 - 延繩式設施(組)", max_length=20
    )
    longline_farmers_changhua = models.CharField(
        "彰化縣 - 延繩式養殖（戶）", max_length=20
    )

    # 總戶數
    total_farmers_nation = models.CharField("全國 - 申報（調查）總戶數", max_length=20)
    total_farmers_fangyuan = models.CharField(
        "芳苑鄉 - 申報（調查）總戶數", max_length=20
    )
    total_farmers_changhua = models.CharField(
        "彰化縣 - 申報（調查）總戶數", max_length=20
    )

    def __str__(self):
        return f"{self.year} 年份資料"

    class Meta:
        db_table = "OysterFarmingStats"
        verbose_name = "牡蠣放養統計"
        verbose_name_plural = "牡蠣放養統計"


class FisheryFarmingStats(models.Model):
    year = models.CharField("年份", max_length=10, blank=True, null=True)

    # 文蛤
    hard_clam_households_total = models.CharField(
        "文蛤 - 養殖戶數", max_length=32, blank=True, null=True
    )
    hard_clam_area_hectare = models.CharField(
        "文蛤 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    hard_clam_stocking_in_pond = models.CharField(
        "文蛤 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    hard_clam_stocking_new = models.CharField(
        "文蛤 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    hard_clam_hatchery_households = models.CharField(
        "文蛤 - 魚苗戶", max_length=32, blank=True, null=True
    )
    hard_clam_farmer_households = models.CharField(
        "文蛤 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 烏魚
    mullet_households_total = models.CharField(
        "烏魚 - 養殖戶數", max_length=32, blank=True, null=True
    )
    mullet_area_hectare = models.CharField(
        "烏魚 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    mullet_stocking_in_pond = models.CharField(
        "烏魚 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    mullet_stocking_new = models.CharField(
        "烏魚 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    mullet_hatchery_households = models.CharField(
        "烏魚 - 魚苗戶", max_length=32, blank=True, null=True
    )
    mullet_farmer_households = models.CharField(
        "烏魚 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 虱目魚
    milkfish_households_total = models.CharField(
        "虱目魚 - 養殖戶數", max_length=32, blank=True, null=True
    )
    milkfish_area_hectare = models.CharField(
        "虱目魚 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    milkfish_stocking_in_pond = models.CharField(
        "虱目魚 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    milkfish_stocking_new = models.CharField(
        "虱目魚 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    milkfish_hatchery_households = models.CharField(
        "虱目魚 - 魚苗戶", max_length=32, blank=True, null=True
    )
    milkfish_farmer_households = models.CharField(
        "虱目魚 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 蜆
    asiatic_clam_households_total = models.CharField(
        "蜆 - 養殖戶數", max_length=32, blank=True, null=True
    )
    asiatic_clam_area_hectare = models.CharField(
        "蜆 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    asiatic_clam_stocking_in_pond = models.CharField(
        "蜆 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    asiatic_clam_stocking_new = models.CharField(
        "蜆 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    asiatic_clam_hatchery_households = models.CharField(
        "蜆 - 魚苗戶", max_length=32, blank=True, null=True
    )
    asiatic_clam_farmer_households = models.CharField(
        "蜆 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 白蝦
    white_shrimp_households_total = models.CharField(
        "白蝦 - 養殖戶數", max_length=32, blank=True, null=True
    )
    white_shrimp_area_hectare = models.CharField(
        "白蝦 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    white_shrimp_stocking_in_pond = models.CharField(
        "白蝦 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    white_shrimp_stocking_new = models.CharField(
        "白蝦 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    white_shrimp_hatchery_households = models.CharField(
        "白蝦 - 魚苗戶", max_length=32, blank=True, null=True
    )
    white_shrimp_farmer_households = models.CharField(
        "白蝦 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 吳郭魚
    tilapia_households_total = models.CharField(
        "吳郭魚 - 養殖戶數", max_length=32, blank=True, null=True
    )
    tilapia_area_hectare = models.CharField(
        "吳郭魚 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    tilapia_stocking_in_pond = models.CharField(
        "吳郭魚 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    tilapia_stocking_new = models.CharField(
        "吳郭魚 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    tilapia_hatchery_households = models.CharField(
        "吳郭魚 - 魚苗戶", max_length=32, blank=True, null=True
    )
    tilapia_farmer_households = models.CharField(
        "吳郭魚 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 鰻魚
    eel_households_total = models.CharField(
        "鰻魚 - 養殖戶數", max_length=32, blank=True, null=True
    )
    eel_area_hectare = models.CharField(
        "鰻魚 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    eel_stocking_in_pond = models.CharField(
        "鰻魚 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    eel_stocking_new = models.CharField(
        "鰻魚 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    eel_hatchery_households = models.CharField(
        "鰻魚 - 魚苗戶", max_length=32, blank=True, null=True
    )
    eel_farmer_households = models.CharField(
        "鰻魚 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 日本黑蜆
    yamato_clam_households_total = models.CharField(
        "日本黑蜆 - 養殖戶數", max_length=32, blank=True, null=True
    )
    yamato_clam_area_hectare = models.CharField(
        "日本黑蜆 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    yamato_clam_stocking_in_pond = models.CharField(
        "日本黑蜆 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    yamato_clam_stocking_new = models.CharField(
        "日本黑蜆 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    yamato_clam_hatchery_households = models.CharField(
        "日本黑蜆 - 魚苗戶", max_length=32, blank=True, null=True
    )
    yamato_clam_farmer_households = models.CharField(
        "日本黑蜆 - 養殖戶", max_length=32, blank=True, null=True
    )

    # 西施貝
    purple_clam_households_total = models.CharField(
        "西施貝 - 養殖戶數", max_length=32, blank=True, null=True
    )
    purple_clam_area_hectare = models.CharField(
        "西施貝 - 養殖面積（公頃）", max_length=64, blank=True, null=True
    )
    purple_clam_stocking_in_pond = models.CharField(
        "西施貝 - 在池-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    purple_clam_stocking_new = models.CharField(
        "西施貝 - 新放養-放養量（尾、粒、隻）", max_length=64, blank=True, null=True
    )
    purple_clam_hatchery_households = models.CharField(
        "西施貝 - 魚苗戶", max_length=32, blank=True, null=True
    )
    purple_clam_farmer_households = models.CharField(
        "西施貝 - 養殖戶", max_length=32, blank=True, null=True
    )

    def __str__(self):
        return f"{self.year} 年份資料"

    class Meta:
        db_table = "FisheryFarmingStats"
        verbose_name = "養殖放養統計"
        verbose_name_plural = "養殖放養統計"

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

#古いファイルは削除する
from django_cleanup import cleanup
#削除を許可しない場合 -> @cleanup.ignore を付ける

class Equipmentmaincategory(models.Model):
    class Meta:
        verbose_name_plural = "メインカテゴリ"

    main_category = models.CharField(max_length=100, help_text ="メインカテゴリ")

    def __str__(self):
        return self.main_category

class Equipmentcategory(models.Model):
    class Meta:
        verbose_name_plural = "サブカテゴリ"

    category = models.CharField(max_length=100, help_text = "カテゴリ")
    main_category = models.ForeignKey(Equipmentmaincategory, on_delete = models.SET_NULL,
                                      null = True, blank = True, help_text="メインカテゴリ名")
    def __str__(self):
        return str(self.main_category) + " - " + self.category

class Equipment(models.Model):
    category = models.ForeignKey(Equipmentcategory, on_delete = models.SET_NULL,
                                 null = True, blank = True, help_text="カテゴリ名")
    management_num = models.IntegerField(null = True, blank = True, help_text="管理番号",)
    name = models.CharField(max_length=100, help_text="名称")

    images = models.ImageField(upload_to = 'equipment/', blank=True, null=True, help_text="画像のURLをそのまま貼り付けても可",)

    alt_image = models.ImageField(upload_to = 'imgs/', help_text="代替画像",
                                  default = 'imgs/no_image_square.jpg',)

    maker = models.CharField(max_length=100, help_text="メーカー", null=False, blank=True, default = "不明", )
    feature = models.CharField(max_length=100, null=False, blank=True, help_text="特徴・色など",)
    size = models.CharField(max_length=100, null=False, blank=True, help_text="サイズなど",)
    num = models.PositiveIntegerField(help_text="個数・本数", default = 1,)

    URL = models.URLField(null = False, blank = True, help_text="販売サイトなどのURLがあれば",)
    purchase_date = models.CharField(max_length=100, null=False, blank=True, default = "不明", help_text="購入時期",)

    status = models.CharField(max_length=10, choices=[('非常に良い', '非常に良い'),
                                                      ('良い', '良い'),
                                                      ('普通', '普通'),
                                                      ('悪い', '悪い'),
                                                      ('非常に悪い', '非常に悪い'),
                                                      ('使用禁止', '使用禁止'),
                                                      ('不明','不明')],
                              help_text="ステータス")

    note = models.TextField(null=False, blank=True, help_text="メモ",)

    created = models.DateTimeField(help_text='作成日', null=True, blank=True)
    modified = models.DateTimeField(help_text='更新日', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Equipment, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "アイテムリスト"

    def __str__(self):
        return self.name

    ##参考サイトなど
    #・https://h-memo.com/django-images/ 画像をリサイズする場合

class Log(models.Model):
    item_name = models.OneToOneField(Equipment, on_delete=models.CASCADE, help_text="名称", related_name='related_itemname')
    times = models.PositiveIntegerField("累計利用回数", default = 0,)

    available = models.CharField(choices=[("不可", "不可"),("可", "可")], max_length=10,
                                 default="可", help_text='利用状況')

    now_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, related_name='now_user',
                                  blank=True, null=True, help_text="現在利用者",)

    previous_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, related_name='previous_user',
                                  blank=True, null=True, help_text="最終使用者",)

    history = models.TextField(null=False, blank=True, help_text="利用履歴",)

    def __str__(self):
        return str(self.item_name)

    class Meta:
        verbose_name_plural = "(メンテナンス用)利用履歴"

    ##参考サイトなど
    #・https://brhk.me/programing/django-foreignkey/#toc7
    #・https://djangobrothers.com/blogs/related_name/
    #・https://y0m0r.hateblo.jp/entry/20130412/1365780614

import datetime
LEND_SPAN = 14
class Lending(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, help_text="利用者", related_name='borrower')#Auto Viewsにて保存処理
    item_name = models.OneToOneField(Equipment, on_delete = models.CASCADE, help_text="装備名", related_name='borrow_item')#Auto Viewsにて保存処理
    lend_date = models.DateTimeField(help_text="利用開始日", default = timezone.now)#Auto Viewsにて保存処理
    lend_span = models.PositiveIntegerField(help_text="貸出期間(日)", default = LEND_SPAN)#Auto Modelsにて保存処理
    return_date = models.DateTimeField(help_text="返却予定日")#Auto Modelsにて保存処理
    note = models.CharField(null=False, blank=True, max_length=140, help_text="メモ欄(最大140文字)",)#Optional Viewsにて保存処理

    def save(self, *args, **kwargs):
        self.return_date = self.lend_date + datetime.timedelta(days=self.lend_span) #return_dateの決定
        return super(Lending, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "(メンテナンス用)利用状況リスト"

    def __str__(self):
        return str(self.user)+ " - "+ str(self.item_name)

    #参考サイトなど
    #https://yu-nix.com/blog/2021/9/10/django-datetimefield/#auto_now_add,%20auto_now%E3%81%AF%E4%BD%BF%E3%81%86%E3%81%B9%E3%81%8D%E3%81%8B%EF%BC%9F

#参考サイトなど
#https://python.always-basics.com/python/python%e5%85%a5%e9%96%80/hello_django/django-models/
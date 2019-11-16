from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField
# Create your models here.
class GoodsType(BaseModel):
    """商品类型类"""
    name = models.CharField(max_length=100, verbose_name="种类名称")
    logo = models.CharField(max_length=100, verbose_name="标识")
    image = models.ImageField(upload_to='type', verbose_name="商品类型图片")

    class Meta:
        db_table = "t_goods_type"
        verbose_name = "商品种类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsSKU(BaseModel):
    """商品SKU模型"""
    status_choices = (
        (0, '下线'),
        (1, '上线'),
    )
    type = models.ForeignKey(to="GoodsType", on_delete=models.CASCADE, verbose_name="商品种类")
    goods = models.ForeignKey(to='Goods', on_delete=models.CASCADE, verbose_name="商品SPU")
    name = models.CharField(max_length=20, verbose_name="名称")
    desc = models.CharField(max_length=256, verbose_name="商品简介")
    price = models.CharField(max_length=20, verbose_name="商品价格")
    unite = models.CharField(max_length=20, verbose_name="商品单位")
    picture = models.ImageField(upload_to='goods', verbose_name="商品图片")
    stock = models.IntegerField(default=1, verbose_name="商品库存")
    sales = models.IntegerField(default=0, verbose_name="商品销量")
    status = models.SmallIntegerField(default=1, choices=status_choices, verbose_name="状态")

    class Meta:
        db_table = "t_goods_SKU"
        verbose_name = "商品"
        verbose_name_plural = verbose_name

class Goods(BaseModel):
    """商品SPU模型"""
    name = models.CharField(max_length=20, verbose_name="商品SPU名称")
    detail = HTMLField(verbose_name="商品详情", blank=True, null=True)
    class Meta:
        db_table = "t_goods"
        verbose_name = "商品SPU"
        verbose_name_plural = verbose_name

class Image(BaseModel):
    """商品图片模型"""
    sku = models.ForeignKey(to='GoodsSKU', on_delete=models.CASCADE, verbose_name="商品")
    image = models.ImageField(upload_to="goods", verbose_name="图片路径")

    class Meta:
        db_table = "t_goods_image"
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name

class IndexGoodsBanner(BaseModel):
    """首页轮播商品展示模型"""
    sku = models.ForeignKey(to='GoodsSKU', on_delete=models.CASCADE, verbose_name="商品")
    image = models.ImageField(upload_to="banner", verbose_name="图片")
    index = models.SmallIntegerField(default=0, verbose_name="展示顺序")

    class Meta:
        db_table = "t_index_banner"
        verbose_name = "首页轮播商品"
        verbose_name_plural = verbose_name

class IndexTypeGoodsBanner(BaseModel):
    """首页分类商品展示模型"""
    DISPLAY_TYPE_CHOICES = (
        (0, '标题'),
        (1, '图片'),
    )
    type = models.ForeignKey(to='GoodsType', on_delete=models.CASCADE, verbose_name="商品类型")
    sku = models.ForeignKey(to='GoodsSKU', on_delete=models.CASCADE, verbose_name="商品SKU")
    display_type = models.SmallIntegerField(default=1, choices=DISPLAY_TYPE_CHOICES, verbose_name="展示标识")
    index = models.SmallIntegerField(default=0, verbose_name="展示顺序")

    class Meta:
        db_table = "t_index_type_goods"
        verbose_name = "主页分类展示商品"
        verbose_name_plural = verbose_name

class IndexPromotionBanner(BaseModel):
    """首页促销活动模型"""
    name = models.CharField(max_length=20, verbose_name="活动名称")
    url = models.URLField(verbose_name="活动地址")
    image = models.ImageField(upload_to="banner", verbose_name="活动图片")
    index = models.SmallIntegerField(default=0, verbose_name="展示顺序")

    class Meta:
        db_table = "t_index_promotion"
        verbose_name = "主页促销活动"
        verbose_name_plural = verbose_name
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import reverse

def show_img(img_url):
    if img_url:
        from django.utils.safestring import mark_safe
        return mark_safe(u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.format(img_url))
    else:
        return '(Нет изображения)'

class DMatchingFuels(models.Model):
    fuel_id = models.IntegerField(primary_key=True)
    external_fuel_id = models.IntegerField(blank=True, null=True)
    fuel_uch_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_matching_fuels'


class DMatchingStation(models.Model):
    service_station_id = models.IntegerField(primary_key=True)
    azs_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_matching_station'


class DStationFuelPrices(models.Model):
    station_id = models.IntegerField(primary_key=True)
    fuel_type_id = models.IntegerField()
    price = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_station_fuel_prices'
        unique_together = (('station_id', 'fuel_type_id'),)


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    # user_id = models.IntegerField()
    user_id = models.ForeignKey('MobileDevice', models.DO_NOTHING, db_column='user_id', verbose_name='Phone number')
    mobile_device_id = models.IntegerField(blank=True, null=True)
    device_id = models.CharField('Phone', max_length=128)
    satisfaction_level = models.SmallIntegerField('Satisfaction level')
    subject = models.SmallIntegerField('Subject')
    description = models.CharField('Description', max_length=2048, blank=True, null=True)
    photo = models.CharField(max_length=1024, blank=True, null=True)
    created_dt = models.DateTimeField('Created time', auto_now_add=True, blank=True, null=True)
    updated_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    id_service_station = models.ForeignKey('ServiceStation', models.DO_NOTHING, db_column='id_service_station')
    answer_id = models.OneToOneField('Message', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='answer_id')

    def user_phone(self):
        return self.device_id[-12:]

    def feedback_title(self):
        return "Сообщение № {}".format(self.id)

    def feedback_img(self):
        return show_img(self.photo)

    feedback_img.short_description = 'Картинка'
    feedback_img.allow_tags = True

    class Meta:
        managed = False
        ordering = ['-id']
        db_table = 'feedback'

    def get_absolute_url_list(self):
        return reverse("feedback_list_view")
    
    
    def get_absolute_url_update(self):
        return reverse("feedback_update", kwargs={"pk": self.pk})

    def get_fields_name(self):
        return [field.verbose_name for field in self._meta.fields]

    def get_field_type(self, field):
        return self._meta.get_field(field).get_internal_type

    def get_fields_name_value(self):
        return [(field.name, getattr(self, field.name)) for field in self._meta.fields]

    def get_model_name(self):
        return self._meta.verbose_name.title()

    def __str__(self):
        return "Сообщение № {}".format(self.id)


class FuelType(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    fuel_id = models.SmallIntegerField()
    active = models.BooleanField()
    version_id = models.IntegerField(unique=True, blank=True, null=True)
    lang_abbr = models.ForeignKey('Language', models.DO_NOTHING, db_column='lang_abbr')
    title = models.CharField(max_length=16)
    external_system_id = models.SmallIntegerField(blank=True, null=True)
    price = models.FloatField()
    price_retail = models.FloatField()

    class Meta:
        managed = False
        db_table = 'fuel_type'
        unique_together = (('fuel_id', 'lang_abbr'),)


class Language(models.Model):
    lang_abbr = models.CharField(primary_key=True, max_length=2)
    lang_name = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'language'


class LoyalInfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    position_id = models.SmallIntegerField()
    active = models.BooleanField()
    version_id = models.IntegerField(unique=True, blank=True, null=True)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    rule = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    full_description = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'loyal_info'
        unique_together = (('position_id', 'lang_abbr'),)


class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    # user_id = models.ForeignKey('MobileDevice', models.DO_NOTHING, db_column='user_id', verbose_name='Phone number')
    active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    version_id = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True,)
    updated_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    internal_description = models.CharField(max_length=255, blank=True, null=True)
    img_url = models.CharField(max_length=255)
    pre_title = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    short_review = models.CharField(max_length=255)
    company_site_url = models.CharField(max_length=255)
    content = models.CharField(max_length=4096)
    message_type = models.ForeignKey('MessageType', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'message'

    def get_model_name(self):
        return self._meta.verbose_name.title()


class MessageImg(models.Model):
    id = models.BigAutoField(primary_key=True)
    message = models.ForeignKey(Message, models.DO_NOTHING)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    resolution_id = models.SmallIntegerField()
    img_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'message_img'
        unique_together = (('message', 'lang_abbr', 'resolution_id'),)


class MessageType(models.Model):
    descriprion = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'message_type'


class MessageTypeImg(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_type = models.ForeignKey(MessageType, models.DO_NOTHING)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    resolution_id = models.SmallIntegerField()
    img_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'message_type_img'
        unique_together = (('message_type', 'lang_abbr', 'resolution_id'),)


class MobileDevice(models.Model):
    id = models.BigAutoField('ID', primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    status = models.SmallIntegerField('Status')
    device_id = models.CharField(unique=True, max_length=128)
    phone_number = models.CharField('Phone number', max_length=12)
    token = models.CharField(unique=True, max_length=128, blank=True, null=True)
    created_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    push_device_registration_token = models.CharField(max_length=4096, blank=True, null=True)

    def get_absolute_url_list(self):
        return reverse("mobile_device_list_view")
    
    def get_absolute_url_update(self):
        return reverse("mobile_device_update", kwargs={"pk": self.pk})
        
    def get_absolute_url_delete(self):
        return reverse("mobile_device_delete", kwargs={"pk": self.pk})
    

    def get_fields_name(self):
        return [field.verbose_name for field in self._meta.fields]

    def get_field_type(self, field):
        return self._meta.get_field(field).get_internal_type

    def get_fields_name_value(self):
        return [(field.name, getattr(self, field.name)) for field in self._meta.fields]

    def get_model_name(self):
        return self._meta.verbose_name.title()

    class Meta:
        managed = False
        db_table = 'mobile_device'

    def __str__(self):
        return self.phone_number


class News(models.Model):
    id = models.BigAutoField('ID', primary_key=True)
    active = models.BooleanField('Active')
    version_id = models.IntegerField('Version ID')
    created_time = models.DateTimeField('Created time', auto_now_add=True)
    updated_time = models.DateTimeField('Updated time', auto_now=True, blank=True, null=True)
    internal_description = models.CharField('Description', max_length=255, blank=True, null=True)
    published = models.BooleanField('Published')

    def get_absolute_url_delete(self):
        return reverse("news_delete", kwargs={"pk": self.pk})

    def get_absolute_url_detail(self):
        return reverse("news_detail", kwargs={"pk": self.pk})
    
    def get_absolute_url_edit(self):
        return reverse("news_edit", kwargs={"pk": self.pk})

    def get_fields_name(self):
        return [field.verbose_name for field in self._meta.fields]

    def get_field_type(self, field):
        return self._meta.get_field(field).get_internal_type

    def get_fields_name_value(self):
        return [(field.name, getattr(self, field.name)) for field in self._meta.fields]

    def get_model_name(self):
        return self._meta.verbose_name.title()

    class Meta:
        verbose_name = 'Новости'
        managed = False
        db_table = 'news'
        ordering = ["-created_time"]


class NewsEn(models.Model):
    news = models.OneToOneField(News, models.DO_NOTHING, primary_key=True)
    preview_img_url = models.CharField(max_length=255) # TODO set any default value
    short_review = models.CharField(max_length=255, blank=True, null=True) # TODO set any default value
    pre_title = models.CharField(max_length=255, blank=True, null=True) # TODO set any default value
    title = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255) # TODO set any default value
    company_site_url = models.CharField(max_length=255, blank=True, null=True) # TODO set any default value
    content = models.CharField(max_length=16000)

    class Meta:
        managed = False
        db_table = 'news_en'


class NewsImg(models.Model):
    id = models.BigAutoField(primary_key=True)
    news = models.ForeignKey(News, models.DO_NOTHING)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    resolution_id = models.SmallIntegerField()
    preview_img_url = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    
    class Meta:
        managed = False
        db_table = 'news_img'


class NewsRu(models.Model):
    news = models.OneToOneField(News, models.DO_NOTHING, primary_key=True)
    preview_img_url = models.CharField(max_length=255)
    short_review = models.CharField(max_length=255, blank=True, null=True)
    pre_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    company_site_url = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=16000)

    class Meta:
        managed = False
        db_table = 'news_ru'


class NewsUk(models.Model):
    news = models.OneToOneField(News, models.DO_NOTHING, primary_key=True)
    preview_img_url = models.CharField(max_length=255)
    short_review = models.CharField(max_length=255, blank=True, null=True)
    pre_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    company_site_url = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=16000)

    class Meta:
        managed = False
        db_table = 'news_uk'


class Partner(models.Model):
    id = models.BigAutoField(primary_key=True)
    active = models.BooleanField()
    version_id = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    internal_description = models.CharField(max_length=255, blank=True, null=True)
    published = models.BooleanField()
    map_latitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    map_longitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'partner'


class PartnerCoordinates(models.Model):
    partner = models.ForeignKey(Partner, models.DO_NOTHING)
    map_latitude = models.DecimalField(max_digits=12, decimal_places=8)
    map_longitude = models.DecimalField(max_digits=12, decimal_places=8)

    class Meta:
        managed = False
        db_table = 'partner_coordinates'


class PartnerDescription(models.Model):
    partner = models.ForeignKey(Partner, models.DO_NOTHING)
    version_id = models.BigIntegerField()
    lang_abbr = models.CharField(max_length=2)
    preview_img_url = models.CharField(max_length=255)
    short_review = models.CharField(max_length=255, blank=True, null=True)
    pre_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    company_site_url = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=16000)

    class Meta:
        managed = False
        db_table = 'partner_description'


class PartnerImg(models.Model):
    id = models.BigAutoField(primary_key=True)
    partner = models.ForeignKey(Partner, models.DO_NOTHING)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    resolution_id = models.SmallIntegerField()
    preview_img_url = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'partner_img'
        unique_together = (('partner', 'lang_abbr', 'resolution_id'),)


class Promotion(models.Model):
    id = models.BigAutoField('ID', primary_key=True)
    active = models.BooleanField('Active')
    version_id = models.IntegerField('Version ID')
    created_time = models.DateTimeField('Created time', auto_now_add=True)
    updated_time = models.DateTimeField('Updated time', auto_now=True, blank=True, null=True)
    internal_description = models.CharField('Description', max_length=255, blank=True, null=True)
    published = models.BooleanField('Published')

    def get_fields_name(self):
        return [field.verbose_name for field in self._meta.fields]

    def get_field_type(self, field):
        return self._meta.get_field(field).get_internal_type

    def get_fields_name_value(self):
        return [(field.name, getattr(self, field.name)) for field in self._meta.fields]

    def get_model_name(self):
        return self._meta.verbose_name.title()


    class Meta:
        managed = False
        db_table = 'promotion'


class PromotionEn(models.Model):
    promotion = models.OneToOneField(Promotion, models.DO_NOTHING, primary_key=True)
    preview_img_url = models.CharField(max_length=255)
    short_review = models.CharField(max_length=255, blank=True, null=True)
    pre_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    company_site_url = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=16000)

    class Meta:
        managed = False
        db_table = 'promotion_en'


class PromotionImg(models.Model):
    id = models.BigAutoField(primary_key=True)
    promotion = models.ForeignKey(Promotion, models.DO_NOTHING)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    resolution_id = models.SmallIntegerField()
    preview_img_url = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'promotion_img'


class PromotionRu(models.Model):
    promotion = models.OneToOneField(Promotion, models.DO_NOTHING, primary_key=True)
    preview_img_url = models.CharField(max_length=255)
    short_review = models.CharField(max_length=255, blank=True, null=True)
    pre_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    company_site_url = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=16000)

    class Meta:
        managed = False
        db_table = 'promotion_ru'


class PromotionUk(models.Model):
    promotion = models.OneToOneField(Promotion, models.DO_NOTHING, primary_key=True)
    preview_img_url = models.CharField(max_length=255)
    short_review = models.CharField(max_length=255, blank=True, null=True)
    pre_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    img_url = models.CharField(max_length=255)
    company_site_url = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=16000)

    class Meta:
        managed = False
        db_table = 'promotion_uk'


class ServiceStation(models.Model):
    id_service_station = models.IntegerField(primary_key=True)
    version_id = models.BigIntegerField(blank=True, null=True)
    id_clients = models.IntegerField(blank=True, null=True)
    id_brands = models.IntegerField(blank=True, null=True)
    fuel_types = models.IntegerField()
    services = models.IntegerField()
    map_latitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    map_longitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    n_service_station = models.CharField(max_length=50, blank=True, null=True)
    kn_service_station = models.CharField(max_length=25, blank=True, null=True)
    region = models.CharField(max_length=30, blank=True, null=True)
    area = models.CharField(max_length=30, blank=True, null=True)
    place = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    pos_address = models.CharField(max_length=100, blank=True, null=True)
    pos_index = models.CharField(max_length=10, blank=True, null=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    vendor_id = models.CharField(max_length=64, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    azs_code = models.CharField(max_length=36, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'service_station'
    
    def __str__(self):
        return self.n_service_station


class ServiceStationTranslation(models.Model):
    id_service_station = models.ForeignKey(ServiceStation, models.DO_NOTHING, db_column='id_service_station')
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    n_service_station = models.CharField(max_length=50)
    kn_service_station = models.CharField(max_length=25)
    address = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'service_station_translation'
        unique_together = (('id_service_station', 'lang_abbr'),)


class ServiceType(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    service_id = models.SmallIntegerField()
    active = models.BooleanField()
    version_id = models.IntegerField(unique=True, blank=True, null=True)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    title = models.CharField(max_length=16)
    external_system_id = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'service_type'
        unique_together = (('service_id', 'lang_abbr'),)


class SyncState(models.Model):
    id = models.BigAutoField(primary_key=True)
    table_name = models.CharField(unique=True, max_length=128)
    last_version = models.BigIntegerField()
    updated_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_extended_version = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'sync_state'


class SyncStateByLang(models.Model):
    id = models.BigAutoField(primary_key=True)
    table_name = models.CharField(max_length=128)
    lang_abbr = models.ForeignKey(Language, models.DO_NOTHING, db_column='lang_abbr')
    last_version = models.BigIntegerField()
    updated_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_extended_version = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'sync_state_by_lang'
        unique_together = (('table_name', 'lang_abbr'),)

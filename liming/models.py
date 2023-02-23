# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import localtime



class Farmer(models.Model):
    name = models.CharField("nazwisko i imię", max_length=100)
    location = models.CharField("miejscowość", max_length=100)
    comments = models.TextField("uwagi", max_length=300, null=True, blank=True)

    def __str__(self):
        return f"{self.name} -- zam. {self.location}"

    class Meta:
        unique_together = ('name', 'location')
        ordering = ['name']
        verbose_name = "Rolnik"
        verbose_name_plural = "Rolnicy"



class GrowingField(models.Model):
    farmer = models.ForeignKey('Farmer', on_delete=models.CASCADE)
    field_number = models.CharField("numer pola", max_length=20)
    area = models.FloatField("powierzchnia pola", validators=[MinValueValidator(0.0)])
    description = models.CharField("opis pola", max_length=300, null=True, blank=True)
    parcel_number = models.CharField("numer działki", max_length=30)

    def __str__(self):
        return f"{self.field_number} (dz. {self.parcel_number} - {self.area} ha)"

    class Meta:
        unique_together = ('farmer', 'field_number', 'parcel_number')
        ordering = ['field_number']
        verbose_name = "Pole"
        verbose_name_plural = "Pola"



class ApplicationRate(models.Model):
    # rolnik i pole
    farmer = models.ForeignKey('Farmer', on_delete=models.CASCADE, verbose_name='rolnik')
    growing_field = models.ForeignKey('GrowingField', on_delete=models.CASCADE, verbose_name='pole')

    # regulacja PH (PH Adjustment)
    SOIL_AGRONOMIC_CATEGORY_CHOICES = [
        ("1", "1 - Bardzo lekka"),
        ("2", "2 - Lekka"),
        ("3", "3 - Średnia"),
        ("4", "4 - Ciężka")
    ]
    CORP_TYPE_CHOICES = [
        ("GO", "Grunty orne"),
        ("UZ", "Trwałe użytki zielone")
    ]
    pha_crop_type = models.CharField("typ uprawy", max_length=2, choices=CORP_TYPE_CHOICES, null=True, blank=True)
    pha_soil_agronomic_category = models.CharField("kategoria agronomiczna gleby", max_length=1, choices=SOIL_AGRONOMIC_CATEGORY_CHOICES, null=True, blank=True)
    pha_soil_ph_H2O = models.CharField("odczyn gleby (pHH2O)", max_length=3, choices=[(str(v/10), str(v/10)) for v in range(30,91)], null=True, blank=True)
    pha_lider_ca_application_rate_per_hectare = models.FloatField("dawka nawozu Lider Ca (t/ha)", null=True, blank=True)
    pha_lider_ca_application_rate_per_field = models.FloatField("dawka nawozu Lider Ca (t/pole)", null=True, blank=True)

    # potrzeby uprawowe (Crop Needs)
    CORP_KIND_CHOICES = [
        ("PSZ", "Pszenica"),
        ("JEC", "Jęczmień"),
        ("OWI", "Owies"),
        ("ZYT", "Żyto"),
        ("RZE", "Rzepak"),
        ("KUK", "Kukurydza kiszonka"),
        ("KUZ", "Kukurydza ziarno"),
        ("UZ", "Użytki zielone"),
        ("BOB", "Bobowate")
    ]
    EXPECTED_YIELD_CHOICES = [
        ("W", "Wysoki"),
        ("S", "Średni"),
        ("N", "Niski")
    ]
    cn_crop_kind = models.CharField("rodzaj uprawy", max_length=3, choices=CORP_KIND_CHOICES, null=True, blank=True)
    cn_expected_yield = models.CharField("spodziewany plon", max_length=1, choices=EXPECTED_YIELD_CHOICES, null=True, blank=True)
    cn_lider_mg_application_rate_per_hectare = models.FloatField("dawka nawozu Lider Mg (t/ha)", null=True, blank=True)
    cn_lider_mg_application_rate_per_field = models.FloatField("dawka nawozu Lider Mg (t/pole)", null=True, blank=True)

    # metadane
    date_of_calculation = models.DateField("data wyliczenia", null=True, blank=True)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('growing_field', 'operator')
        verbose_name = "Formularz aplikacji nawozów"
        verbose_name_plural = "Formularze aplikacji nawozów"

    def clean(self):
        if hasattr(self, 'farmer') and hasattr(self, 'growing_field') and (self.growing_field.farmer != self.farmer):
            raise ValidationError({'growing_field':(f'Wybrane pole nie należy do rolnika {self.farmer}.')})
        super().clean()

    def __str__(self):
        return f"{self.farmer}, pole: {self.growing_field} - {self.date_of_calculation} / {self.operator.first_name} {self.operator.last_name}"


    # wyliczenie dawek Lider Ca
    __al_rates_ca = {
        "1": (0.9, 0.5, 0.3, 0.1, 0.0),
        "2": (1.1, 0.8, 0.4, 0.15, 0.0),
        "3": (1.3, 1.0, 0.5, 0.25, 0.0),
        "4": (1.5, 1.1, 0.7, 0.3, 0.0)
    }
    __gl_rates_ca = {
        "all": (0.9, 0.7, 0.3, 0.15, 0.0)
    }
    __soil_ph_H2O_map = {str(v/10):0 for v in range(30,50)} | \
                    {str(v/10):1 for v in range(50,61)} | \
                    {str(v/10):2 for v in range(61,68)} | \
                    {str(v/10):3 for v in range(68,75)} | \
                    {str(v/10):4 for v in range(75,91)}

    def __get_rate_lider_ca(self, crop_type, soil_agronomic_category, soil_ph_H2O):
        if crop_type == "GO":
            # dawki dla gruntów ornych
            rates_values = self.__al_rates_ca
        elif crop_type == "UZ":
            # dawki dla użytków zielonych
            rates_values = self.__gl_rates_ca
            soil_agronomic_category = "all"
        return rates_values[soil_agronomic_category][self.__soil_ph_H2O_map[soil_ph_H2O]]


    # wyliczenie dawek Lider Mg
    __cn_rates_mg = {
        "PSZ": (0.3, 0.25, 0.2),
        "JEC": (0.3, 0.275, 0.25),
        "OWI": (0.25, 0,225, 0,2),
        "ZYT": (0.15, 0.175, 0.1),
        "RZE": (0.25, 0.2, 0.15),
        "KUK": (0.45, 0.375, 0.3),
        "KUZ": (0.7, 0.6, 0.5),
        "UZ":  (0.5, 0.4, 0.3),
        "BOB": (0.2, 0.175, 0.15)
    }
    __expected_yield_map = {"W":0, "S":1, "N":2}

    def __get_rate_lider_mg(self, crop_kind, expected_yield):
        return self.__cn_rates_mg[crop_kind][self.__expected_yield_map[expected_yield]]

    def calculate_rates(self):
        self.pha_lider_ca_application_rate_per_hectare = None
        self.pha_lider_ca_application_rate_per_field = None
        if (self.pha_crop_type is not None) and ((self.pha_crop_type=='UZ') or (self.pha_soil_agronomic_category is not None)) and (self.pha_soil_ph_H2O is not None):
            self.pha_lider_ca_application_rate_per_hectare = self.__get_rate_lider_ca(self.pha_crop_type, self.pha_soil_agronomic_category, self.pha_soil_ph_H2O)
            self.pha_lider_ca_application_rate_per_field = round(self.pha_lider_ca_application_rate_per_hectare * self.growing_field.area, 3)
        self.cn_lider_mg_application_rate_per_hectare = None
        self.cn_lider_mg_application_rate_per_field = None
        if (self.cn_crop_kind is not None) and (self.cn_expected_yield is not None):
            self.cn_lider_mg_application_rate_per_hectare = self.__get_rate_lider_mg(self.cn_crop_kind, self.cn_expected_yield)
            self.cn_lider_mg_application_rate_per_field = round(self.cn_lider_mg_application_rate_per_hectare * self.growing_field.area, 3)
        self.date_of_calculation = datetime.date.today()

    @property
    def is_lider_ca_calculated(self):
        return self.pha_lider_ca_application_rate_per_field is not None

    @property
    def is_lider_mg_calculated(self):
        return self.cn_lider_mg_application_rate_per_field is not None



class Order(models.Model):
    farmer = models.ForeignKey('Farmer', on_delete=models.CASCADE)
    client = models.CharField(max_length=202)
    growing_fields = models.CharField(max_length=200)
    lider_ca_weight = models.FloatField()
    lider_mg_weight = models.FloatField()
    lider_ca_price = models.FloatField("cena Lider Ca", validators=[MinValueValidator(0.0)])
    lider_mg_price = models.FloatField("cena Lider Mg", validators=[MinValueValidator(0.0)])
    packing_type = models.CharField("rodzaj opakowania", max_length=1, choices=[('P','Paleta'), ('B','Big bag')])
    operator = models.CharField(max_length=100)
    date = models.DateField()
    creation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'client']
        verbose_name = "Zamówienie"
        verbose_name_plural = "Zamówienia"

    @property
    def client_name(self):
        return self.client.split('\n')[0]

    @property
    def lider_ca_weight_rounded(self):
        return f"{self.lider_ca_weight:.3f}"

    @property
    def lider_mg_weight_rounded(self):
        return f"{self.lider_mg_weight:.3f}"

    @property
    def lider_ca_price_rounded(self):
        return f"{self.lider_ca_price:.2f}"

    @property
    def lider_mg_price_rounded(self):
        return f"{self.lider_mg_price:.2f}"

    @property
    def lider_ca_amount_rounded(self):
        return f"{(self.lider_ca_price * self.lider_ca_weight):.2f}"

    @property
    def lider_mg_amount_rounded(self):
        return f"{(self.lider_mg_price * self.lider_mg_weight):.2f}"

    def __str__(self):
        return f"{self.client_name} - {localtime(self.creation_time).strftime('%Y-%m-%d %H:%M:%S')} / {self.operator}"



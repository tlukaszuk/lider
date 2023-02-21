from django.contrib import admin
from .models import Farmer, GrowingField, ApplicationRate


class GrowingFieldInline(admin.TabularInline):
    model = GrowingField

class FarmerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Dane rolnika', {
            'fields': ('name', 'location', 'comments')
        }),
    )
    inlines = [GrowingFieldInline,]


class ApplicationRateAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Dane pola', {
            'fields': ('farmer', 'growing_field',)
        }),
        ('Regulacja PH', {
            'fields': ('pha_crop_type', 'pha_soil_agronomic_category', 'pha_soil_ph_H2O', 'pha_lider_ca_application_rate_per_hectare', 'pha_lider_ca_application_rate_per_field'),
        }),
        ('Potrzeby uprawowe', {
            'fields': ('cn_crop_kind', 'cn_expected_yield', 'cn_lider_mg_application_rate_per_hectare', 'cn_lider_mg_application_rate_per_field',),
        }),
        ('Metadane', {
            'fields': ('date_of_calculation', 'operator'),
        }),
    )

admin.site.register(Farmer, FarmerAdmin)
admin.site.register(ApplicationRate, ApplicationRateAdmin)

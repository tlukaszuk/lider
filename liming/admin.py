from django.contrib import admin
from .models import Farmer, GrowingField, ApplicationRate, Order


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
    list_display = ('farmer', 'growing_field', 'date_of_calculation', 'get_operator_name')

    @admin.display(description='operator', ordering='operator__last_name')
    def get_operator_name(self, obj):
        return f"{obj.operator.first_name} {obj.operator.last_name}"

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


class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Nagłówek', {
            'fields': ('farmer', 'client', 'growing_fields')
        }),
        ('Lider Ca', {
            'fields': ('lider_ca_weight', 'lider_ca_price')
        }),
        ('Lider Mg', {
            'fields': ('lider_mg_weight', 'lider_mg_price')
        }),
        ('Pakowanie', {
            'fields': ('packing_type',),
        }),
        ('Metadane', {
            'fields': ('date', 'operator'),
        }),
    )

admin.site.register(Farmer, FarmerAdmin)
admin.site.register(ApplicationRate, ApplicationRateAdmin)
admin.site.register(Order, OrderAdmin)

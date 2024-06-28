import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.db import models
from django.urls import reverse

from .models import (
	Product, OrderItem, Order,
	Address, Payment, Refund, Category
)



def make_refund_accepted(modeladmin, request, queryset):
	queryset.update(refund_request=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


def export_to_csv(modeladmin, request, queryset):
	opts = modeladmin.model._meta
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts.verbose_name)
	writer = csv.writer(response)

	fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
	# Write a first row with header information
	writer.writerow([field.verbose_name for field in fields])
	# Write data rows
	for obj in queryset:
		data_row = []
		for field in fields:
			value = getattr(obj, field.name)
			if isinstance(value, datetime.datetime):
				value = value.strftime('%d/%m/%Y')
			data_row.append(value)
		writer.writerow(data_row)
	return response

export_to_csv.short_description = 'Export to CSV'



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = [
			'name', 
			'slug', 
			'price',
			'available', 
			'created', 
			'updated'
	]
	list_filter = ['available', 'created', 'updated']
	list_editable = ['price', 'available']
	prepopulated_fields = {'slug': ('name',)}


class OrderAdmin(admin.ModelAdmin):
	list_display = [
			'user', 
			'ordered', 
			'being_delivered',
			'received',
			'refund_request',
			'refund_granted',
			'billing_address',
			'shipping_address',  
			'payment',
	]
	list_filter = [
			'user', 
			'ordered', 
			'being_delivered',
			'received',
			'refund_request',
			'refund_granted'
	]
	list_display_links = [
			'user', 
			'billing_address',
			'shipping_address',    
			'payment',
	]
	search_fields = [
		'user__username',
		'ref_code',
	]
	actions = [make_refund_accepted, export_to_csv]

class AddressAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'street_address',
		'apartment_address',
		'country',
		'zip_code',
		#'address_type',
		'default',
	]
	list_filter = [
		'default',
		#'address_type',
		'country',
	]
	search_fields = [
		'user',
		'street_address',
		'apartment_address',
		'zip_code',
	]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
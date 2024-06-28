from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django.db import models 
from django.urls import reverse
# MPTT.FIELDS IMPORT TreeForeignKey -> pip install django-mptt


PAYMENT_CHOICES = (
	('S', 'Stripe'),
	('P', 'PayPal'),
)

ADDRESS_CHOICES = (

	('B', 'Billing'),
	('S', 'Shipping'),

)
#              MPTT.Models
class Category(models.Model):
	# parent = TreeForeignKey('self', blank=True, null=True, related_name='childen', on_delete=models.CASCADE)
	name = models.CharField(max_length=30)
	description = models.CharField(max_length=200)
	image = models.ImageField(blank=True, upload_to='images/')
	slug = models.SlugField(max_length=200, unique=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)
		verbose_name = 'category'
		verbose_name_plural = 'categories'
		
	def __str__(self):
		return self.name


class Product(models.Model):
	category = models.ForeignKey(Category,
									related_name='products',
									on_delete=models.CASCADE)
	name = models.CharField(max_length=200, db_index=True)
	slug = models.SlugField(max_length=200, db_index=True)
	image = models.ImageField(upload_to='products/%Y/%m/%d',
							blank=True)
	description = models.TextField(blank=True)
	price = models.FloatField()
	quantity = models.IntegerField(default=1)
	available = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	
	class Meta:
		ordering = ('name',)
		index_together = (('id', 'slug'),)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('shop:product_detail', kwargs={'slug': self.slug})

	def get_add_to_cart_url(self):
		return reverse("shop:add-to-cart", kwargs={
				'slug': self.slug
		})

	def get_remove_from_cart_url(self):
		return reverse("shop:remove-from-cart", kwargs={
				'slug': self.slug
		})

class OrderItem(models.Model):
	user = models.ForeignKey(get_user_model(),
							 on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)


	def __str__(self):
		return f"{self.quantity} of {self.item.name}"

	def get_total_items_price(self):
		return self.quantity * self.item.price

	def get_final_price(self):
		return self.get_total_items_price()


class Order(models.Model):
	user = models.ForeignKey(get_user_model(),
							 on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=9)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	billing_address = models.ForeignKey(
		'Address', on_delete=models.SET_NULL, blank=True, null=True, related_name='billing_address',
	)
	shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True, related_name='shipping_address',
	)
	payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True,)
	payment_option = models.CharField(max_length=1, choices=PAYMENT_CHOICES )
	being_delivered = models.BooleanField(default=False)
	received = models.BooleanField(default=False)
	refund_request = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default=False)

	def __str__(self): 
		return self.user.username

	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return total


class Address(models.Model):
	user = models.ForeignKey(get_user_model(),
							 on_delete=models.CASCADE)
	street_address = models.CharField(max_length=100)
	apartment_address = models.CharField(max_length=100)
	country = CountryField(multiple=False)
	zip_code = models.CharField(max_length=100)
	address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES )
	default = models.BooleanField(default=False)


	def __str__(self):
		return self.user.username

	class Meta:
		verbose_name_plural = 'Addresses'


class Payment(models.Model):
	charge_id = models.CharField(max_length=50)
	user = models.ForeignKey(get_user_model(), 
							on_delete=models.SET_NULL, blank=True, null=True,
	)
	amount = models.FloatField()
	payment_option = models.CharField(max_length=1, choices=PAYMENT_CHOICES )
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username


class Refund(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	reason = models.TextField()
	accepted = models.BooleanField(default=False)
	email = models.EmailField()

	def __str__(self):
		return f"{self.pk}"



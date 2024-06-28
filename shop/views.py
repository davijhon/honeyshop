import json
from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, View

from .models import (
    Product,
    Order,
    OrderItem,
    Address,
    Payment,
    Refund,
)

from .forms import CheckoutForm, RefundForm
from cart.forms import CartAddProductForm


import random
import string
import stripe

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=9))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


def consulta(id):
    try:
        return Product.objects.get(id=id)
    except:
        return None


# @staff_member_required
# def admin_order_pdf(request, order_id):
# 	order = get_object_or_404(Order, id=order_id)
# 	html = render_to_string('shop/pdf.html', {'order': order})

# 	response = HttpResponse(content_type='application/pdf')
# 	response['Content-Disposition'] = 'filename="order_{}.pdf"'.format(order.id)

# 	weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')])
# 	return response


class HomePageView(ListView):
    def get(self, request, *args, **kwargs):
        context = dict()
        products = list(
            Product.objects.filter(available=True).values_list("id", flat=True)
        )
        if products:
            product1 = random.choice(products)
            products.remove(product1)
            product2 = random.choice(products)
            products.remove(product2)
            product3 = random.choice(products)
            products.remove(product3)

            context = {
                "product1": consulta(product1),
                "product2": consulta(product2),
                "product3": consulta(product3),
            }

        return render(request, "shop/index.html", context)


class ProductListView(ListView):
    model = Product
    template_name = "shop/product-list.html"
    context_object_name = "products"
    paginate_by = 4


class ServicesPageView(TemplateView):
    template_name = "shop/services.html"


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product-page.html"

    def get_context_data(self, **kwargs):
        cart_product_form = CartAddProductForm()
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context["cart_product_form"] = cart_product_form
        return context


class PaymentView(View):
    def get(self, *args, payment_option, **kwargs):
        order = Order.objects.get(
            user=self.request.user, ordered=False
        )  # Para dar dinamismo, ver min:2:35:41 // https://www.youtube.com/watch?v=YZvRrldjf1Y&t=9279s
        context = {
            "order": order,
            "payment_option": payment_option,
        }
        return render(self.request, "shop/payment.html", context)

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        payment_option = order.payment_option

        # If payment option that user is Stripe
        token = self.request.POST.get("stripeToken")
        amount = int(order.get_total() * 100)

        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(amount=amount, currency="usd", source=token)

            # Create the payment
            payment = Payment()
            payment.charge_id = charge["id"]
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # Assign the paymet to the order
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            # TODO: reference Code
            order.ref_code = create_ref_code()
            order.save()

            # messages.success(request, "Payment was successful!")
            # return redirect("shop:home")

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get("error", {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            # print(e)
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(
                self.request,
                "Something  try againwent wrong. You were not charget. Please",
            )
            return redirect("/")

        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            # print(e)
            messages.error(
                self.request, "A serius error accourred. We have been notified"
            )
            return redirect("/")


def payment_complete(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, ordered=False, id=body["orderID"])

    payment = Payment(
        user=request.user, charge_id=body["payID"], amount=order.get_total()
    )
    payment.save()

    # Assign the paymet to the order
    order_items = order.items.all()
    order_items.update(ordered=True)
    for item in order_items:
        item.save()

    order.ordered = True
    order.payment = payment
    # TODO: reference Code
    order.ref_code = create_ref_code()
    order.save()

    if order.ordered:
        subject = "ElectroShop - Invoice no. {}".format(order.id)
        html_message = render_to_string("shop/oder_email.html")
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = request.user.email

        mail.send_mail(
            subject, plain_message, from_email, [to], html_message=html_message
        )

    messages.success(request, "Payment was successful!")
    return redirect("shop:home")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            # form
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                "form": form,
                "order": order,
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user, address_type="S", default=True
            )

            billing_address_qs = Address.objects.filter(
                user=self.request.user, address_type="B", default=True
            )

            return render(self.request, "shop/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("shop:cart")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                # print(form.cleaned_data)TESTEAR SI FUNCIONA EL FORM
                # print("The form is valid")TESTEAR SI FUNCIONA EL FORM
                street_address = form.cleaned_data.get("street_address")
                apartment_address = form.cleaned_data.get("apartment_address")
                country = form.cleaned_data.get("country")
                zip_code = form.cleaned_data.get("zip_code")
                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get("payment_option")

                billing_address = Address(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip_code=zip_code,
                    address_type="B",
                )

                billing_address.save()
                order.billing_address = billing_address
                order.payment_option = payment_option
                order.save()

                if payment_option == "S":
                    return redirect("shop:payment", payment_option="Stripe")
                elif payment_option == "P":
                    return redirect("shop:payment", payment_option="PayPal")
                else:
                    messages.warning(self.request, "Invalid payment option")
                    return redirect("shop:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("shop:cart")


class CartPageView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                "object": order,
            }
            return render(self.request, "shop/cart.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {"form": form}
        return render(self.request, "shop/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_request = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("shop:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("shop:request-refund")


def Erro404View(request, exception):
    return render(request, "shop/404.html")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # Check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("shop:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("shop:cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("shop:cart")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("shop:cart")
        else:
            messages.info(request, "This item not in your cart.")
            return redirect("shop:product_detail", slug=slug)
    else:
        messages.info(request, "You do not have an activate order.")
        return redirect("shop:product_detail", slug=slug) 


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated from your cart.")
            return redirect("shop:cart")
        else:
            messages.info(request, "This item not in your cart.")
            return redirect("shop:product_detail", slug=slug)
    else:
        messages.info(request, "You do not have an activate order.")
        return redirect("shop:product_detail", slug=slug)

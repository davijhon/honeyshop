from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ( 
	View, 
	TemplateView, 
	ListView, 
	DetailView 
)

from blog.models import (
	Post, 
	Category, 
	Web, 
	Contacto,
	Suscriptor,
	FAQ,
)

from blog.forms import ContactoForm


class BlogPageView(ListView):
	model = Post
	template_name = 'blog/blog.html'
	context_object_name = 'posts'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		categories = Category.objects.all()
		ctx = super().get_context_data(**kwargs)
		ctx['categories'] = categories
		return ctx


class CategoryPageView(View):

	def get(self, request, pk, *args, **kwargs):
		categories = Category.objects.all()
		posts = Post.objects.filter(categoria_id=pk)
		context = {
			'posts': posts,
			'categories': categories,
		}
		print(posts)
		return render(request, 'blog/category.html', context)


class SearchResultsListView(ListView):
	model = Post
	context_object_name = 'post_list'
	template_name = 'blog/search.html'
	paginate_by = 3

	def get_queryset(self):
		query = self.request.GET.get('q')
		return Post.objects.filter(
			Q(titulo__icontains=query) | Q(autor__nombre__icontains=query)
		)


class PostDetailView(DetailView):
	model = Post
	template_name = 'blog/blog-post.html'

	def get_context_data(self, **kwargs):
		categories = Category.objects.all()
		ctx = super().get_context_data(**kwargs)
		ctx['categories'] = categories
		return ctx



class ContactView(View):
	def get(self, request, *args, **kwargs):
		contact = Web.objects.filter(estado=True).latest('fecha_creacion')
		form = ContactoForm()
		context = {

			'contact': contact,
			'form': form

		}
		return render(request, 'blog/contact.html', context)

	def post(self, request, *args, **kwargs):
		form = ContactoForm(self.request.POST or None)

		try:
			if form.is_valid():
				nombre = form.cleaned_data.get('nombre')
				correo = form.cleaned_data.get('correo')
				asunto = form.cleaned_data.get('asunto')
				mensaje = form.cleaned_data.get('mensaje')

				contact = Contacto(
					nombre=nombre,
					correo=correo,
					asunto=asunto,
					mensaje=mensaje,
				)
				contact.save()
			messages.success(self.request, "Your message was send it successful!")
			return redirect("/")
		except ObjectDoesNotExist:
			messages.error(self.request, "Something wrong accourred. try again")
			return redirect("shop:cart")


class Suscribir(View):
    def post(self, request, *args, **kwargs):
        correo = request.POST.get('correo')
        Suscriptor.objects.create(correo=correo)
        asunto = 'GRACIAS POR SUSCRIBIRTE A BLOG.DEV!'
        mensaje = 'Te haz suscrito exitosamente a HoneyShop, Gracias por tu preferencia!!!'
        try:
            send_mail(asunto,mensaje,'apikey',[correo])
        except:
            pass

        return redirect('shop:home')


class FAQView(ListView):
	model = FAQ
	template_name = 'blog/FAQ.html'
	context_object_name = 'questions'


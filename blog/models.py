from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class ModelBlogBase(models.Model):
    id = models.AutoField(primary_key=True)
    estado = models.BooleanField("Estado", default=True)
    fecha_creacion = models.DateField(
        "Fecha de Creación", auto_now=False, auto_now_add=True
    )
    fecha_modificacion = models.DateField(
        "Fecha de Modificación", auto_now=True, auto_now_add=False
    )
    fecha_eliminacion = models.DateField(
        "Fecha de Eliminación", auto_now=True, auto_now_add=False
    )

    class Meta:
        abstract = True


class Category(ModelBlogBase):
    nombre = models.CharField("Nombre de la Categoría", max_length=100, unique=True)
    imagen_referencial = models.ImageField("Imagen Referencial", upload_to="categoria/")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Autor(ModelBlogBase):
    nombre = models.CharField("Nombres", max_length=100)
    apellidos = models.CharField("Apellidos", max_length=120)
    email = models.EmailField("Correo Electrónico", max_length=200)
    descripcion = models.TextField("Descripción")
    imagen_referencial = models.ImageField(
        "Imagen Referencial", null=True, blank=True, upload_to="autores/"
    )
    web = models.URLField("Web", null=True, blank=True)
    facebook = models.URLField("Facebook", null=True, blank=True)
    twitter = models.URLField("Twitter", null=True, blank=True)
    instagram = models.URLField("Instagram", null=True, blank=True)

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"

    def __str__(self):
        return "{0}, {1}".format(self.apellidos, self.nombre)


class Post(ModelBlogBase):
    titulo = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion = models.TextField("Descripción")
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Category, on_delete=models.CASCADE)
    contenido = CKEditor5Field("Text", config_name="extends")
    imagen_referencial = models.ImageField(
        "Imagen Referencial", upload_to="imagenes/", max_length=255
    )
    publicado = models.BooleanField("Publicado / No Publicado", default=False)
    fecha_publicacion = models.DateField("Fecha de Publicación")

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.titulo


class Web(ModelBlogBase):
    nosotros = models.TextField("Nosotros")
    telefono = models.CharField("Teléfono", max_length=10)
    email = models.EmailField("Correo Electrónico", max_length=200)
    direccion = models.CharField("Dirección", max_length=200)

    class Meta:
        verbose_name = "Web"
        verbose_name_plural = "Webs"

    def __str__(self):
        return self.nosotros


class RedesSociales(ModelBlogBase):
    facebook = models.URLField("Facebook")
    twitter = models.URLField("Twitter")
    instagram = models.URLField("Instagram")

    class Meta:
        verbose_name = "Red Social"
        verbose_name_plural = "Redes Sociales"

    def __str__(self):
        return self.facebook


class Contacto(ModelBlogBase):
    nombre = models.CharField("Nombre", max_length=100)
    correo = models.EmailField("Correo Electrónico", max_length=200)
    asunto = models.CharField("Asunto", max_length=100)
    mensaje = models.TextField("Mensaje")

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"

    def __str__(self):
        return self.asunto


class Suscriptor(ModelBlogBase):
    correo = models.EmailField(max_length=200)

    class Meta:
        verbose_name = "Suscriptor"
        verbose_name_plural = "Suscriptores"

    def __str__(self):
        return self.correo


class FAQ(ModelBlogBase):
    STATUS = (("True", "True"), ("False", "False"))
    question = models.CharField(max_length=200)
    answer = models.TextField()
    status = models.CharField(max_length=200, choices=STATUS)

    def __str__(self):
        return self.question

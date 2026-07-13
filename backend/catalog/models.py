from django.db import models
from core.models import BaseModel


class Categoria(BaseModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(BaseModel):
    codigo = models.CharField('Código', max_length=50, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    iva_porcentaje = models.DecimalField('IVA %', max_digits=4, decimal_places=2, default=15.00)
    stock = models.IntegerField('Stock', default=0)
    stock_minimo = models.IntegerField('Stock mínimo', default=0, help_text='Alertar cuando el stock baje de esta cantidad')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos', verbose_name='Categoría')
    imagen = models.ImageField('Imagen', upload_to='productos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
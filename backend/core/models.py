from django.contrib.auth.models import Permission
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager que excluye automáticamente registros con is_active=False."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class BaseModel(models.Model):
    """Clase abstracta base con campos de auditoría y soft delete."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado (sin borrarlo físicamente)."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restaura un registro eliminado."""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


class MenuItem(BaseModel):
    """Elemento de navegación del sistema. Módulo (parent=None) o submódulo."""
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children',
        verbose_name='Módulo padre',
        help_text='Null = módulo raíz en el sidebar',
    )
    name = models.CharField('Nombre', max_length=100)
    icon = models.CharField(
        'Icono', max_length=50, blank=True,
        help_text='Clase Bootstrap Icon (ej: bi-shield-lock)',
    )
    url_name = models.CharField(
        'URL interna', max_length=200, blank=True,
        help_text='Nombre de ruta Django (ej: security:user_list)',
    )
    order = models.PositiveIntegerField('Orden', default=0)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name='Permisos requeridos',
        help_text='Visible solo para usuarios con estos permisos. Vacío = visible para todos.',
    )

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Elemento de menú'
        verbose_name_plural = 'Elementos del menú'

    def __str__(self):
        return self.name

    @property
    def is_module(self):
        """True si es un módulo raíz (sin padre)."""
        return self.parent is None

    @property
    def is_submodule(self):
        """True si es un submódulo (tiene padre)."""
        return self.parent is not None

    def _check_permissions(self, user):
        """Verifica si el usuario tiene los permisos requeridos."""
        if not self.permissions.exists():
            return True
        return user.has_perms([
            f'{p.content_type.app_label}.{p.codename}'
            for p in self.permissions.select_related('content_type').only(
                'codename', 'content_type__app_label'
            )
        ])

    def has_access(self, user):
        """¿Puede el usuario ver este elemento en el menú?"""
        if not self.is_active:
            return False
        if self.is_module:
            children = MenuItem.all_objects.filter(parent=self, is_active=True)
            if children.exists():
                return any(child.has_access(user) for child in children)
        return self._check_permissions(user)

    def accessible_children(self, user):
        """Retorna los hijos que el usuario puede ver."""
        if not self.is_module:
            return MenuItem.objects.none()
        children = MenuItem.all_objects.filter(parent=self, is_active=True).order_by('order')
        return [child for child in children if child.has_access(user)]
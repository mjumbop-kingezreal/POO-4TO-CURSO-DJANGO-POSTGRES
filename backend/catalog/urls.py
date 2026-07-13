from django.urls import path
from .views import (
    CategoriaCreateView, CategoriaDeactivateView, CategoriaListView, CategoriaUpdateView,
    ProductoCreateView, ProductoDeactivateView, ProductoListView, ProductoUpdateView,
)

app_name = 'catalog'
urlpatterns = [
    path('categories/', CategoriaListView.as_view(), name='categoria_list'),
    path('categories/create/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categories/<int:pk>/edit/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categories/<int:pk>/deactivate/', CategoriaDeactivateView.as_view(), name='categoria_deactivate'),

    path('products/', ProductoListView.as_view(), name='producto_list'),
    path('products/create/', ProductoCreateView.as_view(), name='producto_create'),
    path('products/<int:pk>/edit/', ProductoUpdateView.as_view(), name='producto_update'),
    path('products/<int:pk>/deactivate/', ProductoDeactivateView.as_view(), name='producto_deactivate'),
]
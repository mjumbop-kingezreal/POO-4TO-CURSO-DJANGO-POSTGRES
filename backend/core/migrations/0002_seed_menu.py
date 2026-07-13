from django.db import migrations


def seed_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')

    modules = [
        {'name': 'Dashboard', 'icon': 'bi-speedometer2', 'url_name': 'home',
         'children': []},
        {'name': 'Seguridad', 'icon': 'bi-shield-lock', 'url_name': '',
         'children': [
            {'name': 'Usuarios', 'icon': 'bi-people', 'url_name': ''},
            {'name': 'Roles', 'icon': 'bi-person-badge', 'url_name': ''},
        ]},
        {'name': 'Cat\u00e1logo', 'icon': 'bi-box', 'url_name': '',
         'children': [
            {'name': 'Categor\u00edas', 'icon': 'bi-tags', 'url_name': ''},
            {'name': 'Productos', 'icon': 'bi-box-seam', 'url_name': ''},
        ]},
        {'name': 'Clientes', 'icon': 'bi-people', 'url_name': '',
         'children': [
            {'name': 'Listado de Clientes', 'icon': 'bi-list-ul', 'url_name': ''},
        ]},
        {'name': 'Ventas', 'icon': 'bi-cart', 'url_name': '',
         'children': [
            {'name': 'Facturas', 'icon': 'bi-receipt', 'url_name': ''},
            {'name': 'Reportes', 'icon': 'bi-graph-up', 'url_name': ''},
        ]},
    ]

    for idx, mod in enumerate(modules, start=1):
        module = MenuItem.objects.create(
            name=mod['name'],
            icon=mod['icon'],
            url_name=mod['url_name'],
            order=idx,
        )
        for jdx, sub in enumerate(mod['children'], start=1):
            MenuItem.objects.create(
                parent=module,
                name=sub['name'],
                icon=sub['icon'],
                url_name=sub['url_name'],
                order=jdx,
            )


def reverse_seed(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    MenuItem.all_objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_menu, reverse_seed),
    ]
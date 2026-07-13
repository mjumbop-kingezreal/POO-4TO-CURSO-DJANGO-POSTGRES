import json
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.utils import timezone
from django.views.generic import TemplateView
from catalog.models import Producto
from customers.models import Cliente
from invoicing.models import Factura


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = "/security/login/"
    redirect_field_name = "redirect_to"
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.localdate()
        inicio_hoy = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
        fin_hoy = inicio_hoy + timedelta(days=1)

        ctx['facturas_hoy'] = Factura.objects.filter(
            fecha_emision__gte=inicio_hoy, fecha_emision__lt=fin_hoy,
            is_active=True
        ).count()

        inicio_mes = timezone.make_aware(datetime.combine(hoy.replace(day=1), datetime.min.time()))
        ventas_mes = Factura.objects.filter(
            fecha_emision__gte=inicio_mes, is_active=True
        ).aggregate(total=Sum('total'))
        ctx['ventas_mes'] = ventas_mes['total'] or 0

        ctx['total_clientes'] = Cliente.objects.count()
        ctx['stock_bajo'] = Producto.objects.filter(stock__lt=F('stock_minimo')).count()

        ctx['ultimas_facturas'] = Factura.objects.select_related('cliente').filter(
            is_active=True
        ).order_by('-fecha_emision')[:5]

        desde = hoy - timedelta(days=6)
        inicio_desde = timezone.make_aware(datetime.combine(desde, datetime.min.time()))
        facturas_periodo = Factura.objects.filter(
            fecha_emision__gte=inicio_desde, fecha_emision__lt=fin_hoy,
            is_active=True
        )

        labels = [(desde + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        data = [0.0] * 7
        for f in facturas_periodo:
            dia_local = timezone.localtime(f.fecha_emision).date()
            idx = (dia_local - desde).days
            if 0 <= idx < 7:
                data[idx] += round(float(f.total), 2)

        ctx['chart_labels_json'] = json.dumps(labels)
        ctx['chart_data_json'] = json.dumps(data)
        return ctx

from io import BytesIO
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from xhtml2pdf import pisa
from .models import Factura


class PDFMixin:
    pdf_template = None
    pdf_filename = 'reporte.pdf'

    def render_pdf(self, context):
        html_str = self.render_to_string(self.pdf_template, context)
        result = BytesIO()
        pdf = pisa.pisaDocument(
            BytesIO(html_str.encode('UTF-8')),
            dest=result,
            encoding='UTF-8',
            link_callback=self._link_callback,
        )
        if pdf.err:
            return HttpResponse('Error al generar PDF', status=500)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{self.pdf_filename}"'
        response.write(result.getvalue())
        return response

    def _link_callback(self, uri, rel):
        import os
        from django.conf import settings
        from django.contrib.staticfiles import finders

        if uri.startswith(settings.STATIC_URL):
            relative_path = uri.replace(settings.STATIC_URL, '').lstrip('/')
            # Try to use Django's staticfiles finders first
            absolute_path = finders.find(relative_path)
            if absolute_path:
                return absolute_path
                
            path = os.path.join(settings.BASE_DIR, relative_path)
            if not os.path.exists(path) and getattr(settings, 'STATICFILES_DIRS', None):
                path = os.path.join(
                    settings.STATICFILES_DIRS[0],
                    relative_path
                )
            return path
        return uri

    def render_to_string(self, template, context):
        from django.template.loader import render_to_string
        return render_to_string(template, context, request=self.request)


class InvoicePDFView(LoginRequiredMixin, PermissionRequiredMixin, View, PDFMixin):
    permission_required = 'invoicing.view_factura'
    pdf_template = 'invoicing/reports/invoice_pdf.html'

    def get(self, request, pk):
        factura = get_object_or_404(Factura.all_objects.select_related('cliente', 'usuario'), pk=pk)
        detalles = factura.detalles.select_related('producto').all()
        self.pdf_filename = f'factura_{factura.numero}.pdf'
        return self.render_pdf({'factura': factura, 'detalles': detalles})


class ReportsIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'invoicing/reports/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['today'] = timezone.localtime()
        return ctx


class DailyClosePDFView(LoginRequiredMixin, PermissionRequiredMixin, View, PDFMixin):
    permission_required = 'invoicing.view_factura'
    pdf_template = 'invoicing/reports/daily_close_pdf.html'

    def get(self, request):
        hoy = timezone.localdate()
        inicio = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
        fin = inicio + timedelta(days=1)
        self.pdf_filename = f'cierre_diario_{hoy.strftime("%Y%m%d")}.pdf'

        facturas = Factura.all_objects.filter(
            fecha_emision__gte=inicio, fecha_emision__lt=fin
        ).select_related('cliente').order_by('fecha_emision')

        activas = facturas.filter(is_active=True)
        resumen = activas.aggregate(
            total=Sum('total'), subtotal=Sum('subtotal'),
            iva=Sum('iva_total'), cantidad=Count('id'),
        )
        por_metodo = list(activas.values('metodo_pago').annotate(
            total=Sum('total'), cantidad=Count('id')
        ).order_by('metodo_pago'))

        return self.render_pdf({
            'fecha': hoy,
            'facturas': facturas,
            'activas': activas,
            'resumen': resumen,
            'por_metodo': por_metodo,
            'anuladas': facturas.filter(is_active=False).count(),
        })


class InvoiceListPDFView(LoginRequiredMixin, PermissionRequiredMixin, View, PDFMixin):
    permission_required = 'invoicing.view_factura'
    pdf_template = 'invoicing/reports/invoice_list_pdf.html'

    def get(self, request):
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        hoy = timezone.localdate()

        if desde:
            inicio = timezone.make_aware(datetime.combine(
                datetime.strptime(desde, '%Y-%m-%d').date(), datetime.min.time()))
        else:
            inicio = timezone.make_aware(datetime.combine(hoy.replace(day=1), datetime.min.time()))

        if hasta:
            fin = timezone.make_aware(datetime.combine(
                datetime.strptime(hasta, '%Y-%m-%d').date(), datetime.min.time())) + timedelta(days=1)
        else:
            fin = timezone.make_aware(datetime.combine(hoy, datetime.min.time())) + timedelta(days=1)

        facturas = Factura.all_objects.filter(
            fecha_emision__gte=inicio, fecha_emision__lt=fin
        ).select_related('cliente').order_by('-fecha_emision')

        activas = facturas.filter(is_active=True)
        resumen = activas.aggregate(
            total=Sum('total'), subtotal=Sum('subtotal'),
            iva=Sum('iva_total'), cantidad=Count('id'),
        )

        self.pdf_filename = f'facturas_{inicio.strftime("%Y%m%d")}_al_{fin.strftime("%Y%m%d")}.pdf'

        return self.render_pdf({
            'facturas': facturas,
            'activas': activas,
            'resumen': resumen,
            'anuladas': facturas.filter(is_active=False).count(),
            'desde': inicio.date(),
            'hasta': (fin - timedelta(days=1)).date(),
        })

#! /usr/bin/python
# -*- encoding: utf-8 -*-

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import cStringIO as StringIO
import cgi
from xhtml2pdf.document import pisaDocument

def render_to_pdf(template_src, context_dict):
    '''
    Renderiza el template con el contexto.
    Envía al cliente la Respuesta HTTP del contenido PDF para
    el template renderizado.
    '''
    
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    #pdf = pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    pdf = pisaDocument(StringIO.StringIO(html.encode("utf-8")), result, encoding="utf-8")
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    
    return HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from django.template import Context

class ProductSelect(Widget):
    class Media:
        css = {
            'all': ('css/chosen.css',)
        }
        js = (
            'js/chosen.jquery.js',
            'js/chosen.ajax.js',
            'js/madjango-admin-widget.js'
            )

    def __init__(self, attrs=None, choices=()):
        super(ProductSelect, self).__init__(attrs)


    def render(self, name, value, attrs=None, choices=()):
        template = get_template('madjango-input-select-widget.html')
        context = Context({
            'name':name,
            'value':value
            })


        if value is None:
            value = ''

        return mark_safe(template.render(context))

from five  import grok
import martian

import z3c.form
import plone.z3cform

from Acquisition import aq_inner

class FormWrapper(grok.View):
    """
    Base wrapper to z3c.form, just register a class which set the form attribute.
    You have a classical grok.View instance with an attribute ``form_instance``
    which is the wrapped z3c.form.form.Form instance.
    >>> class Klass(FormWrapper):
    ...      context = grok.context(someinterface)
    ...      form = FormKlass
    You can also override the layer attribute.
    """
    martian.baseclass()
    grok.implements(plone.z3cform.interfaces.IFormWrapper)

    form, index, request_layer = None, None, None

    def __init__(self,  *args, **kwargs):
        grok.View.__init__(self, *args, **kwargs)
        self.switch_on_form_layer()
        self.form_instance = self.form(aq_inner(self.context), self.request)
        self.form_instance.__name__ = self.__name__
        if getattr(self, 'template', None):
            self.index = self.template

    def switch_on_form_layer(self):
        """
        A call to 'switch_on' is required before we can use/render z3c.forms within Zope 2.
        """
        layer = getattr(self, 'request_layer', None)
        if not layer:
            layer = z3c.form.interfaces.IFormLayer
        plone.z3cform.z2.switch_on(self, layer)

    def update(self, *args, **kwargs):
        self.compute_widgets()
        grok.View.update(self, *args, **kwargs)
        
    def compute_widgets(self):
        """
        shortcut 'widget' dictionary for all fieldsets
        stolen from plone.autoform_instance/plone/autoform_instance/view.py
        """
        self.form_instance.update()
        self.form_instance.w = {}
        for k, v in self.form_instance.widgets.items():
            self.form_instance.w[k] = v
        groups = []
        self.form_instance.fieldsets = {}
        if getattr(self.form_instance, 'groups', None):
            for idx, groupFactory in enumerate(self.form_instance.groups):
                group = groupFactory(self.form_instance.context, 
                                     self.form_instance.request,
                                     self.form_instance)
                group.update()
                for k, v in group.widgets.items():
                    self.form_instance.w[k] = v
                groups.append(group)
                group_name = getattr(group, '__name__', str(idx))
                self.form_instance.fieldsets[group_name] = group
            self.form_instance.groups = tuple(groups)

    def render_form(self):
        """
        call this method in templates to have the full html rendered form
        """
        self.compute_widgets()
        return self.form_instance.render()

    # stolen from plone.directives.form.form.DisplayForm
    def render(self, *args, **kwargs):
        template = getattr(self, 'template', None)
        if template is not None:
            return self.template.render()
        return zope.publisher.publish.mapply(self.render, (), self.request)
    render.base_method = True 


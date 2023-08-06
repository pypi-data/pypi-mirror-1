from five  import grok

import z3c.form
import plone.z3cform

from zope.interface import alsoProvides, noLongerProvides
from zope.interface.interfaces import IInterface
from Acquisition import aq_inner
from plone.z3cform.interfaces import IFormWrapper 
from z3c.form.interfaces import IFormLayer
from zope.publisher.interfaces.browser import IBrowserApplicationRequest

import zope
import Products

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
    grok.baseclass()
    grok.context(zope.interface.Interface)
    grok.implements(IFormWrapper)
    form               = None # z3c.form class
    index              = None # template
    view_request_layer = None # wrapper view layer
    form_request_layer = None # form instance layer

    def __init__(self,  *args, **kwargs):
        grok.View.__init__(self, *args, **kwargs)
        if self.view_request_layer: self.addLayer(self.view_request_layer)
        self.form_instance = self.form(aq_inner(self.context), self.request)
        self.form_instance.__name__ = self.__name__
        self.switch_on_form_layer()
        if getattr(self, 'template', None):
            self.index = self.template

    def switch_on_form_layer(self, layer=None):
        """
        we need that to render forms in zope2 !
        """
        if not layer:
            layer = IFormLayer
            if self.form_request_layer:
                layer = self.form_request_layer
        # check that the layer is interface:
        if IInterface.providedBy(layer):
            if not layer.providedBy(self.request):
                # inspired by plone.z3cform.z2, without the IBrowserApplicationRequest filter.
                # request must be patched for forms to be rendered in Zope2
                # maybe we had IBrowserApplicationRequest, so we need to fix the request.
                if not plone.z3cform.z2.IFixedUpRequest.providedBy(self.request):
                    # try to fix locale, it can fail with attribute error weither which kind of request it is
                    try:
                        self.request.locale = plone.z3cform.z2.setup_locale(self.request)
                    except: 
                        pass
                    plone.z3cform.z2.add_getURL(self.request)
                    plone.z3cform.z2.decode.processInputs(self.request)
                    self.addLayer(plone.z3cform.z2.IFixedUpRequest)
                self.addLayer(layer)

    def addLayer(self, layer):
        alsoProvides(self.request, layer)

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
            for idx, group in enumerate(self.form_instance.groups):
                #group = groupFactory(self.form_instance.context,
                #                     self.form_instance.request,
                #                     self.form_instance)
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

class PloneFormWrapper(FormWrapper):
    """
    Use that nice plone with fieldsets and kss template 
    explicitly rather than the basic z3c.form template
    """
    grok.baseclass()
    view_request_layer = Products.CMFDefault.interfaces.ICMFDefaultSkin

class PloneForm(plone.z3cform.fieldsets.extensible.ExtensibleForm, z3c.form.form.Form):
    grok.baseclass()



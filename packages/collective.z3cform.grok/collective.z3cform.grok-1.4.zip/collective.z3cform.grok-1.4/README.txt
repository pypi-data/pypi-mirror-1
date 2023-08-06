Introduction
=============

    This package enables the use of z3c forms in grok.View style inside a plone environment.

    Note that you have two wrappers and a basic form class:

    - *FormWrapper* to use the basic ``z3c.form`` template
    - *PloneFormWrapper*  is a basic z3c.form wrapper with some plone integration (fieldsets & kss) (from ``plone.app.z3cform``)
    - *PloneForm*  is a basic z3c.form with some plone integration (fieldsets & groups) (from plone.app.z3cform)
    - A *TestCase* to test your code with z3cform.grok with either using directly itself or by sublassing it

Basic Usage
=============

Declare a form in 'foo.py' module
::


    >>> import plone.z3cform.fieldsets.extensible.ExtensibleForm$
    >>> import z3c.form.form.Form
    >>> class Myform(plone.z3cform.fieldsets.extensible.ExtensibleForm, z3c.form.form.Form):
    ...    """A z3c.form"""
    ...    ingoreContext = True or False # override me

Note that ``collective.z3cform.grok.grok.PloneForm`` is a shortcut to the previous declaration, see implementation.

Then a Wrapper
::

    >>> from collective.z3cform.grok.grok import PloneFormWrapper
    >>> class myview(PloneFormWrapper):
    ...     form = Myform


Write a basic template, in foo_templates/myview.py, for example:
::

    <tal metal:use-macro="context/main_template/macros/master">
      <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:tal="http://xml.zope.org/namespaces/tal"
        xmlns:metal="http://xml.zope.org/namespaces/metal"
        xmlns:i18n="http://xml.zope.org/namespaces/i18n"
        i18n:domain="nmd.sugar.forms"
        xml:lang="en" lang="en"
        tal:define="lang language"
        tal:attributes="lang lang; xml:lang lang">
        <body>
          <metal:main fill-slot="body">
            <tal:block tal:content="structure python:view.render_form()"></tal:block>
          </metal:main>
        </body>
      </html>
    </tal>


Et voila, you can access your form @

    - http://url/@@myview



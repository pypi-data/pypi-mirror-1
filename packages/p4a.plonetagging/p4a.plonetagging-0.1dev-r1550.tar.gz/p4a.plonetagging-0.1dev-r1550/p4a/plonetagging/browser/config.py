from p4a.plonetagging import interfaces
from zope.formlib import form
from Products.Five.formlib import formbase

class TaggingConfiglet(formbase.PageEditForm):
    form_fields = form.FormFields(interfaces.ITaggingConfig)

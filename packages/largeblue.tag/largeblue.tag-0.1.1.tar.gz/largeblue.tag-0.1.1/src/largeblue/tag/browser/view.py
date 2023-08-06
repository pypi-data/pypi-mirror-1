import logging

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib.form import EditForm as BaseEditForm
from zope.formlib.form import Fields

from largeblue.tag.interfaces import ITag


class EditForm(BaseEditForm):
    form_fields = Fields(ITag).select('tagstring')


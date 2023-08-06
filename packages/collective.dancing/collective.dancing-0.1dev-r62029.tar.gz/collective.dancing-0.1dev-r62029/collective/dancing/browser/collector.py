import zope.publisher
from zope import schema
import zope.schema.vocabulary
from zope import component
from zope import interface
from zope.app.pagetemplate import viewpagetemplatefile
from z3c.form import field
from z3c.form import form, subform
import z3c.form.interfaces
import z3c.form.browser.select
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import Products.CMFPlone.utils
from collective.singing.interfaces import ICollector
from collective.singing.browser import crud
import collective.singing.interfaces
import collective.singing.z2

import OFS.interfaces

from collective.dancing import MessageFactory as _
from collective.dancing import collector
from collective.dancing.browser import controlpanel

class ManageCollectorsForm(crud.CrudForm):
    """Crud form for collectors.
    """
    update_schema = field.Fields(ICollector).select('title')
    view_schema = field.Fields(ICollector).select('title')

    def get_items(self):
        return [(ob.getId(), ob) for ob in self.context.objectValues()]

    def add(self, data):
        name = Products.CMFPlone.utils.normalizeString(
            data['title'].encode('utf-8'), encoding='utf-8')
        self.context[name] = collector.Collector(
            name, data['title'])
        return self.context[name]

    def remove(self, (id, item)):
        self.context.manage_delObjects([id])

    def link(self, item, field):
        if field == 'title':
            return item.absolute_url()

class CollectorAdministrationView(BrowserView):
    __call__ = ViewPageTemplateFile('controlpanel.pt')

    label = _(u'Collector administration')
    back_link = controlpanel.back_to_controlpanel

    def contents(self):
        collective.singing.z2.switch_on(self)
        return ManageCollectorsForm(self.context, self.request)()

collector_fields = field.Fields(
    collective.singing.interfaces.ICollector).select('title', 'optional')

def heading(self):
    if self.label:
        return "<h%s>%s</h%s>" % (self.level, self.label, self.level)

def prefix(self):
    return self.__class__.__name__ + '-'.join(self.context.getPhysicalPath())

class EditTopicForm(subform.EditSubForm):
    """Edit a single collector.
    """
    component.adapts(Products.ATContentTypes.content.topic.ATTopic,
                     None,
                     z3c.form.interfaces.IEditForm)
    template = viewpagetemplatefile.ViewPageTemplateFile('subform.pt')

    fields = field.Fields(
        schema.TextLine(__name__='title', title=_(u"Title")))

    @property
    def css_class(self):
        return "subform subform-level-%s" % self.level

    @property
    def label(self):
        return u"Collection: %s" % self.context.title

    prefix = property(prefix)

    def contents_bottom(self):
        return u'<a href="%s/criterion_edit_form">Edit the Smart Folder</a>' % (
            self.context.absolute_url())

    heading = heading

class AddToCollectorForm(form.Form):
    ignoreContext = True
    ignoreRequest = True
    template = viewpagetemplatefile.ViewPageTemplateFile('subform.pt')
    css_class = "addform"

    prefix = property(prefix)
    heading = heading

    @property
    def label(self):
        return u"Add item to %s" % self.context.title

    @property
    def fields(self):
        factory = schema.Choice(
            __name__='factory',
            title=_(u"Type"),
            vocabulary=zope.schema.vocabulary.SimpleVocabulary(
                [zope.schema.vocabulary.SimpleTerm(value=f, title=f.title)
                 for f in collector.collectors])
            )

        title = schema.TextLine(
            __name__='title',
            title=_(u"Title"))

        return z3c.form.field.Fields(factory, title)

    @z3c.form.button.buttonAndHandler(_('Add'), name='add')
    def handle_add(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = z3c.form.form.EditForm.formErrorsMessage
            return
        obj = data['factory'](self.context.get_next_id(), data['title'])
        self.context[obj.id] = obj
        self.status = _(u"Item added successfully.")

class DeleteFromCollectorForm(form.Form):
    template = viewpagetemplatefile.ViewPageTemplateFile('subform.pt')
    css_class = "deleteform"

    prefix = property(prefix)

    @z3c.form.button.buttonAndHandler(_('Remove block'), name='remove')
    def handle_remove(self, action):
        self.context.aq_parent.manage_delObjects([self.context.id])
        self.status = _("Item successfully deleted.")

class AbstractEditCollectorForm(object):
    level = 1
    
    @property
    def css_class(self):
        return "subform subform-level-%s" % self.level

    heading = heading

    def update(self):
        super(AbstractEditCollectorForm, self).update()
        addform = AddToCollectorForm(self.context, self.request)
        addform.level = self.level
        addform.update()

        deleteforms = []
        for item in self.context.objectValues():
             deleteform = DeleteFromCollectorForm(item, self.request)
             deleteform.update()
             deleteform.level = self.level + 1
             deleteforms.append(deleteform)

        editforms = []
        for item in self.context.objectValues():
             subform = component.getMultiAdapter(
                (item, self.request, self.parent_form),
                z3c.form.interfaces.ISubForm)
             subform.update()
             subform.level = self.level + 1
             editforms.append(subform)

        self.subforms = []
        for editform, deleteform in zip(editforms, deleteforms):
            self.subforms.extend((editform, deleteform))
        self.subforms.append(addform)

class EditCollectorForm(AbstractEditCollectorForm, subform.EditSubForm):
    """Edit a single collector.
    """
    component.adapts(collective.singing.interfaces.ICollector,
                     zope.publisher.interfaces.http.IHTTPRequest,
                     z3c.form.interfaces.IEditForm)
    template = viewpagetemplatefile.ViewPageTemplateFile(
        'form-with-subforms.pt')
    fields = collector_fields

    prefix = property(prefix)

    @property
    def label(self):
        return u"Collector block: %s" % self.context.title

    @property
    def parent_form(self):
        return self.parentForm

class EditRootCollectorForm(AbstractEditCollectorForm, form.EditForm):
    """Edit a single collector.
    """
    template = viewpagetemplatefile.ViewPageTemplateFile(
        'form-with-subforms.pt')
    fields = collector_fields

    @property
    def parent_form(self):
        return self

class CollectorEditView(BrowserView):
    __call__ = ViewPageTemplateFile('controlpanel.pt')

    def label(self):
        return _(u'Edit ${collector}',
                 mapping=dict(collector=self.context.title))

    def back_link(self):
        return dict(label=_(u"Up to Collector administration"),
                    url=self.context.aq_inner.aq_parent.absolute_url())

    def contents(self):
        collective.singing.z2.switch_on(self)
        form = EditRootCollectorForm(self.context, self.request)
        return '<div class="collector-form">' + form() + '</div>'

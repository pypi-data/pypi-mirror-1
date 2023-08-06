import datetime

from zope import component
from zope.app.pagetemplate import viewpagetemplatefile
import Acquisition
import Zope2.App.startup
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import field
from z3c.form import form
import collective.singing.interfaces
import collective.singing.z2
import collective.singing.message
import collective.singing.browser.subscribe

from collective.dancing import MessageFactory as _
from collective.dancing.channel import Subscription

class SubscribeForm(collective.singing.browser.subscribe.Subscribe):
    factory = Subscription

class Subscribe(BrowserView):
    template = ViewPageTemplateFile('skeleton.pt')
    label = _(u"Subscribe")

    def __call__(self):
        collective.singing.z2.switch_on(self)
        return self.template()

    def contents(self):
        subscribe = SubscribeForm(self.context.aq_inner, self.request)
        return subscribe()

class Confirm(BrowserView):
    template = ViewPageTemplateFile('skeleton.pt')
    contents = ViewPageTemplateFile('status.pt')

    label = _(u"Confirming your subscription")

    def __call__(self):
        secret = self.request.form['secret']
        subscriptions = self.context.aq_inner.subscriptions

        if secret in subscriptions:
            for subscription in subscriptions[secret]:
                m = collective.singing.interfaces.ISubscriptionMetadata(
                    subscription)
                m['pending'] = False
            self.status = _(u"You confirmed your subscription successfully.")
        else:
            self.status = _(u"Your subscription isn't known to us.")

        return self.template()

class Unsubscribe(BrowserView):
    template = ViewPageTemplateFile('skeleton.pt')
    contents = ViewPageTemplateFile('status.pt')

    label = _(u"Unsubscribe")

    def __call__(self):
        secret = self.request.form['secret']
        subscriptions = self.context.aq_inner.subscriptions
        
        if secret in subscriptions:
            del subscriptions[secret]
            self.status = _(u"You unsubscribed successfully.")
        else:
            self.status = _(u"You aren't subscribed to this channel.")

        return self.template()

class IncludeHiddenSecret(object):
    def render(self):
        html = super(IncludeHiddenSecret, self).render()
        secret = self.request.get('secret')
        if secret is not None:
            index = html.find('</form>')
            html = (html[:index] +
                    '<input type="hidden" name="secret" value="%s"' % secret +
                    html[index:])
        return html

class SubscriptionEditForm(IncludeHiddenSecret, form.EditForm):
    template = viewpagetemplatefile.ViewPageTemplateFile('form.pt')    

    removed = False

    @property
    def prefix(self):
        return '%s.%s.' % (
            self.context.channel.name, self.context.metadata['format'])

    @property
    def label(self):
        subscription = self.context
        value = subscription.channel.title
        if len(subscription.channel.composers) > 1:
            format = subscription.metadata['format']
            value = u"%s (%s)" % (
                value, subscription.channel.composers[format].title)
        return value

    @property
    def fields(self):
        if self.context.channel.collector is None:
            return field.Fields()
        return field.Fields(self.context.channel.collector.schema)

    buttons, handlers = form.EditForm.buttons, form.EditForm.handlers
    
    @button.buttonAndHandler(_('Unsubscribe'), name='unsubscribe')
    def handle_unsubscribe(self, action):
        secret = self.request.form['secret']
        del self.context.channel.subscriptions[secret]
        self.removed = self.context
        self.status = _(u"You unsubscribed successfully.")

class SubscriptionAddForm(IncludeHiddenSecret, form.Form):
    template = viewpagetemplatefile.ViewPageTemplateFile('form.pt')
    ignoreContext = True
    
    added = None
    format = None # set by parent form

    @property
    def prefix(self):
        return '%s.%s.' % (self.context.name, self.format)

    @property
    def label(self):
        value = self.context.title
        if len(self.context.composers) > 1:
            value = u"%s (%s)" % (
                value, self.context.composers[self.format].title)
        return value

    @property
    def fields(self):
        fields = field.Fields(self.context.composers[self.format].schema,
                              prefix='composer.')
        if self.context.collector is not None:
            fields += field.Fields(self.context.collector.schema,
                                   prefix='collector.')
        return fields

    @button.buttonAndHandler(_('Subscribe'), name='subscribe')
    def handle_subscribe(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = form.AddForm.formErrorsMessage
            return

        extract = lambda d, prefix: dict(
            [(key.split('.', 1)[-1], value) for (key, value) in d.items()
             if key.startswith(prefix)])

        comp_data = extract(data, 'composer.')
        coll_data = extract(data, 'collector.')

        composer = self.context.composers[self.format]
        secret = collective.singing.subscribe.secret(
            self.context,
            composer,
            comp_data,
            self.request)
        secret_provided = self.request.form.get('secret')
        if secret_provided and secret != secret_provided:
            self.status = _(
                u"There seems to be an error with the information you entered.")
            return

        metadata = dict(
            format=self.format,
            date=datetime.datetime.now(),
            pending=not secret_provided)

        self.added = collective.dancing.channel.Subscription(
            self.context, secret, comp_data, coll_data, metadata)

        if not secret_provided:
            msg = composer.render_confirmation(self.added)
            status, status_msg = collective.singing.message.dispatch(msg)
            if status != u'sent':
                self.status = _(u"We're sorry, but there seems to be an error. "
                                u"Please try again later.\n"
                                u"(${error})",
                                mapping=dict(error=status_msg))
                return

        self.context.subscriptions[secret].append(self.added)
        self.status = _(u"You subscribed successfully.")

class Subscriptions(BrowserView):
    __call__ = ViewPageTemplateFile('skeleton.pt')
    contents_template = ViewPageTemplateFile('subscriptions.pt')

    label = _(u"My subscriptions")
    status = u""

    def contents(self):
        collective.singing.z2.switch_on(self)

        secret = self.request.form.get('secret')
        subscriptions, channels = self._subscriptions_and_channels(secret)

        # Assemble the list of edit forms
        self.subscription_editforms = [
            SubscriptionEditForm(s, self.request) for s in subscriptions]

        # Assemble the list of add forms
        self.subscription_addforms = []
        for format, channel in channels:
            addform = SubscriptionAddForm(channel, self.request)
            addform.format = format
            self.subscription_addforms.append(addform)

        # The edit forms might have deleted a subscription.  We'll
        # take care of this while updating them:
        for form in self.subscription_editforms:
            form.update()
            if form.removed:
                subscription = form.context
                name = subscription.channel.name
                addform = SubscriptionAddForm(
                    subscription.channel, self.request)
                addform.format = subscription.metadata['format']
                addform.update()
                self.subscription_addforms.append(addform)
            elif form.status != form.noChangesMessage:
                self.status = form.status

        # Let's update the add forms now.  One of them may have added
        # a subscription:
        for form in self.subscription_addforms:
            form.update()
            subscription = form.added
            if subscription is not None:
                editform = SubscriptionEditForm(
                    subscription, self.request)
                editform.update()
                self.subscription_editforms.append(editform)
                self.status = _(u"You subscribed successfully.")
            elif form.status:
                self.status = form.status

        return self.contents_template()

    def _subscriptions_and_channels(self, secret):
        subscriptions = []
        channels_and_formats = []

        for channel in component.getUtility(
            collective.singing.interfaces.IChannelLookup)():
            channel_subs = channel.subscriptions

            subscribed_formats = []
            if secret is not None and secret in channel_subs:
                subs = channel_subs[secret]
                subscriptions.extend(subs)
                subscribed_formats = [s.metadata['format'] for s in subs]

            for format in channel.composers.keys():
                if format not in subscribed_formats:
                    channels_and_formats.append((format, channel))

        return subscriptions, channels_and_formats

from zope.component import getUtility
import zope.event
from zope.lifecycleevent import ObjectModifiedEvent
from Products.Five.formlib.formbase import EditForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.formlib.form import FormFields
from zope.formlib.form import action
from zope.formlib.form import applyChanges
from zope.formlib.form import haveInputWidgets
from simplon.plone.currency.interfaces import IGlobalCurrencySettings
from simplon.plone.currency.interfaces import ICurrencyManager
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from simplon.plone.currency.currencies import currencies

try:
    from plone.app.form.validators import update_only_validator
except ImportError:
    # XXX This will be part of plone.app.form 1.1
    def update_only_validator(form, action):
        """Only validate an action when updating.

        This allows you to create an action without having formlib render a
        button for it.
        """
        return "form_result" not in form.__dict__


def GlobalCurrencySettingsFactory(context=None):
    return getUtility(ICurrencyManager)


class ControlPanel(EditForm):
    template = ViewPageTemplateFile("controlpanel.pt")

    form_fields = FormFields(IGlobalCurrencySettings)
    label = u"Currency management"
    description = u""
    form_name = u"Currency management"

    def currencies(self):
        config=GlobalCurrencySettingsFactory()

        def morph(cur):
            return dict(
                    code=cur.code,
                    symbol=currencies[cur.code][1],
                    rate=cur.rate,
                    description=currencies[cur.code][0],
                    protected=cur.code==config.currency)

        return [morph(cur) for cur in config.currencies.values()]

    @action(_("Apply"), condition=haveInputWidgets)
    def handle_edit_action(self, action, data):
        message=IStatusMessage(self.request)
        config=GlobalCurrencySettingsFactory()
        oldcurrency=config.currency

        if applyChanges(self.context, self.form_fields, data, self.adapters):
            newcurrency=config.currency
            if newcurrency!=oldcurrency:
                config.currency=oldcurrency
                config.SwitchCurrency(newcurrency)
            zope.event.notify(ObjectModifiedEvent(self.context))
            message.addStatusMessage(
                _("made_changes",
                    default=u"Changes applied"),
                type="info")

        else:
            message.addStatusMessage(
                _("no_changes",
                    default=u"Nothing changed"),
                type="info")



    @action(_("Delete"), condition=update_only_validator)
    def handle_delete_action(self, action, data):
        todo=[str(cur) for cur in self.request.form["currencies"]]
        config=GlobalCurrencySettingsFactory()
        message=IStatusMessage(self.request)

        succes=False
        for code in todo:
            if code!=config.currency:
                try:
                    del config.currencies[code]
                    succes=True
                except KeyError:
                    message.addStatusMessage(
                            _("remove_bogus_currency",
                                default=u"Failed to remove currency ${code}",
                                mapping=dict(code=code)),
                            type="error")

        if succes:
            message.addStatusMessage(
                    _("currencies_removed",
                        default=u"Currencies have been removed"),
                    type="info")


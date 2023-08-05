from Acquisition import aq_parent, aq_inner
import zope.event
from zope.lifecycleevent import ObjectModifiedEvent
from zope.interface import implements
from Products.Five.formlib.formbase import AddFormBase
from Products.Five.formlib.formbase import EditFormBase
from simplon.plone.currency.browser.interfaces import ICurrencyAdding
from simplon.plone.currency.interfaces import ICurrencyInformation
from simplon.plone.currency.currency import Currency
from Acquisition import Implicit
from Products.Five import BrowserView
from Products.CMFPlone import PloneMessageFactory as _
from zope.formlib.form import FormFields
from zope.formlib.form import applyChanges
from zope.formlib.form import action
from zope.formlib.form import haveInputWidgets
from zope.traversing.interfaces import ITraversable
from zope.component import adapts
from zope.component import getUtility
from zope.component import getMultiAdapter
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from zope.publisher.interfaces.browser import IBrowserRequest
from simplon.plone.currency.interfaces import ICurrencyManager
from plone.app.form.validators import null_validator

class CurrencyAdding(Implicit, BrowserView):
    implements(ICurrencyAdding)

    contentName = _(u"Currency")
    request = None
    context = None

    __allow_access_to_unprotected_subobjects__ = True

    def add(self, content):
        """Add the currency to the schema
        """
        currencies=getUtility(ICurrencyManager).currencies
        currencies.addItem(content)

    def nextURL(self):
        parent = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((parent, self.request), name=u"absolute_url"))
        return url + "/@@currency-controlpanel"

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False

    def addingInfo(self):
        return ()

    def isSingleMenuItem(self):
        return False

    def hasCustomAddView(self):
        return False


class CurrencyAddForm(AddFormBase):
    """An add form for currencies.
    """
    form_fields = FormFields(ICurrencyInformation)
    label = _(u"Add Currency")
    description = _(u"Register a new currency in your site")
    form_name = _(u"Configure currency")
    fieldset = "schema"

    def create(self, data):
        currency = Currency(data["code"])
        del data["code"]
        applyChanges(currency, self.form_fields, data)
        return currency

    def nextURL(self):
        parent = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((parent, self.request), name=u"absolute_url"))
        return url + "/@@currency-controlpanel"



class CurrencyEditForm(EditFormBase):
    """An edit form for LDAP properties.
    """
    form_fields = FormFields(ICurrencyInformation)
    label = _(u"Edit Currency")
    description = _(u"Edit a currency.")
    form_name = _(u"Configure currency")
    fieldset = "schema"

    @action(_("Apply"), condition=haveInputWidgets)
    def handle_edit_action(self, action, data):
        # Override the edit action since we want a redirect after edit
        # and a different status message
        message=IStatusMessage(self.request)
        manager=getUtility(ICurrencyManager)

        if manager.currency==self.context.code:
            message.addStatusMessage(
                _("can_not_edit_base_currency",
                    default=u"You can not edit the base currency"),
                type="error")

        if applyChanges(self.context, self.form_fields, data, self.adapters):
            zope.event.notify(ObjectModifiedEvent(self.context))
            message.addStatusMessage(
                    _("currency_updated",
                        default=u"Currency ${code} modified.",
                        mapping=dict(code=self.context.code)),
                    type="info")
        else:
            message.addStatusMessage(
                _("no_changes",
                    default=u"Nothing changed"),
                type="info")

        self.request.response.redirect(self.nextURL())
        return ""


    @action(_(u"label_cancel", default=u"Cancel"),
                             validator=null_validator, name=u'cancel')
    def handle_cancel_action(self, action, data):
        self.request.response.redirect(self.nextURL())
        return ""


    def nextURL(self):
        parent = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((parent, self.request), name=u"absolute_url"))
        return url + "/@@currency-controlpanel"


class CurrencyNamespace(object):
    """Currencies traversing.
    """
    implements(ITraversable)
    adapts(ISiteRoot, IBrowserRequest)

    def __init__(self, context, request=None):
        self.context=context
        self.request=request


    def traverse(self, name, ignore):
        currencies = getUtility(ICurrencyManager).currencies
        return currencies[name].__of__(self.context)


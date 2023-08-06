from zope.component import getUtility, queryUtility
from collective.addtofolder.interfaces import IAddMenuConfiguration
from plone.app.contentmenu import menu
from Products.CMFPlone import PloneMessageFactory as _
from zope.i18nmessageid.message import Message
from zope.i18n import translate


def _safe_unicode(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8', 'ignore')
    return text

def allow_addtofolder(self):
    if queryUtility(IAddMenuConfiguration, name='addmenuconfig'):
        menuconfig = getUtility(IAddMenuConfiguration, name='addmenuconfig')
        allow = menuconfig.allowAddToParent
    else:
        allow = False
    return allow

def patched_available(self):
    itemsToAdd = self._itemsToAdd()
    showConstrainOptions = self._showConstrainOptions()

    allow = allow_addtofolder(self)
    if not allow and \
        self._addingToParent() and not self.context_state.is_default_page():
        return False

    return (len(itemsToAdd) > 0 or showConstrainOptions)

def patched_title(self):
    itemsToAdd = self._itemsToAdd()
    showConstrainOptions = self._showConstrainOptions()

    if showConstrainOptions or len(itemsToAdd) > 1:
        if allow_addtofolder(self) and self._addingToParent():
            return _(u'label_add_new_item_in_folder', default=u'Add to folder')
        else:
            return _(u'label_add_new_item', default=u'Add item')
    elif len(itemsToAdd) == 1:
        fti=itemsToAdd[0][1]
        title = fti.Title()
        if isinstance(title, Message):
            title = translate(title, context=self.request)
        else:
            title = translate(_safe_unicode(title),
                              domain='plone',
                              context=self.request)
        return _(u'label_add_type', default='Add ${type}',
                 mapping={'type' : title})
    else:
        return _(u'label_add_new_item', default=u'Add item')

def patched_description(self):
    itemsToAdd = self._itemsToAdd()
    showConstrainOptions = self._showConstrainOptions()
    if showConstrainOptions or len(itemsToAdd) > 1:
        if allow_addtofolder(self) and self._addingToParent():
            return _(u'title_add_new_items_inside_folder', default=u'Add new items in the same folder as this item')
        else:
            return _(u'title_add_new_items_inside_item', default=u'Add new items inside this item')
    elif len(itemsToAdd) == 1:
        return itemsToAdd[0][1].Description()
    else:
        return _(u'title_add_new_items_inside_item', default=u'Add new items inside this item')


menu.FactoriesSubMenuItem.available = patched_available
menu.FactoriesSubMenuItem.description = patched_description
menu.FactoriesSubMenuItem.title = patched_title

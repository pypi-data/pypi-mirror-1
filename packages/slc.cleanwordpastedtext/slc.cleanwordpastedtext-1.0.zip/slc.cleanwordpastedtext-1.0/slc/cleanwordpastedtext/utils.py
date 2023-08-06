import logging

from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner

from Products.Archetypes.Widget import RichWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError
from Products.CMFCore.utils import getToolByName

log = logging.getLogger('slc.cleanwordpastedtext/utils.py')

def clean_word_text(text):
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('<p></p>', '')
    text = text.replace('<p>&nbsp;</p>', '')
    text = text.replace(u'<p class="MsoNormal">&nbsp;</p>', '')
    text = text.replace('\n', '')
    text = text.replace('\r', '')
    text.strip();
    text = sanitize(text, document_cleaner())
    text = text.replace('\n', "")
    text = text.replace('<p></p>', '')
    if text.find('<p/>') == 0:
        # For the strange case where the sanitized text startѕ with <p/>
        text = text[4:]
    return text

def update_object_history(context, comment):
    REQUEST = context.REQUEST
    pr = getToolByName(context, 'portal_repository')
    if pr.isVersionable(context):
        if ((pr.supportsPolicy(context, 'at_edit_autoversion')) or \
                REQUEST.get('cmfeditions_save_new_version', None)):
            try:
                context.portal_repository.save(obj=context, comment=comment)
            except FileTooLargeToVersionError:
                putils = getToolByName(context, 'plone_utils')
                putils.addPortalMessage(
                    _("Versioning for this file has been disabled because it is too large"), 
                    type="warn")
        return 'success'

def get_unicode_text(text):
    for encoding in ['utf-8', 'utf-16', 'cp1252']:
        try:
            return unicode(text, )
        except UnicodeDecodeError:
            pass

def get_rich_text_fields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]

def document_cleaner():
    # This could be made configurable with a persistent utility or
    # plone.registry, but for now there is no time...
    return Cleaner(
                page_structure = False,
                remove_unknown_tags = False,
                safe_attrs_only = True,
                allow_tags = [ "br", "blockquote", "a", "em", "p", "strong"],
                scripts = False,
                javascript = False,
                comments = False,
                style = False,
                links = False, 
                meta = False,
                processing_instructions = False,
                frames = False,
                annoying_tags = False)

def sanitize(input, cleaner):
    fragments=html.fragments_fromstring(input)
    output=[]

    for fragment in fragments:
        if isinstance(fragment, basestring):
            output.append(fragment)
        else:
            try:
                cleaned=cleaner.clean_html(fragment)
                output.append(etree.tostring(cleaned, encoding=unicode))
            except AssertionError:
                # This happens if the cleaner tries to strip the top-level
                # element
                output.extend(filter(None, [fragment.text, fragment.tail]))
                continue

    return u"".join(output)



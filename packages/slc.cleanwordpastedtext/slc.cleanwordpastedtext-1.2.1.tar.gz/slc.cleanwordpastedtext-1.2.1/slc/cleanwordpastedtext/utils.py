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
    text = sanitize(text)
    # Make another iteration, because in some cases, an embedded comment remains.
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = sanitize(text)
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
                allow_tags = [ "blockquote", "a", "img", "em", "p", "strong",
                            "h3", "h4", "h5", "ul", "ol", "li", "sub", "sup",
                            "abbr", "acronym", "dl", "dt", "dd", "cite",
                            "dft", "br", "table", "tr", "td", "th", "thead",
                            "tbody", "tfoot" ],
                safe_attrs_only = True,
                add_nofollow = True,
                scripts = False,
                javascript = False,
                comments = False,
                style = False,
                links = False, 
                meta = False,
                processing_instructions = False,
                frames = False,
                annoying_tags = False
                )
                

def remove_empty_tags(doc):
    """Removes all empty tags from a HTML document. Javascript editors
    and browsers have a nasty habit of leaving stray tags around after
    their contents have been removed. This function removes all such
    empty tags, leaving only valid empty tags.

    In addition consecutive <br/> tags are folder into a single tag.
    This forces whitespace styling to be done using CSS instead of via an
    editor, which almost always produces better and more consistent results.
    """
    legal_empty_tags = frozenset(["br", "hr", "img", "input"])

    if hasattr(doc, "getroot"):
        doc=doc.getroot()

    def clean(doc):
        victims=[]
        for el in doc.iter():
            if el.tag=="br" and not el.tail:
                try:
                    preceding=el.itersiblings(preceding=True).next()
                    if preceding.tag==el.tag:
                        victims.append(el)
                        continue
                except StopIteration:
                    pass

            if el.tag in legal_empty_tags:
                continue

            if len(el)==0 and (el.text is None or not el.text.strip()):
                victims.append(el)
                continue

        if victims and victims[0]==doc:
            doc.clear()
            return 0
        else:
            for victim in victims:
                victim.getparent().remove(victim)

        return len(victims)

    while clean(doc):
        pass

    return doc


def wrap_text(doc):
    """Make sure there is no unwrapped text at the top level. Any bare text
    found is wrapped in a `<p>` element.
    """
    def par(text):
        el=etree.Element("p")
        el.text=text
        return el
        
    if doc.text:
        doc.insert(0, par(doc.text))

    insertions=[]
    for i in range(len(doc)):
        el=doc[i]
        if el.tail:
            insertions.append((i, par(el.tail)))
            el.tail=None

    for (index, el) in reversed(insertions):
        doc.insert(index+1, el)


ANCHORS = etree.XPath("descendant-or-self::a | descendant-or-self::x:a",
                      namespaces={'x':html.XHTML_NAMESPACE})

def force_link_target(doc, target="_blank"):
    """Force a target on links in a HTML document. If the `None` is
    given as target all target attributes are removed instead."""
    for el in ANCHORS(doc):
        if target is None:
            if "target" in el.attrib:
                del el.attrib["target"]
        else:
            el.set("target", target)


def sanitize(input, cleaner=document_cleaner()):
    """Cleanup markup using a given cleanup configuration."""
    if "body" not in cleaner.allow_tags:
        cleaner.allow_tags.append("body")

    input=u"<html><body>%s</body></html>" % input
    document=html.document_fromstring(input)
    bodies=[e for e in document if html._nons(e.tag)=="body"]
    body=bodies[0]

    cleaned=cleaner.clean_html(body)
    remove_empty_tags(cleaned)
    wrap_text(cleaned)
    force_link_target(cleaned)

    output=u"".join([etree.tostring(fragment, encoding=unicode)
                     for fragment in cleaned.iterchildren()])
    return output



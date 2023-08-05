import re
from gettext import GNUTranslations
from threading import local
from mako.ext.babelplugin import extract as extract_mako
from StringIO import StringIO
import os.path

format_re = re.compile(r"\{(\d+)\}");
settings = local()
translations = {}
translations_path = '%s.mo'

def format(text, vals):
    return format_re.sub(lambda m: str(vals[int(m.group(1))]), text)

def gettext(a):
    return settings.translation.gettext(a)
    
def ngettext(a,b,c):
    return settings.translation.ngettext(a,b,c)
    
def setlanguage(lang):
    t = translations.get(lang, None)
    if not t:
        t = GNUTranslations(open(translations_path % lang))
        translations[lang] = t
    settings.lang = lang
    settings.translation = t

def preprocessor(template):
    template = unicode(template)
    buf = []
    start = 0
    end = len(template)
    idx = template.find(u'$${')
    while idx >= 0:
        buf.append(template[start:idx])
        cnt = 1
        e = idx+3 # len('$${')
        for i in range(e, end):
            if template[i] == u'{':
                cnt += 1
            elif template[i] == u'}':
                cnt -= 1
                if not cnt:
                    break
        else:
            # Put tail to the result,
            # mako itself will report error
            break 
        parts = template[e:i].split(u'|', 1)
        if len(parts) > 1:
            text, tail = parts
            buf.append(u'${format(gettext(u"""')
            buf.append(text)
            buf.append(u'"""),(')
            buf.append(tail)
            buf.append(u'))}')
        else:
            text = parts[0]
            buf.append(u'${gettext(u"""')
            buf.append(text)
            buf.append(u'""")}')
        start = i + 1
        idx = template.find('$${', start)
    if start < end:
        buf.append(template[start:end])
    buf.append('<%! from makolang import format, gettext, ngettext %>')
    return u''.join(buf)
    
def extract_makolang(fileobj, keywords, comment_tags, options):
    template = preprocessor(fileobj.read())
    return extract_mako(StringIO(template), keywords, comment_tags, options)

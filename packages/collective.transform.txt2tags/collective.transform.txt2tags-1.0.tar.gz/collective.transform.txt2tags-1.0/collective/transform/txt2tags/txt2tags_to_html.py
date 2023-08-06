# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import itransform
from txt2tags import process_source_file, convert_this_files

def _safe_unicode(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8', 'replace')
    return text


class Txt2tagsToHtml:
    """Transform which converts from txt2tags to xhtml"""

    __implements__ = itransform

    __name__ = "txt2tags_to_html"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/x-txt2tags',), tab_width = 4):
        self.config = {
            'inputs' : inputs,
            'tab_width' : 4
        }
        self.config_metadata = {
            'inputs' : ('list',
                        'Inputs',
                        'Input(s) MIME type. Change with care.'),
            'tab_width' : ('string',
                           'Tab width',
                           'Number of spaces for a tab in the input')
            }
        if name:
            self.__name__ = name
        
    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        #text = _safe_unicode(orig)
        #if not isinstance(text, unicode):
        #    text = unicode(text, 'utf-8', 'replace')
        text = _safe_unicode(orig)
        
        lines = text.split("\n")
        if lines[:3] != ['','','']:
            #disable txt2tag's first three lines, let plone manage title, author, etc.
            lines = ['','',''] + lines
        conf, outlist = process_source_file(contents=lines)
        conf['headers']=0
        conf['target']='xhtml'
        conf['encoding']='uft-8'
        conf['toc-level']=3
        textlines, allconf = convert_this_files([(conf,outlist)])
        text = "\n".join(textlines)
            
        data.setData(text)
        return data

def register():
    return Txt2tagsToHtml()

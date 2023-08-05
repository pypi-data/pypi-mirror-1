#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

#import release
#__version__ = release.version
#__author__ = release.author
#__email__ = release.email
#__copyright__ = release.copyright
#__license__ = release.license

from formencode.htmlgen import html as T
import elementtree.ElementTree as ET
#import StringIO
try:
    import pkg_resources
except:
    logger.warn("pkg_resources undefined, template's location must be relative to rootPath" )

import os
import sys

# ------------------------------------------------------------------------------
class TurboHtmlPy:
    extension = "htmlpy"

    def __init__(self, extra_vars_func = None, options = {}):
        self.get_extra_vars = extra_vars_func
        self.usePrettyPrint = options.get('htmlpy.prettyprint', False) or options.get('tidy', False)
        self.indentation = options.get('htmlpy.prettyprint_indent', '  ')
        self.slotRaiseOnUndef = options.get('htmlpy.slotRaiseOnUndef', False)
        self.encoding = options.get('htmlpy.encoding', 'utf-8')
        self.rootPath = options.get('htmlpy.rootPath', None)
        
#        self.compiledTemplates = {}
    
    def _evalTemplate(self, template, locals = None, globals = None, basemodule = None, isLocation = True):
        txt = template
        if isLocation:
            if template.startswith('.'):
                template = basemodule + template
            else :
                basemodule = template[:template.rfind('.')]
            divider = template.rfind(".")
            if divider > -1:
                package = template[0:divider]
                basename = template[divider+1:]
            else:
                raise ValueError, "All templates must be in a package"
            if pkg_resources:
                filename = pkg_resources.resource_filename(package, "%s.%s" % (basename, self.extension))
            else :
                filename = '%s.%s' % (os.path.join(self.rootPath, *template.split('.')), self.extension)
                #filename = '%s.%s' % (os.path.join(*template.split('.')), self.extension)
            txt = file(filename, 'rU').read()
        try:
            node = eval(txt, locals, globals)
            if isinstance(node, tuple):
                node = node[0]
        except Exception:
            exc = sys.exc_info()
            if (isLocation):
                loc = len(template) > 20 and ("..." + template[-20:]) or template
            else:
                loc = template[:20]+ "..."
            raise exc[0], "template=%s / %s" % (loc, exc[1]), exc[2] 
        if (node is not None) and (node.tag == 'hpy:define'):
            slot = locals['slot']
            for c in node :
                setattr(slot, c.tag, c)
            node = self._evalTemplate(str(node.attrib['into']), locals, basemodule = basemodule)
        return node
        
    
    def _include_tag(self, template, locals = None, globals = None):
        return self._evalTemplate( template, locals, globals)

#    def _include_kid(self, __stan_vars, **kwargs):
#        import kid
#
#        # sanitize variables so we don't pass reserved words to kid
#        reserved = dir(kid.BaseTemplate)
#        sv = dict([(k, v) for (k, v) in __stan_vars.items() if k not in reserved ])
#        kwargs.update(sv)
#        
#        template = kid.Template(**kwargs)
#        return T.xml(template.serialize())
                
    def render(self, info, format = "xhtml", fragment = False, template = None, isLocation=True):
        """
        Renders the template to a string using the provided info.
        
        @param info dict of variables to pass into template
        @param format "xhtml", "xml" or anything else
        @param template template to render
        @param isLocation True if template is a location of the template,
                          False if template is the text/content of the template 
        """
        if template is None:
            return None
        el = self.transform(info, template, isLocation=isLocation)
        if el is None:
            str = ''
        elif self.usePrettyPrint :
            str = self.prettyprint(el, indent = self.indentation)
        else :
            #print ET.ElementTree(el)._write(StringIO, el, self.encoding, {})
            str = self.write(el, self.encoding)

        #append header
        if not(fragment):
            if format == 'xhtml' :
                header = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
                str = header + str
            if format == 'xml' or format == 'xhtml' :
                header = '<?xml version="1.0" encoding="%s"?>\n\n' % self.encoding
                str = header + str
        return str


    def load_template(self, templatename):
        """ unused but required by tg """
        #TODO implement caching
        pass
    
    def transform(self, info, template, isLocation=True):
        """
        This method is not required for most uses of templates. 
        It is specifically used for efficiently inserting widget 
        output into Kid pages. It does the same thing render does, 
        except the output is ElementTree Elements rather than 
        a string.

        @param info dict of variables to pass into template (define the attrinutes of 'vars')
        @param template template to render
        @param isLocation True if template is a location of the template,
                          False if template is the text/content of the template 
        """        
        locals = Namespace()
        
        try:
            import turbogears.widget.Widget as Widget
            for key, value in info.items():
                if issubclass(value.__class__, Widget):
                    locals[key] = value.insert
        except Exception, exc:
            logger.info("can't create TG Widget shortcut", exc)
            
        locals['vars'] = Context('vars', info)
        if self.get_extra_vars :
            locals['xtra'] = Context('xtra', self.get_extra_vars()) # turbogears.view.stdvars()
            if hasattr(locals['xtra'], 'std') :
                locals['std'] = Context('std', locals['xtra'].std)
                locals['std'].std = locals['std'] # for compatibitkity with 0.3a
        locals['hpy__include'] = lambda template: self._include_tag(template, None, locals)
        locals['hpy__kid'] = lambda **kwargs: self._include_kid(__stan_vars = info, **kwargs)
        locals['hpy__pi'] = ET.ProcessingInstruction
        locals['hpy__xml'] = ET.XML
        locals['hpy__raw'] = RawData
        locals['hpy__cdata'] = CData
        locals['hpy__comment'] = ET.Comment
        locals['hpy__cond'] = self.cond
        locals['slot'] = Slot(self.slotRaiseOnUndef)
        locals['True'] = True
        locals['true'] = True
        locals['False'] = False
        locals['false'] = False
        locals['None'] = None
        root = self._evalTemplate(template, locals, isLocation=isLocation)
        #self.cnv_ElementGenerator(root)
        return root
        
    def cond(self, condition, onTrue, onFalse=None):
        if condition:
            return onTrue
        return onFalse
    
    ##
    # Writes the element tree to a file, as XML.
    #
    # @param file A file name, or a file object opened for writing.
    # @param encoding Optional output encoding (default is US-ASCII).

    def write(self, node, encoding="us-ascii"):
        class dummy:
            pass
        data = []
        file = dummy()
        file.write = data.append
        if not encoding:
            encoding = "us-ascii"
        elif encoding != "utf-8" and encoding != "us-ascii":
            file.write("<?xml version='1.0' encoding='%s'?>\n" % encoding)
        self._write(file, node, encoding)
        return "".join(data)

    def _write(self, file, node, encoding):
        namespaces={}
        # write XML to file
        tag = node.tag
        if tag is ET.Comment:
            file.write("<!-- %s -->" % ET._escape_cdata(node.text, encoding))
        elif tag is ET.ProcessingInstruction:
            file.write("<?%s?>" % ET._escape_cdata(node.text, encoding))
        elif tag is CData:
            file.write("<![CDATA[%s]]>" % node.text.encode(encoding))
        elif tag is RawData:
            file.write(node.text.encode(encoding))
        else:
            items = node.items()
            xmlns_items = [] # new namespaces in this scope
            try:
                if isinstance(tag, ET.QName) or tag[:1] == "{":
                    tag, xmlns = ET.fixtag(tag, namespaces)
                    if xmlns: xmlns_items.append(xmlns)
            except TypeError:
                ET._raise_serialization_error(tag)
            file.write("<" + ET._encode(tag, encoding))
            if items or xmlns_items:
                items.sort() # lexical order
                for k, v in items:
                    try:
                        if isinstance(k, ET.QName) or k[:1] == "{":
                            k, xmlns = ET.fixtag(k, namespaces)
                            if xmlns: xmlns_items.append(xmlns)
                    except TypeError:
                        ET._raise_serialization_error(k)
                    try:
                        if isinstance(v, ET.QName):
                            v, xmlns = ET.fixtag(v, namespaces)
                            if xmlns: xmlns_items.append(xmlns)
                    except TypeError:
                        ET._raise_serialization_error(v)
                    file.write(" %s=\"%s\"" % (ET._encode(k, encoding),
                                               ET._escape_attrib(v, encoding)))
                for k, v in xmlns_items:
                    file.write(" %s=\"%s\"" % (ET._encode(k, encoding),
                                               ET._escape_attrib(v, encoding)))
            if node.text or len(node):
                file.write(">")
                if node.text:
                    file.write(ET._escape_cdata(node.text, encoding))
                for n in node:
                    self._write(file, n, encoding, namespaces)
                file.write("</" + ET._encode(tag, encoding) + ">")
            else:
                file.write(" />")
            for k, v in xmlns_items:
                del namespaces[v]
        if node.tail:
            file.write(ET._escape_cdata(node.tail, encoding))

    #TODO : support encodfing
    #TODO : add test
    #TODO : encode XML (entities)
    @staticmethod
    def prettyprint(el, indent='  ', depth=0):
        back = (indent * depth) + '<' + el.tag
        if len(el.attrib) > 0:
            back += ' '.join(['%s="%s"' % (key, value) for (key, value) in el.attrib.items()])
        if not(el.text or len(el) > 0):
            back += '/>\n'
        else :
            back += '>' + el.text
            if len(el) > 0:
                back += '\n'
                for child in el :
                    back += self.prettyprint(child, indent, depth+1)
                    if child.tail :
                        back += (indent * depth) + child.tail + '\n'
                back += (indent * depth)
            back += '</' + el.tag + '>\n'
        return back

class Context(dict):
    """
    turn a dict into a class for notational convenience in templates
    """
    def __init__(self, name, values):
        self.__name__ = name
        self.update(values)

    def __getattr__(self, key):
        if self.has_key(key):
            return self[key]
        raise AttributeError("Context '%s' has no attribute '%s'" % (self.__name__, str(key)))

#TODO : implements testcase (slot: empty, undefined, several child, text only, mixed)
class Slot:
    def __init__(self, raiseOnUndef = False):
        self.raiseOnUndef = raiseOnUndef 

    def __getattr__(self, key):
        if self.raiseOnUndef:
            raise AttributeError('slot undefined :' + str(key))
        return T.comment('slot undefined :' + str(key))
    
class Namespace(dict):
    def __getitem__(self, key):
        back = self.get(key, None)
        if back is None:
            if key in dir(__builtins__) :
                raise KeyError()
            back = T.__getattr__(key)
        return back

def RawData(text=None):
    logger.info("using 'hpy__raw' could generate bad-formed XML")
    element = ET.Element(RawData)
    element.text = text
    return element

def CData(text=None):
    logger.info("using 'hpy__cdata' could generate bad-formed XML")
    element = ET.Element(CData)
    element.text = text
    return element
   
#TODO implements the rules for indentation
#class IndentStringIO(StringIO):
#    depth = 0
#    indent = '  '
#    
#    def write(self, str):
#        """ overwrite the method to insert indentation and line feed
#        """
#        if str.startswith("</"):  
               
if __name__ == "__main__" :
    import sys
    templater = TurboHtmlPy()
    print templater.render({}, template=sys.argv[1], isLocation=True)
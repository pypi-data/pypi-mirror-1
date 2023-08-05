#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

"""
TurboHtmlPy - Provides basic Formencode.htmlgen integration for TurboGears.

Note:
  Thanks to Cliff Wells, <cliff@develix.com>  for TurboStan used as base code.
  
  Special tags :
      'inherits' and 'replace':

  in your file home.htmlpy:
  hpy__define(into = '.master') (
      content(
          p('this will fill in the content slot in master' ),
      ),

      sidebar(
          p('this will fill in the sidebar slot in master' )
      ),
  )

  and in master.htmlpy:
  html(
      body( slot.content, slot.sidebar)
  )

  In templates, tags are bare, that is, they are not prefixed by any module name.
  Since the namespace is local to the template, this should not be an issue.

  Example template:
      html (
          head (
             title ( vars.pageTitle )
          ),

          body (
              div (id = 'main', style = 'border: 10px;') (
                ul (id = 'menu') (
                   [ li ( m ) for m in ( 'file', 'edit', 'help' ) ]
                ),
                include (template = 'content.stan'),
                span (render = vars.render_span)
             )
          )
      )
"""


#import release
#__version__ = release.version
#__author__ = release.author
#__email__ = release.email
#__copyright__ = release.copyright
#__license__ = release.license

from formencode.htmlgen import html as T
import elementtree.ElementTree as ET
import StringIO

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
#        self.compiledTemplates = {}
    
    def _evalTemplate(self, template, locals = None, globals = None, basemodule = None, isPath = True):
        txt = template
        if isPath:
            if template.startswith('.'):
                template = basemodule + template
            else :
                basemodule = template[:template.rfind('.')]
            filename = '%s.%s' % (os.path.join(*template.split('.')), self.extension)
            txt = file(filename, 'rU').read()
        try:
            node = eval(txt, locals, globals)
        except Exception:
            exc = sys.exc_info()
            if (isPath):
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
                
    def render(self, info, format = "html", fragment = False, template = None, isPath=True):
        """
        Renders the template to a string using the provided info.
        info: dict of variables to pass into template
        format: can only be "html" at this point
        template: path to template
        """
        if template is None:
            return None
        el = self.transform(info, template, isPath=isPath)
        if el is None:
            return None
        if self.usePrettyPrint :
            return self.prettyprint(el, indent = self.indentation)
        #print ET.ElementTree(el)._write(StringIO, el, self.encoding, {})
        return ET.tostring(el, self.encoding)


    def load_template(self, templatename):
        """ unused but required by tg """
        #TODO implement caching
        pass
    
    def transform(self, info, template, isPath=True):
        """
        This method is not required for most uses of templates. 
        It is specifically used for efficiently inserting widget 
        output into Kid pages. It does the same thing render does, 
        except the output is ElementTree Elements rather than 
        a string.
        """        
        locals = Namespace()
        
        try:
            import turbogears.widget.Widget as Widget
            for key, value in info.items():
                if issubclass(value.__class__, Widget):
                    locals[key] = value.insert
        except Exception, exc:
            logger.info("can't create TG Widget shortcut", exc)
            
        locals['vars'] = Vars(info)
        if self.get_extra_vars :
            locals['std'] = Vars(self.get_extra_vars()) # turbogears.view.stdvars()
        locals['hpy__include'] = lambda template: self._include_tag(template, None, locals)
        locals['hpy__kid'] = lambda **kwargs: self._include_kid(__stan_vars = info, **kwargs)
        locals['hpy__pi'] = ET.ProcessingInstruction
        locals['hpy__xml'] = ET.XML
        locals['hpy__comment'] = ET.Comment
        locals['hpy__cnv'] = self.cnv
        locals['hpy__cond'] = self.cond
        locals['slot'] = Slot(self.slotRaiseOnUndef)
        locals['True'] = True
        locals['true'] = True
        locals['False'] = False
        locals['false'] = False
        locals['None'] = None
        root = self._evalTemplate(template, locals, isPath=isPath)
        #self.cnv_ElementGenerator(root)
        return root
        
    #HACK: to support widget define with Kid (not return a elementtree.Element)
    def cnv(self, node):
        if hasattr(node, 'next'):
            from kid.pull import ElementStream
            return ElementStream(node).expand()
        return node
        

    #HACK: to support widget define with Kid (not return a elementtree.Element)
    def cond(self, condition, onTrue, onFalse=None):
        if condition:
            return onTrue
        return onFalse
    
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

class Vars:
    """
    turn a dict into a class for notational convenience in templates
    """
    def __init__(self, values):
        self.__dict__.update(values)

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
    print templater.render({}, template=sys.argv[1], isPath=True)
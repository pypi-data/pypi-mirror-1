#!/usr/bin/python
# -*- coding: utf-8 -*-

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


__version__ = '0.1'

from formencode.htmlgen import html as T
import os

# ------------------------------------------------------------------------------
class TurboHtmlPy:
    extension = "htmlpy"

    def __init__(self, extra_vars_func = None, options = {}):
        self.get_extra_vars = extra_vars_func
        self.options = options
#        self.compiledTemplates = {}
    
    def _evalTemplate(self, template, locals = None, globals = None, basemodule = None):
        if template.startswith('.'):
            template = basemodule + template
        else :
            basemodule = template[:template.rfind('.')]
        filename = '%s.%s' % (os.path.join(*template.split('.')), self.extension)
        node = eval(file(filename, 'rU').read(), locals, globals)
        if node.tag == 'hpy:define':
            slot = locals['slot']
            for c in node :
                setattr(slot, c.tag, c)
            node = self._evalTemplate(str(node.attrib['into']), locals, basemodule = basemodule)
        return node
        
    
    def _include_tag(self, template, locals = None, globals = None):
        return self._evalTemplate( template, locals, globals)

    def _include_kid(self, __stan_vars, **kwargs):
        import kid

        # sanitize variables so we don't pass reserved words to kid
        reserved = dir(kid.BaseTemplate)
        sv = dict([(k, v) for (k, v) in __stan_vars.items() if k not in reserved ])
        kwargs.update(sv)
        
        template = kid.Template(**kwargs)
        return T.xml(template.serialize())
                
    def render(self, info, format = "html", fragment = False, template = None):
        """
        Renders the template to a string using the provided info.
        info: dict of variables to pass into template
        format: can only be "html" at this point
        template: path to template
        """
        return str(self.transform(info, template))


    def load_template(self, templatename):
        """ unused but required by tg """
        #TODO implement caching
        pass
    
    def transform(self, info, template):
        """
        This method is not required for most uses of templates. 
        It is specifically used for efficiently inserting widget 
        output into Kid pages. It does the same thing render does, 
        except the output is ElementTree Elements rather than 
        a string.
        """        
        locals = Namespace()
        locals['vars'] = Vars(info)
        if self.get_extra_vars :
            locals['std'] = Vars(self.get_extra_vars()) # turbogears.view.stdvars()
        locals['hpy:include'] = lambda template: self._include_tag(template, None, locals)
        locals['hpy:kid'] = lambda **kwargs: self._include_kid(__stan_vars = info, **kwargs)
        locals['slot'] = Slot(self.options.get('htmlpy.slotRaiseOnUndef', False))

        return self._evalTemplate(template, locals)
        
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
    
if __name__ == "__main__" :
    import sys
    templater = TurboHtmlPy()
    print templater.render({}, template=sys.argv[1])
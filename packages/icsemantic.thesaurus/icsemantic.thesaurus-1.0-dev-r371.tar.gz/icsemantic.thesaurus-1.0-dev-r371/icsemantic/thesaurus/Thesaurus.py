# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: Thesaurus.py 261 2008-06-12 21:09:24Z flarumbe $
#
# end: Platecom header

from zope.interface import implements
from interfaces import IThesaurus
from pyThesaurus.Thesaurus import Thesaurus as NonPersistentThesaurus
from OFS.SimpleItem import SimpleItem
import pyThesaurus.ioSKOSCore as ioSKOSCoreModule
from pyThesaurus.ioSKOSCore import ioSKOSCore
from pyThesaurus.ioDing import ioDing
import transaction
import StringIO
from zope.app.component.hooks import getSite

from persistent import Persistent, list, dict

_format = {
	'SKOSCore': ioSKOSCore,
	'Ding': ioDing,
	}

class Thesaurus(SimpleItem):
    implements(IThesaurus)

    def __init__(self):
        self._thesaurus = NonPersistentThesaurus()
        wrap(self, "_thesaurus")
        self.commit()

    def clean(self):
	self._thesaurus = NonPersistentThesaurus()
        self.commit()
    
    def load(self, filename, lang, contexts=[], format='SKOSCore', encoding='utf-8', new=False):
	if new: self._thesaurus = NonPersistentThesaurus()
	io = _format[format](lang, contexts=contexts, thesaurus=self._thesaurus)
        file = open(filename)
        io.read(file, encoding=encoding)
	file.close()
        self.commit()
    
    def load_string(self, string, lang, contexts=[], format='SKOSCore', encoding='utf-8', new=False):
	if new: self._thesaurus = NonPersistentThesaurus()
	io = _format[format](lang, contexts=contexts, thesaurus=self._thesaurus)
	file = StringIO.StringIO(string)
        io.read(file, encoding=encoding)
	file.close()
        self.commit()
    
    def save(self, filename, lang='', contexts=[], format='SKOSCore', encoding='utf-8'):
	io = _format[format](lang, contexts=contexts, thesaurus=self._thesaurus)
        file = open(filename, 'w')
	io.write(file, encoding=encoding)
	file.close()

    def rdf_string(self, lang='', contexts=[], format='SKOSCore', encoding='utf-8'):
	io = _format[format](lang, contexts=contexts,
			thesaurus=self._thesaurus)
        temp = StringIO.StringIO()
	io.write(temp)
        return temp.getvalue()

    def rdf_term_concepts(self, term, context=None, encoding='utf-8'):
        temp = StringIO.StringIO()
        ioSKOSCoreModule.write_concepts(temp,
			self.term_concepts(term, context))
        return temp.getvalue()

    def rdf_concepts_search(self, search_expression, context=None):
        temp = StringIO.StringIO()
        ioSKOSCoreModule.write_concepts(temp,
			self.concepts_search_objects(search_expression, context))
        return temp.getvalue()

    def commiting_methods(self):
        return [ "set_prefered", "append_term", "append_concept", "replace_concept_at" ]

    def commit(self):
        t = self._thesaurus
        self._thesaurus = t
        transaction.commit()
    
def wrap(anObject, attribute_name):
    """
    Makes this class wrap an attribute. It adds to this class the methods of the wrapped object and forwards to it. It also execute commit method after calling the wrapped one.
    """
    if not hasattr(anObject.__class__, attribute_name + "_wrapped") or \
        not getattr(anObject, attribute_name + "_wrapped"):
        wrapped_class = eval("anObject." + attribute_name).__class__
	n_items = vars(wrapped_class).items()
	for inhe_class in wrapped_class.__bases__:
	    n_items += vars(inhe_class).items()
        for func_name, func in n_items:
            if hasattr(func, "func_code") and (not func_name.startswith("_") or func_name == "__getitem__" or func_name == "__call__"):
                # Parameters for declaring and for invoking
                pars_declare = []
                pars_invoke = []
                for i in range(func.func_code.co_argcount):
                    par = func.func_code.co_varnames[i]
                    if i > 0:
                        pars_invoke.append(par)
                    
                    if func.func_defaults != None:
                        default_index = i - (func.func_code.co_argcount - len(func.func_defaults))
                        if default_index >= 0:
                            par += "=" + repr(func.func_defaults[default_index])
                    pars_declare.append(par)
                
                # Function code
                code = "def " + func_name + "(" + ", ".join(pars_declare) + "): "
                if func_name in anObject.commiting_methods():
                    code += "tmp = self." + attribute_name + "." + func_name + "("
                    code += ", ".join(pars_invoke) + "); self.commit(); return tmp"
                else:
                    code += "return self." + attribute_name + "." + func_name + "("
                    code += ", ".join(pars_invoke) + ");"

                #print code + "\n"
                exec(code)
                setattr(anObject.__class__, func_name, eval(func_name))
        setattr(anObject.__class__, attribute_name + "_wrapped", True)

def thesaurus_utility():
    from zope.component import queryUtility
    ut = queryUtility(IThesaurus)
    if ut is None:
        raise NameError, "Thesaurus utility does not exist. Please, reinstall icsemantic.thesaurus product."
    wrap(ut, "_thesaurus")
    return ut


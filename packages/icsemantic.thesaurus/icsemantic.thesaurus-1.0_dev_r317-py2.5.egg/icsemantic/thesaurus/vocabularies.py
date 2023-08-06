# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: vocabularies.py 256 2008-06-12 15:41:52Z crocha $
#
# end: Platecom header
"""
"""
from zope.schema import vocabulary
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.component import getUtility
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IPropertiesTool

from icsemantic.core.i18n import _
from icsemantic.core.config import HAS_PLONE3

from pyThesaurus import io

if HAS_PLONE3:
    from plone.i18n.locales.interfaces import IContentLanguageAvailability
else:
    from Products.PloneLanguageTool import availablelanguages

class ThesaurusFormatVocabulary(object):
	implements(IVocabularyFactory)

	def __call__(self, context):
		formats = []
		for format in io.formats():
			formats.append(vocabulary.SimpleTerm(
				unicode(format),
				title=unicode(format)
				)
			)
	        return vocabulary.SimpleVocabulary( formats )
ThesaurusFormatVocabularyFactory = ThesaurusFormatVocabulary()

class EncodingsVocabulary(object):
	implements(IVocabularyFactory)

	def __call__(self, context):
		encode_list = {
		'ascii':'ascii:English',
		'big5':'big5:Traditional Chinese',
		'big5hkscs':'big5hkscs:Traditional Chinese',
		'cp037':'cp037:English',
		'cp424':'cp424:Hebrew',
		'cp437':'cp437:English',
		'cp500':'cp500:Western Europe',
		'cp737':'cp737:Greek',
		'cp775':'cp775:Baltic languages',
		'cp850':'cp850:Western Europe',
		'cp852':'cp852:Central and Eastern Europe',
		'cp855':'cp855:Bulgarian, Byelorussian, Macedonian, Russian, Serbian',
		'cp856':'cp856:Hebrew',
		'cp857':'cp857:Turkish',
		'cp860':'cp860:Portuguese',
		'cp861':'cp861:Icelandic',
		'cp862':'cp862:Hebrew',
		'cp863':'cp863:Canadian',
		'cp864':'cp864:Arabic',
		'cp865':'cp865:Danish, Norwegian',
		'cp866':'cp866:Russian',
		'cp869':'cp869:Greek',
		'cp874':'cp874:Thai',
		'cp875':'cp875:Greek',
		'cp932':'cp932:Japanese',
		'cp949':'cp949:Korean',
		'cp950':'cp950:Traditional Chinese',
		'cp1006':'cp1006:Urdu',
		'cp1026':'cp1026:Turkish',
		'cp1140':'cp1140:Western Europe',
		'cp1250':'cp1250:Central and Eastern Europe',
		'cp1251':'cp1251:Bulgarian, Byelorussian, Macedonian, Russian, Serbian',
		'cp1252':'cp1252:Western Europe',
		'cp1253':'cp1253:Greek',
		'cp1254':'cp1254:Turkish',
		'cp1255':'cp1255:Hebrew',
		'cp1256':'cp1256:Arabic',
		'cp1257':'cp1257:Baltic languages',
		'cp1258':'cp1258:Vietnamese',
		'euc_jp':'euc jp:Japanese',
		'euc_jis_2004':'euc jis 2004:Japanese',
		'euc_jisx0213':'euc jisx0213:Japanese',
		'euc_kr':'euc kr:Korean',
		'gb2312':'gb2312:Simplified Chinese',
		'gbk':'gbk:Unified Chinese',
		'gb18030':'gb18030:Unified Chinese',
		'hz':'hz:Simplified Chinese',
		'iso2022_jp':'iso2022 jp:Japanese',
		'iso2022_jp_1':'iso2022 jp 1:Japanese',
		'iso2022_jp_2':'iso2022 jp 2:Japanese, Korean, Simplified Chinese, Western Europe, Greek',
		'iso2022_jp_2004':'iso2022 jp 2004:Japanese',
		'iso2022_jp_3':'iso2022 jp 3:Japanese',
		'iso2022_jp_ext':'iso2022 jp ext:Japanese',
		'iso2022_kr':'iso2022 kr:Korean',
		'latin_1':'latin 1:West Europe',
		'iso8859_2':'iso8859 2:Central and Eastern Europe',
		'iso8859_3':'iso8859 3:Esperanto, Maltese',
		'iso8859_4':'iso8859 4:Baltic languagues',
		'iso8859_5':'iso8859 5:Bulgarian, Byelorussian, Macedonian, Russian, Serbian',
		'iso8859_6':'iso8859 6:Arabic',
		'iso8859_7':'iso8859 7:Greek',
		'iso8859_8':'iso8859 8:Hebrew',
		'iso8859_9':'iso8859 9:Turkish',
		'iso8859_10':'iso8859 10:Nordic languages',
		'iso8859_13':'iso8859 13:Baltic languages',
		'iso8859_14':'iso8859 14:Celtic languages',
		'iso8859_15':'iso8859 15:Western Europe',
		'johab':'johab:Korean',
		'koi8_r':'koi8 r:Russian',
		'koi8_u':'koi8 u:Ukrainian',
		'mac_cyrillic':'mac cyrillic:Bulgarian, Byelorussian, Macedonian, Russian, Serbian',
		'mac_greek':'mac greek:Greek',
		'mac_iceland':'mac iceland:Icelandic',
		'mac_latin2':'mac latin2:Central and Eastern Europe',
		'mac_roman':'mac roman:Western Europe',
		'mac_turkish':'mac turkish:Turkish',
		'ptcp154':'ptcp154:Kazakh',
		'shift_jis':'shift jis:Japanese',
		'shift_jis_2004':'shift jis 2004:Japanese',
		'shift_jisx0213':'shift jisx0213:Japanese',
		'utf_16':'utf-16:all languages',
		'utf_16_be':'utf-16 be:all languages (BMP only)',
		'utf_16_le':'utf-16 le:all languages (BMP only)',
		'utf_7':'utf-7:all languages',
		'utf_8':'utf-8:all languages',
		'utf_8_sig':'utf-8 sig:all languages',
		}
		encode = []
		for value, title in encode_list.items():
			encode.append(vocabulary.SimpleTerm(
				unicode(value),
				title=unicode(title)
				)
			)
	        return vocabulary.SimpleVocabulary( encode )
EncodingsVocabularyFactory = EncodingsVocabulary()


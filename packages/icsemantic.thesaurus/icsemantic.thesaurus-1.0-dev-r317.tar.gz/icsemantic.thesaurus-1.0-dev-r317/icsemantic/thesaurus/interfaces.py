# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: __init__.py 258 2008-06-12 15:57:43Z crocha $
#
# end: Platecom header
""" icsemantic.thesaurus interfaces.
"""

from zope import schema
from zope.interface import Interface
from icsemantic.core.i18n import _

class IThesaurus( Interface ):
    """ Interface for Thesaurus Utility
    """

class IicSemanticManagementThesaurusUpload( Interface ):
    """ Interface used for a thesaurus file upload.
    """

    thesaurus_file = schema.Bytes(title = _(u"Thesaurus file"),
                                 required = True,
                                 description = _(u"A thesaurus file located in your computer"))

    default_language = schema.Choice(
		    title = _(u"heading_thesaurus_language",
			    default=u"Default language"),
		    description = _(u"description_site_language",
			    default=u"If term have no language is defined as this language"),
		    required = True,
		    vocabulary="icsemantic.available_languages")
    thesaurus_context = schema.TextLine(
		    title = _(u"heading_thesaurus_context",
			    u"Default Context"),
		    description = _(u"description_thesaurus_context",
			    default=u"If term have no context is defined as this context"),
                    required = False) #When updated will be required
    thesaurus_format = schema.Choice(
		    title = _(u"heading_file_format",
			    u"File format"),
		    description = _(u"description_file_format",
			    u"Thesaurus File format"),
		    required = True,
                    vocabulary="icsemantic.core.thesaurus_formats") #When updated will be required
    encoding = schema.Choice(
		    title = _(u"heading_encodings",
			    u"Encoding"),
		    description = _(u"description_encodings",
			    u"Encoding File format"),
		    required = True,
                    vocabulary="icsemantic.core.encodings")
    new = schema.Bool(
		    title = _(u"heading_new",
			    u"Start new thesaurus"),
		    description = _(u"description_new",
			    u"Clean old thesaurus and create one with this data."),
		    required = True,
		    )

class IicSemanticVerticalSelectTest( Interface ):
    """ Interface used for test the vertical select widget.
    """
    vertical_select = schema.TextLine(
		    title = _(u"heading_thesaurus_verticalselect",
			    u"Vertical select"),
		    description = _(u"description_thesaurus_verticalselect",
			    default=u"Select a branch of concepts"),
            required = False)


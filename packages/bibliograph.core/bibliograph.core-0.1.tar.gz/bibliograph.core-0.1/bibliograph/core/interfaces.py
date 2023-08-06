from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from bibliograph.core.encodings import _python_encodings

# XXX as long as we don't have a propper translation messagefactory
_ = unicode

###############################################################################

class IBibliographyExport(Interface):
    """ Marker interface for a container with
        exportable bibliography elements.
    """

    format = schema.Choice(
        title=_('Export format'),
        required=True,
        default='bibtex',
        # XXX make this dynamic using a factory utilizing 'enabled' &
        # 'available' flags          
        vocabulary=SimpleVocabulary.fromItems([
            (_("Bibtex"), 'bibtex'),
            (_("Endnote"), 'endnote'),
            (_("RIS"), 'ris'),
            (_("XML (MODS)"), 'xml'),
            (_("PDF"), 'pdf'),
        ])
        )

    output_encoding = schema.Choice(
        title=_('Encoding of output'),
        required=False,
        vocabulary=SimpleVocabulary.fromValues(_python_encodings)
        )

###############################################################################

class IBibliographicReference(Interface):
    """ An object is renderable as a bibliography """

    title = schema.TextLine(
        title=_('Title'),
        description=_('The title of the document'),
        required = True,
        )

    authors = schema.TextLine(
        title=_('Authors'),
        description=_('A formated string of the authors of the document'),
        required = True,
        )

    publication_type = schema.Choice(
        title=_('Publication type'),
        description=_('A publication type as found in the bibtex definition'),
        required=True,
        vocabulary=SimpleVocabulary.fromItems([
            (_("Article"), 'article'),
            (_("Book"), 'book'),
            (_("Booklet"), 'booklet'),
            (_("Conference"), 'conference'),
            (_("Inbook"), 'inbook'),
            (_("Incollection"), 'incollection'),
            (_("Inproceedings"), 'inproceenings'),
            (_("Manual"), 'manual'),
            (_("Masterthesis"), 'masterthesis'),
            (_("Misc"), 'misc'),
            (_("Phdthesis"), 'phdthesis'),
            (_("Proceedings"), 'proceedings'),
            (_("Techeport"), 'techreport'),
            (_("Unpublished"), 'unpublished'),
            ])
        )

    editor_flag = schema.Bool(
        title=_('Editor'),
        description=_('Marker for interpretation of author field as editor'),
        required = False,
        )

    publication_year = schema.Int(
        title=_('Year of publication'),
        required=True,
        )

    abstract = schema.Text(
        title=_('Abstract'),
        description=_('A short summary of the document'),
        required = False,
        )
    
    url = schema.TextLine(
        title=_('URL of the publication'),
        required=False,
        )

    subject = schema.List(
        title=_('Subject'),
        description=_('A list of tags(subjects) of the document'),
        required = True,
        )

    note = schema.Text(
        title=_('Note'),
        description=_('Some additional notes'),
        required = False,
        )

    annote = schema.Text(
        title=_('Annotation'),
        description=_('Some annotations'),
        required = False,
        )

    source_fields = schema.List(
        title=_('Source fields'),
        value_type=schema.Tuple(),
        required=False,
        )

    def getAuthors(*args, **kw):
        """ Get a list-like object containing the authors.
            The object must know about rendering a formatted list
            of authors by being called.
        """

# EOF

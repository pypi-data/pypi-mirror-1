import os.path as op
import xml.sax, xml.sax.handler, cStringIO as stringio
from handler import _Handler

class Template(object):
    '''
    A courtain template page.

    :IVariables:
        source : str
            The Python code producing the page.
        error_location : (int, int)
            The location of the last error expressed as a couple (line, column).
    '''
    def __init__(self, str_source = None, file_source = None,
        auto_reload = False):
        '''
        Create a new template.

        :Parameters:
            str_source : str
                The template as a single string. If str_source is given,
                file_source must be None.
            file_source : file | str
                A file-like object (or the path of a file) which provides the
                template. If file_source is given, str_source must be None.
            auto_reload : bool
                If the source is a file specified through its path, then when
                this flag is on the file contents are auto-reparsed if the file
                is modified. This options can cause a sensible degradation of
                performances and should only be used as a development
                facilities, never to be abilitated on production environments.
        '''
        # check and save parameters
        assert [str_source, file_source].count(None) == 1, \
            'need just str_source or file_source'
        if auto_reload and not isinstance(file_source, (str, unicode)):
            raise ValueError(
                'auto_reload is valid only with a path file_source')
        self.__auto_reload = auto_reload
        self.__file_source = file_source
        self.__str_source = str_source
        # parse
        self.__handler = None
        self.__last_timestamp = None
        self.__parse_if_needed()
    def __parse_if_needed(self):
        if not self.__auto_reload and self.__handler is not None:
            return
        if self.__auto_reload:
            new_timestamp = op.getmtime(self.__file_source)
            if self.__last_timestamp == new_timestamp:
                return
        handler = _Handler(self)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.setFeature(xml.sax.handler.feature_namespaces, 1)
        if self.__file_source is None:
            if isinstance(self.__str_source, unicode):
                self.__str_source = self.__str_source.encode('utf8')
            self.__file_source = stringio.StringIO(self.__str_source)
        parser.parse(self.__file_source)
        self.__handler = handler
        self.__source = handler.source
        if self.__auto_reload:
            self.__last_timestamp = new_timestamp
    @property
    def source(self):
        return self.__source
    def __call__(self, xml_generator, env, translation_context = None,
        location = None, *args, **kwargs):
        '''
        Calls the template and send the output to a SAX XML generator.

        :Parameters:
            xml_generator : xml.sax.handler.ContentHandler
                The handler to which the XML SAX events are sent during
                template computation. Tipically `xml.sax.saxutils.XMLGenerator`
                is a good choice.
            env : dict{str, object)}
                The environment in which the template is executed.
            translation_context : object
                The object passed as "context" to the zope.i18n.translate
                method during translations. See narrative documentation for
                more informations.
            location : Location
                An object which is updated with the current location (in the
                source template) where execution is taking place. It is useful
                in case of exception to recognize the place where an error has
                occourred.
        '''
        if location is None:
            location = Location()
        self.__parse_if_needed()
        self.__handler.function(xml_generator, env,
            _location = location,
            _i18n_context = translation_context,
            *args, **kwargs)

class Location(object):
    def __init__(self):
        self.__current = None
    def new(self, line, column):
        self.__current = (line, column)
    @property
    def current(self):
        return self.__current

import xml.sax.handler

from curtain import ns
import processors

class _AttributesImpl(dict):
    def __init__(self, dct, extra_attrs):
        self.update(dct)
        self.update(extra_attrs)
    def getLength(self): return len(self)
    def getNames(self): return self.keys()
    def getType(self, name):
        # FIXME: when is not CDATA?
        return 'CDATA'
    def getValue(self, name): return self[name]
    def __hash__(self):
        return hash(tuple(self.items()))

class _Handler(xml.sax.handler.ContentHandler):
    '''
    The SAX handler which process a template and produce the function.

    :IVariables:
        __template : Template
            The template which requested this handler.
        __function : list(str)
            The body of the generated function, as a list of strings.
        __locator : Locator
            The locator possibly provided by the XML parser.
        __indentation_level : int
            The current indentation level for output.
        __completed : bool
            Whether the processing of the whole document has been completed or not.
        __enders : list(list(callable))
            A stack of list of methods which should be called at the end tag,
            just after the endElementNS event code has been produced.
        __preenders : list(list(callable))
            A stack of list of methods which should be called at the end tag,
            just before the endElementNS event code has been produced.
        __pmappings : list(bool)
            A stack of booleans meaning if the i-th 'startPrefixMapping' has
            been emitted or not.
        __processor_classes : list(type)
            A list of processor classes, ordered by priority.
        __output_suspension_level : int
            An integer which tells how many times the _suspend_output function
            has been called (_resume_output decrease this counter instead).
        __lastvarnum : int
            The number of variables used, to produce new unique variable names.
    '''
    #
    # public interface
    #
    def __init__(self, template):
        '''
        Create a new handler.

        :Parameters:
            template : Template
                The template which requested this handler.
        '''
        # initialize internal variables
        self.__template = template
        self.__function = []
        self.__locator = None
        self.__indentation_level = 0
        self.__completed = False
        self.__enders = []
        self.__preenders = []
        self.__pmappings = []
        self.__processor_classes = []
        self.__output_suspension_level = 0
        self.__lastvarnum = 0
        self.__precallbacks = {'startDocument': [], 'endDocument': [],
            'startElementNS': [], 'endElementNS': [], 'characters': []}
        self.__postcallbacks = {'startDocument': [], 'endDocument': [],
            'startElementNS': [], 'endElementNS': [], 'characters': []}
        self.__register_default_processor_classes()
    @property
    def source(self):
        'The source code of the compiled function.'
        assert self.__completed
        return '\n'.join(self.__function)
    @property
    def function(self):
        '''The function which produce the output; takes the xml generator and
        environment as arguments.'''
        d = {}
        exec self.source in d
        return d['process']
    def register_processor(self, processor_class):
        '''
        Register a new processor.
        '''
        self.__processor_classes.append(processor_class)
        self.__processor_classes.sort(key = lambda el: -el.priority)
        processor_class.registered(self)

    #
    # internal interface
    #
    __tab = '\t'
    def __attrs(self, attrs):
        return 'curtain.handler._AttributesImpl(%r, _extra_attrs)' % dict(
            (k,v) for (k,v) in attrs.items() if k[0] != ns)
    def __register_default_processor_classes(self):
        for name in dir(processors):
            k = getattr(processors, name)
            if (isinstance(k, type) and
                issubclass(k, processors.Processor) and
                k != processors.Processor):
                self.register_processor(k)
    def __callbacks(self, callbackmap, name, *args, **kwargs):
        for entry in callbackmap[name]:
            entry(*args, **kwargs)
    def __save_location_deco(meth):
        def decorated(self, *args, **kwargs):
            ln, cn = self.__locator.getLineNumber(), self.__locator.getColumnNumber()
            self._add('_location.new(%r, %r)' % (ln, cn))
            return meth(self, *args, **kwargs)
        return decorated

    #
    # processors interface
    #
    def _indent(self): self.__indentation_level += 1
    def _unindent(self): self.__indentation_level -= 1
    def _add(self, line):
        if self.__output_suspension_level == 0:
            self.__function.append(
                self.__tab*self.__indentation_level +
                line)
    def _get_var(self):
        name = '_var_%d' % self.__lastvarnum
        self.__lastvarnum += 1
        return name
    def _add_ender(self, ender):
        self.__enders[-1].append(ender)
    def _add_preender(self, preender):
        self.__preenders[-1].append(preender)
    def _suspend_output(self):
        self.__output_suspension_level += 1
    def _resume_output(self):
        self.__output_suspension_level -= 1
    def _reset_suspension(self, value):
        old = self.__output_suspension_level
        self.__output_suspension_level = value
        return old
    def _register_precallback(self, name, value):
        self.__precallbacks[name].append(value)
    def _register_postcallback(self, name, value):
        self.__postcallbacks[name].append(value)
    def _unregister_precallback(self, name, value):
        self.__precallbacks[name].remove(value)
    def _unregister_postcallback(self, name, value):
        self.__postcallbacks[name].remove(value)

    #
    # xml.sax.handlers.ContentHandler interface
    #
    def setDocumentLocator(self, locator):
        # save the locator
        self.__locator = locator
    def startDocument(self):
        # precallbacks
        self.__callbacks(self.__precallbacks, 'startDocument')
        # start of the program
        self.__completed = False
        self._add('import curtain')
        self._add('def process(xml_generator, env, _location, _slots = {}, _i18n_context = None):')
        self._indent()
        self._add("globals().update(env)")
        self._add('if len(_slots) == 0:')
        self._indent()
        self._add('xml_generator.startDocument()')
        self._unindent()
        # postcallbacks
        self.__callbacks(self.__postcallbacks, 'startDocument')
    def endDocument(self):
        # precallbacks
        self.__callbacks(self.__precallbacks, 'endDocument')
        # end of program
        self._add('if len(_slots) == 0:')
        self._indent()
        self._add('xml_generator.endDocument()')
        self._unindent()
        self._unindent()
        self.__completed = True
        # postcallbacks
        self.__callbacks(self.__postcallbacks, 'endDocument')
    @__save_location_deco
    def startElementNS(self, name, qname, attrs):
        # precallbacks
        self.__callbacks(self.__precallbacks, 'startElementNS', name, qname, attrs)
        # initialize environment
        self.__enders.append([])
        self.__preenders.append([])
        # invoke processor classes
        processors = []
        for attrname in attrs.keys():
            if attrname[0] == ns:
                for processor in self.__processor_classes:
                    if processor.attr_name == attrname[1]:
                        p = processor()
                        value = attrs[attrname].strip()
                        if p.value_kind == 'simple':
                            pass
                        elif p.value_kind == 'single':
                            i = value.index(' ')
                            value = (value[:i], value[i+1:])
                        elif p.value_kind == 'list':
                            v = []
                            for subvalue in value.split(';'):
                                subvalue = subvalue.strip()
                                i = subvalue.index(' ')
                                v.append((subvalue[:i], subvalue[i+1:]))
                            value = v
                        else:
                            raise ValueError('unknown value_kind %r' %
                                p.value_kind)
                        p.process(self, value)
                        processors.append((p, value))
        # produce tag
        self._add('_extra_attrs = {}')
        if name[0] != ns:
            self._add('xml_generator.startElementNS(%r, %r, %s)' % (name,
                qname, self.__attrs(attrs)))
        # processor post-processing
        for p, value in processors:
            p.post_process(self, value)
        # postcallbacks
        self.__callbacks(self.__postcallbacks, 'startElementNS', name, qname, attrs)
    @__save_location_deco
    def endElementNS(self, name, qname):
        # precallbacks
        self.__callbacks(self.__precallbacks, 'endElementNS', name, qname)
        # preenders
        preender = self.__preenders.pop()
        for f in preender: f()
        # code
        if name[0] != ns:
            self._add('xml_generator.endElementNS(%r, %r)' % (name, qname))
        # postenders
        ender = self.__enders.pop()
        for f in ender: f()
        # postcallbacks
        self.__callbacks(self.__postcallbacks, 'endElementNS', name, qname)
    @__save_location_deco
    def ignorableWhitespace(self, whitespace):
        self._add('xml_generator.ignorableWhitespace(%r)' % whitespace)
    @__save_location_deco
    def characters(self, content):
        # precallbacks
        self.__callbacks(self.__precallbacks, 'characters', content)
        # code
        self._add('xml_generator.characters(%r)' % content)
        # postcallbacks
        self.__callbacks(self.__postcallbacks, 'characters', content)
    @__save_location_deco
    def startPrefixMapping(self, prefix, uri):
        if uri != ns:
            self._add('xml_generator.startPrefixMapping(%r, %r)' % (prefix, uri))
            self.__pmappings.append(True)
        else:
            self.__pmappings.append(False)
    @__save_location_deco
    def endPrefixMapping(self, prefix):
        if self.__pmappings.pop():
            self._add('xml_generator.endPrefixMapping(%r)' % prefix)

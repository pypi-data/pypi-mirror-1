from zope.i18n import translate

from curtain import ns

class Processor(object):
    '''
    An attribute processor.

    :CVariables:
        attr_name : unicode
            Name of the attribute.
        value_kind : str
            Can be 'simple' (attr value is the passed value), 'single' (attr
            value is a space separated couple name / expression) or 'list' (a
            list of 'single' values separated by semicolons).
        priority : int
            The priority of processing; 0 means the lowest.
    '''
    attr_name = None
    value_kind = 'simple'
    priority = 0

    @staticmethod
    def registered(handler):
        '''
        This processor has been registered to given handler. Useful for
        installing some callbacks (like the one on startDocument).

        :Parameters:
            handler : _Handler
                The handler which has registered this handler.
        '''

    def process(self, handler, value):
        '''
        The attribute has been found and processing is required. This method is
        called before generating the actual element tag.

        :Parameters:
            handler : _Handler
                The handler processing the request.
            value : unicode | tuple(unicode, unicode) | list(tuple(unicode, unicode)
                The parsed value of the attribute.
        '''

    def post_process(self, handler, value):
        '''
        The attribute has been found and processing is required. This method is
        called after generating the actual element tag.

        :Parameters:
            handler : _Handler
                The handler processing the request.
            value : unicode | tuple(unicode, unicode) | list(tuple(unicode, unicode)
                The parsed value of the attribute.
        '''

class DefnProcessor(Processor):
    attr_name = u'defn'
    value_kind = 'list'
    priority = 1000
    def process(self, handler, value):
        vname = handler._get_var()
        handler._add('def %s():' % vname)
        handler._indent()
        for varname, expr in value:
            assert not varname.startswith('_')
            handler._add('%s = %s' % (varname, expr))
        @handler._add_ender
        def _():
            handler._unindent()
            handler._add('%s()' % vname)

class UseProcessor(Processor):
    attr_name = u'use'
    @staticmethod
    def registered(handler):
        def start():
            handler._add('slots_list = []')
        handler._register_postcallback('startDocument', start)
    def process(self, handler, macroname):
        handler._add('slots_list.append({})')
        handler._suspend_output()
        @handler._add_ender
        def _():
            handler._resume_output()
            handler._add('%s(xml_generator, env, _slots = slots_list.pop(), translation_context = _i18n_context)' % (
                macroname))

class SlotProcessor(Processor):
    attr_name = u'slot'
    def process(self, handler, slotname):
        var = handler._get_var()
        handler._add('%s = %r in _slots' % (var, slotname))
        handler._add('if %s:' % var)
        handler._indent()
        handler._add('_slots[%r]()' % slotname)
        handler._unindent()
        handler._add('else:')
        handler._indent()
        handler._add('pass')
        handler._add_ender(handler._unindent)

class FillProcessor(Processor):
    attr_name = u'fill'
    def process(self, handler, slotname):
        oldsuspvalue = handler._reset_suspension(0)
        var = handler._get_var()
        handler._add('def %s():' % var)
        handler._indent()
        @handler._add_ender
        def _():
            handler._unindent()
            handler._add('slots_list[-1][%r] = %s' % (slotname, var))
            handler._reset_suspension(oldsuspvalue)

class CondProcessor(Processor):
    attr_name = u'cond'
    priority = 900
    def process(self, handler, value):
        handler._add('if %s:' % value)
        handler._indent()
        handler._add_ender(handler._unindent)

class LoopProcessor(Processor):
    attr_name = u'loop'
    value_kind = 'single'
    priority = 800
    def process(self, handler, value):
        varname, expr = value
        handler._add('for %s in %s:' % (varname, expr))
        handler._indent()
        handler._add_ender(handler._unindent)

class SkipProcessor(Processor):
    attr_name = u'skip'
    priority = 500
    def process(self, handler, value):
        skip = True
        self.skip_vname = handler._get_var()
        handler._add('%s = %s' % (self.skip_vname, value))
        handler._add('if not %s:' % self.skip_vname)
        handler._indent()
    def post_process(self, handler, value):
        handler._unindent()
        @handler._add_preender
        def _():
            handler._add('if not %s:' % self.skip_vname)
            handler._indent()
        handler._add_ender(handler._unindent)

class AttrProcessor(Processor):
    attr_name = u'attr'
    value_kind = 'list'
    priority = 600
    def process(self, handler, value):
        for attrname, expr in value:
            handler._add('_value = %s' % expr)
            handler._add('if _value: extra_attrs[%r] = _value' % attrname)

class ContProcessor(Processor):
    attr_name = u'cont'
    priority = 700
    def post_process(self, handler, value):
        handler._add('xml_generator.characters(%s)' % value)
        handler._suspend_output()
        handler._add_preender(handler._resume_output)

class DomainProcessor(Processor):
    attr_name = u'domain'
    @staticmethod
    def registered(handler):
        def start():
            handler._add('_domain_stack = []')
        handler._register_postcallback('startDocument', start)
    def process(self, handler, value):
        handler._add('_domain_stack.append(%r)' % value)
        @handler._add_ender
        def _():
            handler._add('_domain_stack.pop()')

class NameProcessor(Processor):
    attr_name = u'name'
    def process(self, handler, value):
        v = handler._get_var()
        susp = handler._reset_suspension(0)
        handler._add('def %s():' % v)
        handler._indent()
        @handler._add_ender
        def _():
            handler._unindent()
            handler._add('_translate_stack[-1].append((%r, %s))' % (value, v))
            handler._reset_suspension(susp)

class TranslateProcessor(Processor):
    attr_name = u'translate'
    @staticmethod
    def registered(handler):
        def imp():
            handler._add('from curtain.processors import _translator_output')
        handler._register_precallback('startDocument', imp)
        def start():
            handler._add('_translate_stack = []')
        handler._register_postcallback('startDocument', start)
    def post_process(self, handler, value):
        handler._add('_translate_stack.append([])')
        handler._suspend_output()
        self.stack_level = 0
        def characters(content):
            if self.stack_level == 0:
                v = handler._reset_suspension(0)
                handler._add('_translate_stack[-1].append((None, %r))' % content)
                handler._reset_suspension(v)
        handler._register_precallback('characters', characters)
        def startElementNS(name, qname, attrs):
            self.stack_level = self.stack_level + 1
        handler._register_precallback('startElementNS', startElementNS)
        def endElementNS(name, qname):
            self.stack_level = self.stack_level - 1
        handler._register_precallback('endElementNS', endElementNS)
        @handler._add_preender
        def _():
            handler._unregister_precallback('characters', characters)
            handler._unregister_precallback('startElementNS', startElementNS)
            handler._unregister_precallback('endElementNS', endElementNS)
            handler._resume_output()
            handler._add('_translator_output(xml_generator, _translate_stack.pop(), _domain_stack[-1], _i18n_context)')

def _translator_output(xml_generator, message, domain, context):
    producers = dict((name, meth) for (name, meth) in message if name is not None)
    msgid = u''.join([value if name is None else u'${%s}' % name for (name, value) in message])
    res = translate(msgid, domain, context = context)
    breaks = []
    for name, gen in producers.items():
        cn = u'${%s}' % name
        i = res.index(cn)
        breaks.append((i, i+len(cn), gen))
    breaks.sort(key = lambda b: b[0])
    i = 0
    for start, end, gen in breaks:
        xml_generator.characters(res[i:start])
        gen()
        i = end
    xml_generator.characters(res[i:])

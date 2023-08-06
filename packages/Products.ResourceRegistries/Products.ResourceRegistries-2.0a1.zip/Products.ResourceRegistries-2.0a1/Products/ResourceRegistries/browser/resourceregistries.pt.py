registry = dict(version='8.3.2.1')
def bind():
	from cPickle import loads as _loads
	_init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
	_lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
	_init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
	_init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
	_lookup_name = _loads('cchameleon.core.codegen\nlookup_name\np1\n.')
	_get_content_provider = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveContentProviderTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
	_init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
	def render(econtext, rcontext=None):
		macros = econtext.get('macros')
		_translate = econtext.get('_translate')
		_slots = econtext.get('_slots')
		target_language = econtext.get('target_language')
		u'_init_stream()'
		(_out, _write) = _init_stream()
		u'_init_tal()'
		(_attributes, repeat) = _init_tal()
		u'_init_default()'
		_default = _init_default()
		u'None'
		default = None
		u'None'
		_domain = None
		u"''"
		_write(u'')
		_default.value = default = ''
		u'plone.resourceregistries.styles'
		_content = _get_content_provider(econtext['context'], econtext['request'], econtext['view'], 'plone.resourceregistries.styles')
		u'_content'
		_tmp1 = _content
		_tmp = _tmp1
		if (_tmp.__class__ not in (str, unicode, int, float) and hasattr(_tmp, '__html__')):
			_write(_tmp.__html__())
		elif _tmp is not None:
			if not (isinstance(_tmp, unicode)):
				_tmp = str(_tmp)
			_write(_tmp)
		u"''"
		_write(u'')
		_default.value = default = ''
		u'plone.resourceregistries.kineticstylesheets'
		_content = _get_content_provider(econtext['context'], econtext['request'], econtext['view'], 'plone.resourceregistries.kineticstylesheets')
		u'_content'
		_tmp1 = _content
		_tmp = _tmp1
		if (_tmp.__class__ not in (str, unicode, int, float) and hasattr(_tmp, '__html__')):
			_write(_tmp.__html__())
		elif _tmp is not None:
			if not (isinstance(_tmp, unicode)):
				_tmp = str(_tmp)
			_write(_tmp)
		u"''"
		_write(u'')
		_default.value = default = ''
		u'plone.resourceregistries.scripts'
		_content = _get_content_provider(econtext['context'], econtext['request'], econtext['view'], 'plone.resourceregistries.scripts')
		u'_content'
		_tmp1 = _content
		_tmp = _tmp1
		if (_tmp.__class__ not in (str, unicode, int, float) and hasattr(_tmp, '__html__')):
			_write(_tmp.__html__())
		elif _tmp is not None:
			if not (isinstance(_tmp, unicode)):
				_tmp = str(_tmp)
			_write(_tmp)
		_write(u'')
		return _out.getvalue()
	return render

registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()

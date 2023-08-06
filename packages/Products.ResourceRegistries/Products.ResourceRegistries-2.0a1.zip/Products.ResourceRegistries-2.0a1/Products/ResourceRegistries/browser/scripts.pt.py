registry = dict(version='8.3.2.1')
def bind():
	from cPickle import loads as _loads
	_init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
	_lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
	_init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
	_re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
	_init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
	_lookup_name = _loads('cchameleon.core.codegen\nlookup_name\np1\n.')
	_init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
	_path = _loads('ccopy_reg\n_reconstructor\np1\n(cfive.pt.expressions\nFiveTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n.')
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
		u'context/@@resourceregistries_scripts_view'
		view = _path(econtext['context'], econtext['request'], True, '@@resourceregistries_scripts_view')
		u'view/scripts'
		_tmp1 = _path(view, econtext['request'], True, 'scripts')
		script = None
		(_tmp1, _tmp2) = repeat.insert('script', _tmp1)
		for script in _tmp1:
			_tmp2 = (_tmp2 - 1)
			u'script/inline'
			_write('')
			inline = _path(script, econtext['request'], True, 'inline')
			u'script/conditionalcomment'
			condcomment = _path(script, econtext['request'], True, 'conditionalcomment')
			u'condcomment'
			_write('')
			_tmp3 = _path(condcomment, econtext['request'], True)
			if _tmp3:
				pass
				u"''"
				_write(u'')
				_default.value = default = ''
				u'<!--[if ${condcomment}]>'
				_content = ('%s%s%s' % (u'<!--[if ', _path(condcomment, econtext['request'], True), u']>'))
				u'_content'
				_tmp3 = _content
				_tmp = _tmp3
				if (_tmp.__class__ not in (str, unicode, int, float) and hasattr(_tmp, '__html__')):
					_write(_tmp.__html__())
				elif _tmp is not None:
					if not (isinstance(_tmp, unicode)):
						_tmp = str(_tmp)
					_write(_tmp)
				_write(u'')
			u'not(_path(inline, request, True, ))'
			_tmp3 = not (_path(inline, econtext['request'], True))
			if _tmp3:
				pass
				u'script/src'
				_write(u'<script type="text/javascript"')
				_tmp3 = _path(script, econtext['request'], True, 'src')
				if _tmp3 is _default:
					_tmp3 = None
				if (_tmp3 is None or _tmp3 is False):
					pass
				else:
					if not (isinstance(_tmp3, unicode)):
						_tmp3 = str(_tmp3)
					if '&' in _tmp3:
						if ';' in _tmp3:
							_tmp3 = _re_amp.sub('&amp;', _tmp3)
						else:
							_tmp3 = _tmp3.replace('&', '&amp;')
					if '<' in _tmp3:
						_tmp3 = _tmp3.replace('<', '&lt;')
					if '>' in _tmp3:
						_tmp3 = _tmp3.replace('>', '&gt;')
					if '"' in _tmp3:
						_tmp3 = _tmp3.replace('"', '&quot;')
					_write((' src="' + _tmp3) + '"')
				_write(u'></script>')
			u'inline'
			_tmp3 = _path(inline, econtext['request'], True)
			if _tmp3:
				pass
				u"''"
				_write(u'')
				_default.value = default = ''
				u'script/content'
				_content = _path(script, econtext['request'], True, 'content')
				u'_content'
				_write(u'<script type="text/javascript">')
				_tmp3 = _content
				_tmp = _tmp3
				if (_tmp.__class__ not in (str, unicode, int, float) and hasattr(_tmp, '__html__')):
					_write(_tmp.__html__())
				elif _tmp is not None:
					if not (isinstance(_tmp, unicode)):
						_tmp = str(_tmp)
					_write(_tmp)
				_write(u'</script>')
			u'condcomment'
			_tmp3 = _path(condcomment, econtext['request'], True)
			if _tmp3:
				pass
				u"''"
				_write(u'')
				_default.value = default = ''
				u'<![endif]-->'
				_content = u'<![endif]-->'
				u'_content'
				_tmp3 = _content
				_tmp = _tmp3
				if (_tmp.__class__ not in (str, unicode, int, float) and hasattr(_tmp, '__html__')):
					_write(_tmp.__html__())
				elif _tmp is not None:
					if not (isinstance(_tmp, unicode)):
						_tmp = str(_tmp)
					_write(_tmp)
				_write(u'')
			if _tmp2 == 0:
				break
			_write(' ')
		return _out.getvalue()
	return render

registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()

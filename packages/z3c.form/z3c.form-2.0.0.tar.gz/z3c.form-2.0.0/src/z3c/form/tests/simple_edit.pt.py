registry = dict(version='2.1.3.7')
def bind():
	from cPickle import loads as _loads
	_init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
	_lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
	_init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
	_re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
	_init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
	_lookup_name = _loads('cchameleon.core.codegen\nlookup_name\np1\n.')
	_init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
	_path = _loads("ccopy_reg\n_reconstructor\np1\n(cz3c.pt.expressions\nZopeTraverser\np2\nc__builtin__\nobject\np3\nNtRp4\n(dp5\nS'proxify'\np6\ncz3c.pt.expressions\nidentity\np7\nsb.")
	def render(econtext, rcontext=None):
		macros = econtext.get('macros')
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
		_write(u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml">       \n  <body>\n    ')
		_default.value = default = ''
		u'view/status'
		_tmp1 = _path(econtext['view'], econtext['request'], True, 'status')
		if _tmp1:
			pass
			u'view/status'
			_content = _path(econtext['view'], econtext['request'], True, 'status')
			u'_content is None'
			_tmp1 = _content is None
			if not (_tmp1):
				pass
				_write(u'<i>')
			u'_content'
			_tmp2 = _content
			_tmp = _tmp2
			if (_tmp.__class__ not in (str, unicode) and hasattr(_tmp, '__html__')):
				_write(_tmp.__html__())
			elif _tmp is not None:
				if not (isinstance(_tmp, unicode)):
					_tmp = str(_tmp)
				if '&' in _tmp:
					if ';' in _tmp:
						_tmp = _re_amp.sub('&amp;', _tmp)
					else:
						_tmp = _tmp.replace('&', '&amp;')
				if '<' in _tmp:
					_tmp = _tmp.replace('<', '&lt;')
				if '>' in _tmp:
					_tmp = _tmp.replace('>', '&gt;')
				_write(_tmp)
			if not (_tmp1):
				pass
				_write(u'</i>')
		u'view/widgets/errors'
		_write(u'\n    ')
		_tmp1 = _path(econtext['view'], econtext['request'], True, 'widgets', 'errors')
		if _tmp1:
			pass
			u'view/widgets/errors'
			_write(u'<ul>\n      ')
			_tmp1 = _path(econtext['view'], econtext['request'], True, 'widgets', 'errors')
			error = None
			_tmp1 = repeat.insert('error', _tmp1)
			try:
				error = _tmp1.next()
				while True:
					u'error/widget'
					_write(u'<li>\n        ')
					_tmp2 = _path(error, econtext['request'], True, 'widget')
					if _tmp2:
						pass
						u"''"
						_write(u'')
						_default.value = default = ''
						u'error/widget/label'
						_content = _path(error, econtext['request'], True, 'widget', 'label')
						u'_content'
						_tmp2 = _content
						_tmp = _tmp2
						if (_tmp.__class__ not in (str, unicode) and hasattr(_tmp, '__html__')):
							_write(_tmp.__html__())
						elif _tmp is not None:
							if not (isinstance(_tmp, unicode)):
								_tmp = str(_tmp)
							if '&' in _tmp:
								if ';' in _tmp:
									_tmp = _re_amp.sub('&amp;', _tmp)
								else:
									_tmp = _tmp.replace('&', '&amp;')
							if '<' in _tmp:
								_tmp = _tmp.replace('<', '&lt;')
							if '>' in _tmp:
								_tmp = _tmp.replace('>', '&gt;')
							_write(_tmp)
						_write(u':')
					u"''"
					_write(u'\n')
					_default.value = default = ''
					u'error/render'
					_content = _path(error, econtext['request'], True, 'render')
					u'_content'
					_tmp2 = _content
					_tmp = _tmp2
					if (_tmp.__class__ not in (str, unicode) and hasattr(_tmp, '__html__')):
						_write(_tmp.__html__())
					elif _tmp is not None:
						if not (isinstance(_tmp, unicode)):
							_tmp = str(_tmp)
						_write(_tmp)
					_write(u'\n</li>')
					error = _tmp1.next()
					_write(' ')
			except StopIteration:
				error = None
			_write(u'\n    </ul>')
		u'view/widgets/values'
		_write(u'\n    <form action=".">\n      ')
		_tmp1 = _path(econtext['view'], econtext['request'], True, 'widgets', 'values')
		widget = None
		_tmp1 = repeat.insert('widget', _tmp1)
		try:
			widget = _tmp1.next()
			while True:
				u"''"
				_write(u'<div class="row">\n        ')
				_default.value = default = ''
				u'widget/error'
				_tmp2 = _path(widget, econtext['request'], True, 'error')
				if _tmp2:
					pass
					u'widget/error/render'
					_content = _path(widget, econtext['request'], True, 'error', 'render')
					u'_content is None'
					_tmp2 = _content is None
					if not (_tmp2):
						pass
						_write(u'<b>')
					u'_content'
					_tmp3 = _content
					_tmp = _tmp3
					if (_tmp.__class__ not in (str, unicode) and hasattr(_tmp, '__html__')):
						_write(_tmp.__html__())
					elif _tmp is not None:
						if not (isinstance(_tmp, unicode)):
							_tmp = str(_tmp)
						_write(_tmp)
					if not (_tmp2):
						pass
						_write(u'</b>')
				u"''"
				_default.value = default = ''
				u'widget/label'
				_content = _path(widget, econtext['request'], True, 'label')
				u'_content is None'
				_tmp2 = _content is None
				if not (_tmp2):
					pass
					u'widget/id'
					_write(u'<label')
					_tmp3 = _path(widget, econtext['request'], True, 'id')
					if _tmp3 is _default:
						_tmp3 = u''
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
						_write((' for="' + _tmp3) + '"')
					_write('>')
				u'_content'
				_tmp3 = _content
				_tmp = _tmp3
				if (_tmp.__class__ not in (str, unicode) and hasattr(_tmp, '__html__')):
					_write(_tmp.__html__())
				elif _tmp is not None:
					if not (isinstance(_tmp, unicode)):
						_tmp = str(_tmp)
					if '&' in _tmp:
						if ';' in _tmp:
							_tmp = _re_amp.sub('&amp;', _tmp)
						else:
							_tmp = _tmp.replace('&', '&amp;')
					if '<' in _tmp:
						_tmp = _tmp.replace('<', '&lt;')
					if '>' in _tmp:
						_tmp = _tmp.replace('>', '&gt;')
					_write(_tmp)
				if not (_tmp2):
					pass
					_write(u'</label>')
				u"''"
				_write(u'\n        ')
				_default.value = default = ''
				u'widget/render'
				_content = _path(widget, econtext['request'], True, 'render')
				u'_content'
				_tmp2 = _content
				_tmp = _tmp2
				if (_tmp.__class__ not in (str, unicode) and hasattr(_tmp, '__html__')):
					_write(_tmp.__html__())
				elif _tmp is not None:
					if not (isinstance(_tmp, unicode)):
						_tmp = str(_tmp)
					_write(_tmp)
				_write(u'</div>')
				widget = _tmp1.next()
				_write(' ')
		except StopIteration:
			widget = None
		u'view/actions/values'
		_write(u'\n      ')
		_tmp1 = _path(econtext['view'], econtext['request'], True, 'actions', 'values')
		action = None
		_tmp1 = repeat.insert('action', _tmp1)
		try:
			action = _tmp1.next()
			while True:
				u"''"
				_write(u'<div class="action">\n        ')
				_default.value = default = ''
				u'action/render'
				_content = _path(action, econtext['request'], True, 'render')
				u'_content'
				_tmp2 = _content
				_tmp = _tmp2
				if (_tmp.__class__ not in (str, unicode) and hasattr(_tmp, '__html__')):
					_write(_tmp.__html__())
				elif _tmp is not None:
					if not (isinstance(_tmp, unicode)):
						_tmp = str(_tmp)
					_write(_tmp)
				_write(u'</div>')
				action = _tmp1.next()
				_write(' ')
		except StopIteration:
			action = None
		_write(u'\n    </form>\n  </body>\n</html>')
		return _out.getvalue()
	return render

registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()

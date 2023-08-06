def bind():
	from cPickle import loads as _loads
	_init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
	_lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
	_init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
	_init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
	_lookup_name = _loads('cchameleon.core.codegen\nlookup_name\np1\n.')
	def render(xincludes, target_language=None):
		(_out, _write) = _init_stream()
		u'_init_scope()'
		econtext = _init_scope()
		u'_init_tal()'
		(_attributes, repeat) = _init_tal()
		u'None'
		_domain = None
		"join('xinclude', value('2'), '.html')"
		_write('<div>\n  ')
		_include = ('%s%s%s' % ('xinclude', 2, '.html'))
		u"%(xincludes)s.get(%(include)s, 'xml').render_xinclude(_domain=_domain, xincludes=xincludes, econtext=econtext, _out=_out, _write=_write, target_language=target_language)"
		_tmp1 = _lookup_attr(_lookup_attr(xincludes, 'get')(_include, 'xml'), 'render_xinclude')(_domain=_domain, xincludes=xincludes, econtext=econtext, _out=_out, _write=_write, target_language=target_language)
		_tmp = _tmp1
		if _tmp is not None:
			if not (isinstance(_tmp, basestring)):
				_tmp = str(_tmp)
			_write(_tmp)
		_write('\n  ')
		u"greeting('world')"
		_tmp1 = _lookup_name(econtext, 'greeting')('world')
		_tmp = _tmp1
		if _tmp is not None:
			if not (isinstance(_tmp, basestring)):
				_tmp = str(_tmp)
			_write(_tmp)
		_write('\n')
		_write('</div>')
		_write('\n')
		return _out.getvalue()
	return render

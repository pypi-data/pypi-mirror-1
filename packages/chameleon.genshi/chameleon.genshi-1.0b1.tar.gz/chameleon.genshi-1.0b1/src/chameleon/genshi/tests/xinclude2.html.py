def bind():
	from cPickle import loads as _loads
	_init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
	_lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
	_init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
	_init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
	_lookup_name = _loads('cchameleon.core.codegen\nlookup_name\np1\n.')
	def render(_domain=None, xincludes=None, econtext=None, _out=None, _write=None, target_language=None):
		(_attributes, repeat) = _init_tal()
		u'None'
		_domain = None
		_write('\n  ')
		def greeting(name):
			_write('<p class="greeting">\n    Hello, ')
			_tmp1 = name
			_tmp = _tmp1
			if _tmp is not None:
				if not (isinstance(_tmp, basestring)):
					_tmp = str(_tmp)
				_write(_tmp)
			_write('!\n  ')
			_write('</p>')
		u'greeting'
		econtext['greeting'] = greeting
		_write('\n')
		_write('\n')
		return None
	return render

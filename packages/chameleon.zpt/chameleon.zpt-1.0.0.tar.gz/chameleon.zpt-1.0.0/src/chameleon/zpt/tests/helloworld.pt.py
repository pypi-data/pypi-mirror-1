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
		_write('<div xmlns="http://www.w3.org/1999/xhtml">\n  Hello World!\n</div>')
		return _out.getvalue()
	return render

import os.path
import dv.xdvserver

from dv.xdvserver import xdvcompiler

COMPILER = os.path.join(os.path.split(dv.xdvserver.__file__)[0], 'compiler', 'compiler.xsl')

def get_host(request):
    """Try to get HTTP host even if there's no HOST header.
    """
    
    base = request.get('BASE0')
    if base:
        divider = base.find('://')
        if divider > 0:
            base = base[divider+3:]
        
        if base:
            return base
    
    host = request.get('HTTP_HOST')
    if host:
        return host
    
    return "%s:%s" % (request.get('SERVER_NAME'), request.get('SERVER_PORT'))

def compile_theme(theme, rules, boilerplate=None, absolute_prefix=None, extraurl=None, compiler=COMPILER):
    """Given a them file/URI and a rules file, and optionally a boilerplate
    file and/or an absolute prefix, return a compiled theme XSLT file as a
    string.
    """
    return xdvcompiler.compile_theme(compiler, theme, rules, boilerplate, absolute_prefix, extraurl)
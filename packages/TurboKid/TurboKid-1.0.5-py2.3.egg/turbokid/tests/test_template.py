"""TurboKid tests."""

import os
import sys
import time

from turbokid import KidSupport

values = dict(v='My value!', one=1)

def extra_vars():
    return dict(x='Extra value!', two=2)

options = {
    'kid.assume_encoding': 'utf-8',
    'kid.encoding': 'utf-8',
    'kid.precompiled': False,
    'kid.sitetemplate': 'turbokid.tests.site',
    'dummy': 'does nothing'
}

def get_engine():
    return KidSupport(extra_vars, options)


def test_options():
    """Make sure all engine options are set."""
    engine = get_engine()
    opt = engine.options
    assert opt['dummy'] == 'does nothing'
    assert opt['kid.assume_encoding'] == engine.assume_encoding == 'utf-8'
    assert opt['kid.encoding'] == engine.encoding == 'utf-8'
    assert opt['kid.precompiled'] == engine.precompiled == False
    assert opt['kid.sitetemplate'] == engine.stname == 'turbokid.tests.site'

def test_simple():
    """Make sure a simple test works."""
    engine = get_engine()
    s = engine.render(values, template='turbokid.tests.simple')
    s = s.splitlines()[-1]
    assert s == '<p>Check: My value!</p>'

def test_kid():
    """Make sure kid directives work."""
    engine = get_engine()
    values = {'title': 'Fruit Test', 'fruits': 'apple orange kiwi M&M'.split()}
    s = engine.render(values, template='turbokid.tests.fruits')
    assert s == """<!DOCTYPE HTML PUBLIC \
"-//W3C//DTD HTML 4.01 Transitional//EN" \
"http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
<title>Fruit Test</title>
  </head>
  <body>
    <p>These are some of my favorite fruits:</p>
    <ul>
      <li>
        I like apples
      </li><li>
        I like oranges
      </li><li>
        I like kiwis
      </li><li>
        I like M&amp;Ms
      </li>
    </ul>
  </body>
</html>"""

def test_not_found():
    """Make sure undefined variables do not go unnoticed."""
    engine = get_engine()
    try:
        s = engine.render(None, template='turbokid.tests.simple')
    except NameError:
        pass
    except Exception, e:
        assert False, 'Undefined name raised wrong exception (%s)' % str(e)
    else:
        assert s.splitlines()[-1] != 'Check:', 'Undefined name was ignored'
        assert False, 'Undefined name did not raise any exception'

def test_extra():
    """Make sure extra variables work."""
    engine = get_engine()
    s = engine.render(None, template='turbokid.tests.extra')
    s = s.splitlines()[-1]
    assert s == '<p>Another check: Extra value!</p>'

def test_unicode():
    """Make sure unicode values work."""
    engine = get_engine()
    s = engine.render({'v': u"K\xe4se!"}, template='turbokid.tests.simple')
    assert isinstance(s, str)
    s = s.splitlines()[-1]
    assert s == u'<p>Check: K\xe4se!</p>'.encode('utf-8')

def test_extend():
    """Make sure one template can inherit from another."""
    engine = get_engine()
    values = {'name': 'World', 'flash': 'flash',
        'header': 'head', 'footer': 'foot'}
    s = engine.render(values, template='turbokid.tests.hello')
    assert s == """<!DOCTYPE HTML PUBLIC \
"-//W3C//DTD HTML 4.01 Transitional//EN" \
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
<title>Welcome to TurboKid</title>
    <meta content="master" name="siteinfo">
    <meta content="turbokid" name="siteinfo">
</head>
<body>
    <div>top</div>
    <div>head</div>
    <div>flash</div>
    <h1>Hello, World!</h1>
    <div>foot</div>
    <div>bottom</div>
</body>
</html>"""

def test_template_string():
    """Check rendering of template strings."""
    engine = get_engine()
    t = engine.load_template(values, template_string='<p>String: $v</p>')
    s = t(**values).serialize().splitlines()[-1]
    assert s == '<p>String: My value!</p>'

def load_and_render(engine, template, **kwargs):
    """Auxiliary function for loading and rendering a template."""
    template = engine.load_template('turbokid.tests.%s' % template)
    engine.render(kwargs, template=template)
    return template

def touch(template, times=None):
    """Auxiliary function for changing the modification time of a template."""
    fname = sys.modules['turbokid.tests.%s' % template].__file__
    fhandle = file(fname, 'a')
    try:
        for n in range(6):
            mtime = os.stat(fname).st_mtime
            os.utime(fname, times)
            if times or os.stat(fname).st_mtime != mtime:
                break
            time.sleep(0.5)
        else:
            raise OSError("Could not change modification time of %s." % fname)
    finally:
        fhandle.close()

def test_use_cache():
    """Make sure that load_template returns cached templates if there are no changes."""
    engine = get_engine()
    a1 = load_and_render(engine, 'a')
    b1 = load_and_render(engine, 'b')    
    a2 = load_and_render(engine, 'a')
    b2 = load_and_render(engine, 'b')
    assert a1 is a2
    assert b1 is b2

def test_template_reloads():
    """Make sure that templates reloads when it was changed."""
    engine = get_engine()
    a1 = load_and_render(engine, 'a')
    b1 = load_and_render(engine, 'b')
    touch('a')    
    a2 = load_and_render(engine, 'a')
    b2 = load_and_render(engine, 'b')
    assert a1 is not a2
    assert b1 is not b2

def test_relations_1():
    """Make sure that template reloads in relations 1."""
    engine = get_engine()   
    a1 = load_and_render(engine, 'a')
    b1 = load_and_render(engine, 'b')
    c1 = load_and_render(engine, 'c')
    d1 = load_and_render(engine, 'd')
    touch('a')
    a2 = load_and_render(engine, 'a')
    b2 = load_and_render(engine, 'b')
    c2 = load_and_render(engine, 'c')
    d2 = load_and_render(engine, 'd')
    assert a1 is not a2
    assert b1 is not b2
    assert c1 is not c2
    assert d1 is not d2

def test_relations_2():
    """Make sure that template reloads in relations 2."""
    engine = get_engine()   
    a1 = load_and_render(engine, 'a')
    b1 = load_and_render(engine, 'b')
    c1 = load_and_render(engine, 'c')
    d1 = load_and_render(engine, 'd')
    touch('a')
    c2 = load_and_render(engine, 'c')
    a2 = load_and_render(engine, 'a')
    d2 = load_and_render(engine, 'd')
    b2 = load_and_render(engine, 'b')
    assert a1 is not a2
    assert b1 is not b2
    assert c1 is not c2
    assert d1 is not d2

def test_relations_3():
    """Make sure that template reloads in relations 3."""
    engine = get_engine()
    tmpls = 'abcde'
    for t1 in tmpls:
        for t2 in tmpls:
            load_and_render(engine, t2)
        touch(t1)
        for t2 in tmpls:
            load_and_render(engine, t2)

def test_relations_4():
    """Make sure that template reloads in relations 4."""
    engine = get_engine()
    tmpls = 'cebae' # use random order
    for t1 in tmpls:
        for t2 in tmpls:
            load_and_render(engine, t2)
        touch(t1)
        for t2 in tmpls:
            load_and_render(engine, t2)

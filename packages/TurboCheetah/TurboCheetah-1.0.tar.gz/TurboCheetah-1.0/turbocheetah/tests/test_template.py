"""TurboCheetah tests."""

import os
from turbocheetah import CheetahSupport


# Note: To test with the precompiled or without the importhooks feature,
# you need to compile the templates manually with "cheetah-compile".

importhooks = True
precompiled = False


here = os.path.dirname(__file__)

values = { 'v': 'My value!', 'one': 1 }

def extra_vars():
    return { 'x': 'Extra value!', 'two': 2 }

options = {
    'cheetah.importhooks': importhooks,
    'cheetah.precompiled': precompiled,
    'dummy': 'does nothing'
}

def get_engine():
    return CheetahSupport(extra_vars, options)

def check_lines(expect, result):
    """Check lines of result against expectation after stripping lines."""
    expect = expect.splitlines()
    result = result.splitlines()
    for expect_line, result_line in zip(expect, result):
        expect_line = expect_line.strip()
        result_line = result_line.strip()
        assert result_line == expect_line, \
            '\nExpect: %r\nResult: %r' % (expect_line, result_line)


def test_options():
    """Make sure all engine options are set."""
    engine = get_engine()
    opt = engine.options
    assert opt['dummy'] == 'does nothing'
    assert opt['cheetah.importhooks'] == engine.importhooks == importhooks
    assert opt['cheetah.precompiled'] == engine.precompiled == precompiled

def test_simple():
    """Make sure a simple test works."""
    engine = get_engine()
    s = engine.render(values, template='turbocheetah.tests.simple')
    assert s.strip() == 'Check: My value!'

def test_not_found():
    """Make sure undefined variables do not go unnoticed."""
    try:
        from Cheetah.NameMapper import NotFound
    except ImportError:
        assert False, 'Cheetah.NameMapper does not export NotFound error'
    engine = get_engine()
    try:
        s = engine.render(None, template='turbocheetah.tests.simple')
    except NotFound:
        pass
    except Exception, e:
        assert False, 'Undefined name raised wrong exception (%s)' % str(e)
    else:
        assert s.strip() != 'Check:', 'Undefined name was ignored'
        assert False, 'Undefined name did not raise any exception'

def test_extra():
    """Make sure extra variables work."""
    engine = get_engine()
    s = engine.render(None, template='turbocheetah.tests.extra')
    assert s.strip() == 'Another check: Extra value!'

def test_unicode():
    """Make sure unicode values work."""
    engine = get_engine()
    s = engine.render({'v': u"K\xe4se!"}, template='turbocheetah.tests.simple')
    assert isinstance(s, unicode)
    assert s.strip() == u'Check: K\xe4se!'

def test_extend():
    """Make sure one template can inherit from another."""
    engine = get_engine()
    s = engine.render(None, template='turbocheetah.tests.page')
    assert s.strip() == 'Hello! Welcome to TurboCheetah!'

def test_sub():
    """Make sure we can use subpackages."""
    engine = get_engine()
    check_lines(engine.render(None, template='turbocheetah.tests.subpage'),
        'Hello from my subpackage! Welcome to my subpage.')
    check_lines(engine.render(None, template='turbocheetah.tests.sub.page'),
        'Hello from my subpackage! Welcome to my subpackage page.')

def test_tricky():
    """Make sure we can do trickier things."""
    engine = get_engine()
    check_lines(engine.render(values, template='turbocheetah.tests.page2'),
        """Hello from my subpackage!\n
        This is getting tricky:\n
        # the data\n1: My value!\n2: Extra value!
        # the end\nThat's all, folks!""")

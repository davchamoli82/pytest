import pytest
import sys

@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    yield
    config = request.config
    if config.option.setuponly:
        if hasattr(request, 'param'):
            # Save the fixture parameter so ._show_fixture_action() can
            # display it now and during the teardown (in .finish()).
            if fixturedef.ids:
                if callable(fixturedef.ids):
                    fixturedef.cached_param = fixturedef.ids(request.param)
                else:
                    fixturedef.cached_param = fixturedef.ids[request.param_index]
            else:
                fixturedef.cached_param = request.param
        _show_fixture_action(fixturedef, 'SETUP')

def pytest_fixture_post_finalizer(fixturedef):
    if hasattr(fixturedef, "cached_result"):
        config = fixturedef._fixturemanager.config
        if config.option.setuponly:
            _show_fixture_action(fixturedef, 'TEARDOWN')
            if hasattr(fixturedef, "cached_param"):
                del fixturedef.cached_param

def _show_fixture_action(fixturedef, msg):
    config = fixturedef._fixturemanager.config
    capman = config.pluginmanager.getplugin('capturemanager')
    if capman:
        out, err = capman.suspendcapture()

    tw = config.get_terminal_writer()
    tw.line()
    tw.write(' ' * 2 * fixturedef.scopenum)
    tw.write('{step} {scope} {fixture}'.format(
        step=msg.ljust(8),  # align the output to TEARDOWN
        scope=fixturedef.scope[0].upper(),
        fixture=fixturedef.argname))

    if msg == 'SETUP':
        deps = sorted(arg for arg in fixturedef.argnames if arg != 'request')
        if deps:
            tw.write(' (fixtures used: {0})'.format(', '.join(deps)))

    if hasattr(fixturedef, 'cached_param'):
        tw.write('[{0}]'.format(fixturedef.cached_param))

    if capman:
        capman.resumecapture()
        sys.stdout.write(out)
        sys.stderr.write(err)

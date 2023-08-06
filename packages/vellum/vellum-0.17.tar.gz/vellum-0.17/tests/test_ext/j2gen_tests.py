


from nose.tools import *
from vellum.scribe import Scribe
from vellum.script import Script
import os
import vellum
from vellum.parser import Reference

import tempfile

def test_system():
    s = Script('tests/test_ext/j2gen_data/j2gen_build')
    scribe = Scribe(s)
    assert scribe.is_command('jinja2gen.gen')

    input = 'tests/test_ext/j2gen_data/j2gen_template.jinja'
    output = 'tests/test_ext/j2gen_data/j2gen_template_out.txt'
    scribe.command('jinja2gen.gen',
        dict(input=input, output=output, test='goo'))

    assert os.path.exists(output)

    from jinja2 import Template
    f = open(input, 'r')
    t = Template(f.read())
    f.close()

    f = open(output, 'r')
    o = f.read()
    f.close()

    assert t.render(test='goo') == open(output).read()

    os.unlink(output)



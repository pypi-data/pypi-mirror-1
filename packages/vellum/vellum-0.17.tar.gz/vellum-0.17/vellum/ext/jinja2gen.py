
import os

def gen(scribe, input=None, output=None, **expr):
    """
    Like the core gen command, but using jinja2 templates.

    Used to do simple code generation tasks.  It
    expects a "from" and "to" argument in a dict
    then it loads from, renders the
    whole thing against the expr merged with the
    options, and finally writes the results to "to".

    Usage:  gen(input somefile.txt output outfile.txt other "variable")
    """
    scribe.log("jinja2gen: input %s output %s" % (input, output) )
    if not (input and output):
        scribe.die("jinja2gen", "You must give both input and output for gen.")

    if scribe.option("dry_run"):
        return
    expr.update(scribe.options)

    # We need this to be nice, so we make a full environment
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        scribe.die('Jinja2 is not installed. easy_install jinja2')
    templates_dir = scribe.options.get('jinja2_templates_dir',
                                        os.path.dirname(input))
    j2env = Environment(loader=FileSystemLoader(templates_dir))
    template = j2env.get_template(os.path.basename(input))

    rendered = template.render(**expr)

    f = open(output,'w')
    f.write(rendered)
    f.close()


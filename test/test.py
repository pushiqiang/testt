import yaml
from jinja2 import Template
from jinja2 import Environment

import jinja2_highlight


env = Environment(extensions=['jinja2_highlight.HighlightExtension'])

stream = file('fru.yml', 'r')

swagger= yaml.load(stream)

fp_tpl = file('swagger.html', 'r')

#template = Template(fp_tpl.read())
template = env.from_string(fp_tpl.read())

result = template.render(page=page)
       
fr = open('res.html', "w")
fr.write(result)
fr.close()

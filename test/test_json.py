# encoding=utf8
import json
from jinja2 import Template
from jinja2 import Environment

import jinja2_highlight


env = Environment(extensions=['jinja2_highlight.HighlightExtension'])

stream = file('swagger.json', 'r')
data = stream.read()

swagger= json.loads(data, )

fp_tpl = file('swagger.html', 'r')

#template = Template(fp_tpl.read())
template = env.from_string(fp_tpl.read())

result = template.render(swagger=swagger)
       
fr = open('res_json.html', "w")
fr.write(result)
fr.close()

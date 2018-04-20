import os
from jinja2 import Environment, FileSystemLoader
from constants import *

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
         autoescape=False,
         loader=FileSystemLoader(os.path.join(PATH, 'templates')),
         trim_blocks=False)


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_index_html():
     fname = "output.html"
     urls = ['http://example.com/1', 'http://example.com/2', 'http://example.com/3']
     context = {
             'urls': urls
             }
     #
     with open(fname, 'w') as f:
         html = render_template('index.html', context)
         f.write(html)

def create_plc_scripts():

    for k,v in varmap.iteritems():
        context = { "name_plc" : k, "variable_type" : v} 
        fname = "plcs/script_plc_"+k
        with open(fname, 'w') as f:
            plc_script = render_template('script_plc_template.py', context)
            f.write(plc_srcipt)
            



def main():
    create_plc_scripts()

########################################

if __name__ == "__main__":
    main()

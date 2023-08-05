"Template support for jinja"

try:
    from jinja import Template, Context, StringLoader#FileSystemLoader
except:
    print "jinja not found. You should install jinja first to use jinja template"
    raise
import pkg_resources

class TurboJinja:
    extension = "html"

    def __init__(self, extra_vars_func=None, options=None):
        self.get_extra_vars = extra_vars_func
        if options:
            self.options = options
        else:
            self.options = dict()

        
    def load_template(self, template_name):
        """template_name == dotted.path.to.template (without .ext)

        Searches for a template along the Python path.

        Template files must end in ".html" and be in legitimate packages.
        """
        
        divider = template_name.rfind(".")
        if divider > -1:
            package = template_name[0:divider]
            basename = template_name[divider+1:]
        else:
            raise ValueError, "All templates must be in a package"

        template_file_path = pkg_resources.resource_filename(package,
                                                        "%s.html" % basename)
        
        template_file = open(template_file_path)
                                                    
        template_obj = Template(template_file.read(), StringLoader())
        
        return template_obj

    def render(self, info, format="html", fragment=False, template=None):
        vars = info

        if callable(self.get_extra_vars):
            vars.update(self.get_extra_vars())

        tclass = self.load_template(template)

        return tclass.render(Context(vars))


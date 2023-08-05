from vectorformats.Feature import Feature
from vectorformats.Formats.Format import Format

from Cheetah.Template import Template

class HTML (Format):
    template_file = "template/default.html"

    def encode(self, result):
        template = self.template()
        output = Template(template, searchList = [{'features':result}, self])
        return str(output)
    
    def template(self):
        return file(self.template_file).read()

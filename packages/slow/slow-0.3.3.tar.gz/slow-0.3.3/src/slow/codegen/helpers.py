OVERML_NAMESPACE  = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML"
SLOW_NAMESPACE    = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/slow"
NALA_NAMESPACE    = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/nala"
SLOSL_NAMESPACE   = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/slosl"
HIMDEL_NAMESPACE  = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/himdel"
EDSL_NAMESPACE    = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/edsl"
SLOWGUI_NAMESPACE = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/slow-gui"
CODEGEN_NAMESPACE = "http://www.dvs1.informatik.tu-darmstadt.de/research/OverML/codegen"

XSD_NAMESPACE     = "http://www.w3.org/2001/XMLSchema-datatypes"
MATH_NAMESPACE    = "http://www.w3.org/1998/Math/MathML"


from lxml.etree import ElementBase, Namespace

class CodegenElement(ElementBase):
    def __getattr__(self, name):
        try:
            return self.get(name)
        except AttributeError:
            pass
        for child in self:
            local_name = child.tag.split('}', 1)[-1]
            if local_name == name:
                return child
        raise AttributeError, "Cannot find attribute or element of name '%s'." % name

Namespace(CODEGEN_NAMESPACE)[None] = CodegenElement


def capitalize(name):
    return ''.join(
        part.capitalize()
        for part in name.split('_')
        )


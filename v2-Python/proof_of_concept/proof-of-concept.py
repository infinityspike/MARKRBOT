from svg_to_gcode.svg_parser import parse_string
from svg_to_gcode.compiler import Compiler, interfaces
from MarkrbotGcode import MarkrbotGcode
from xml.etree import ElementTree
from SVGtransformAdapter import adaptSVGTransformElementsIntoPath


# Instantiate a compiler, specifying the interface type and the speed at which the tool should move. pass_depth controls
# how far down the tool moves after every pass. Set it to 0 if your machine does not support Z axis movement.
gcode_compiler = Compiler(interfaces.Gcode, movement_speed=1000, cutting_speed=300, pass_depth=0)

import ziafont

svg = ElementTree.parse("./proof_of_concept/test-svgs/drawing.svg").getroot()

ziafont.config.svg2 = False
font = ziafont.Font('./proof_of_concept/test-fonts/Arizonia-Regular.ttf')
svg2 = font.text('One\nTwo\nThree\nFour\nFive\nSix', size=10).svgxml()

svg1p = ElementTree.tostring(svg, encoding='unicode')
curves = parse_string(svg1p)

gcode_compiler.append_curves(curves)
gcode_compiler.compile_to_file("./proof_of_concept/test-gcode/drawing.gcode")

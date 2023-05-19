from xml.etree.ElementTree import Element
#deprecated
def adaptSVGTransformElementsIntoPath(svg:Element) :

    newsvg:Element = svg

    existingsymbols = newsvg.findall('symbol')

    t = newsvg.find('g')
    transforms = t.findall('use')
    ressvg = Element('svg',svg.attrib.copy())

    for transform in transforms :
        for sym in existingsymbols :
            if '#' + sym.attrib['id'] == transform.attrib['href'] :
                ressvg.append(Element("path",{"transform":transform.attrib['transform'], "d":sym.find('path').attrib['d']}))
                #sym.find('path').attrib['transform'] = transform.attrib['transform']
    return ressvg





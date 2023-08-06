import unittest
import xml.etree.ElementTree as et

from odplib import preso

class TestScript(unittest.TestCase):
    def test_basic_preso(self):
        p = preso.Preso()
        self.assertEquals(p.to_xml(), '<office:document-content office:version="1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><office:scripts /><office:automatic-styles /><office:body><office:presentation /></office:body></office:document-content>')

    def test_basic_slide_title(self):
        p = preso.Preso()
        s = p.add_slide()
        t = s.add_title_frame()
        t.write("FOO")
        self.assertEquals(t.to_xml(), '<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="Default-subtitle" svg:height="2.533cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="10.577cm"><draw:text-box><text:p text:style-name="P1">FOO</text:p></draw:text-box></draw:frame>')

    def test_slide_copy(self):
        p = preso.Preso()
        s = p.add_slide()
        t = s.add_title_frame()
        t.write('copy me')
        n = s.add_notes_frame()
        copy = p.copy_slide(s)
        self.assertEquals(copy.to_xml(), '')

    def test_indent_1(self):
        o = preso.OutlineList()
        o.new_item('A')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L1"><text:list-item><text:p text:style-name="P2">A</text:p></text:list-item></text:list>')
        o.new_item('B')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L1"><text:list-item><text:p text:style-name="P2">A</text:p></text:list-item><text:list-item><text:p text:style-name="P2">B</text:p></text:list-item></text:list>')
        o.indent()
        o.new_item('1')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L1"><text:list-item><text:p text:style-name="P2">A</text:p></text:list-item><text:list-item><text:p text:style-name="P2">B</text:p></text:list-item><text:list><text:list-item><text:p text:style-name="P2">1</text:p></text:list-item></text:list></text:list>')

    def test_list_style(self):
        o = preso.OutlineList()
        tree = et.fromstring(o.default_styles())
        xml = preso.to_xml(tree)
        self.assertEquals(xml, '')

    def test_mixed_content(self):
        m = preso.MixedContent('p')
        m.write('This text is ')
        m.add_node('b')
        m.write('bold')
        m.pop_node()
        m.write('This is not')
        xml = preso.to_xml(m.get_node())


        self.assertEquals(xml, '')

    def test_code(self):
        p = preso.Preso()
        s = p.add_slide()
        s.add_code("print 'hello world'", 'python')
        self.assertEquals(s.to_xml(), '')

    def test_new_outline(self):
        p = preso.Preso()
        s = p.add_slide()
        o = preso.OutlineList(s)
        o.new_item('foo')
        o.new_item('bar')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L2"><text:list-item><text:p text:style-name="P1"><text:span>foo</text:span></text:p></text:list-item><text:list-item><text:p text:style-name="P1"><text:span>bar</text:span></text:p></text:list-item></text:list>')
        
        o.indent()
        o.new_item('barbie')
        self.assertEquals(o.to_xml(), '')

if __name__ == "__main__":
    unittest.main()

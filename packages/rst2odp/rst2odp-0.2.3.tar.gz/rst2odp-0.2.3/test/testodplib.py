import unittest
import xml.etree.ElementTree as et

from odplib import preso

class TestScript(unittest.TestCase):
    def test_basic_preso(self):
        p = preso.Preso()
        self.assertEquals(p.to_xml(),'<office:document-content office:version="1.0" xmlns:anim="urn:oasis:names:tc:opendocument:xmlns:animation:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:smil="urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><office:scripts /><office:automatic-styles /><office:body><office:presentation /></office:body></office:document-content>')

    def test_basic_slide_title(self):
        p = preso.Preso()
        s = p.add_slide()
        t = s.add_title_frame()
        t.write("FOO")
        self.assertEquals(t.to_xml(), '<draw:frame draw:layer="layout" presentation:class="title" presentation:style-name="Default-title" svg:height="1.737cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="1.721cm"><draw:text-box><text:p text:style-name="P0">FOO</text:p></draw:text-box></draw:frame>')

    def test_slide_copy(self):
        p = preso.Preso()
        s = p.add_slide()
        t = s.add_title_frame()
        t.write('copy me')
        n = s.add_notes_frame()
        copy = p.copy_slide(s)
        self.assertEquals(copy.to_xml(), '<draw:page draw:master-page-name="Default" draw:name="page1" draw:style-name="dp1" presentation:presentation-page-layout-name="AL1T0"><office:forms form:apply-design-mode="false" form:automatic-focus="false" /><draw:frame draw:layer="layout" presentation:class="title" presentation:style-name="Default-title" svg:height="1.737cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="1.721cm"><draw:text-box><text:p text:style-name="P0">copy me</text:p></draw:text-box></draw:frame><presentation:notes draw:style-name="dp2"><draw:page-thumbnail draw:layer="layout" draw:page-number="2" presentation:class="page" presentation:style-name="gr1" svg:height="10.476cm" svg:width="13.968cm" svg:x="3.81cm" svg:y="2.123cm" /><draw:frame draw:layer="layout" presentation:class="notes" presentation:placeholder="true" presentation:style-name="pr1" svg:height="12.322cm" svg:width="17.271cm" svg:x="2.159cm" svg:y="13.271cm"><draw:text-box /></draw:frame></presentation:notes></draw:page>')

    def test_indent_1(self):
        p = preso.Preso()
        s = p.add_slide()
        o = preso.OutlineList(s)
        o.new_item('A')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L2"><text:list-item><text:p text:style-name="P3">A</text:p></text:list-item></text:list>')
        o.new_item('B')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L2"><text:list-item><text:p text:style-name="P3">A</text:p></text:list-item><text:list-item><text:p text:style-name="P3">B</text:p></text:list-item></text:list>')
        o.indent()
        o.new_item('1')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L2"><text:list-item><text:p text:style-name="P3">A</text:p></text:list-item><text:list-item><text:p text:style-name="P3">B</text:p></text:list-item><text:list-item><text:list><text:list-item><text:p text:style-name="P3">1</text:p></text:list-item></text:list></text:list-item></text:list>')

    def test_list_style(self):
        p = preso.Preso()
        s = p.add_slide()
        o = preso.OutlineList(s)
        self.assertEquals(o.default_styles(), '<?xml version="1.0" encoding="UTF-8"?>\n<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:smil="urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0" xmlns:anim="urn:oasis:names:tc:opendocument:xmlns:animation:1.0" xmlns:field="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:field:1.0" office:version="1.1">\n  <text:list-style style:name="L2">\n      <text:list-level-style-bullet text:level="1" text:bullet-char="\xe2\x97\x8f">\n\t<style:list-level-properties text:space-before="0.3cm" text:min-label-width="0.9cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="45%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="2" text:bullet-char="\xe2\x80\x93">\n\t<style:list-level-properties text:space-before="1.6cm" text:min-label-width="0.8cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="75%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="3" text:bullet-char="\xe2\x97\x8f">\n\t<style:list-level-properties text:space-before="3cm" text:min-label-width="0.6cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="45%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="4" text:bullet-char="\xe2\x80\x93">\n\t<style:list-level-properties text:space-before="4.2cm" text:min-label-width="0.6cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="75%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="5" text:bullet-char="\xe2\x97\x8f">\n\t<style:list-level-properties text:space-before="5.4cm" text:min-label-width="0.6cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="45%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="6" text:bullet-char="\xe2\x97\x8f">\n\t<style:list-level-properties text:space-before="6.6cm" text:min-label-width="0.6cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="45%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="7" text:bullet-char="\xe2\x97\x8f">\n\t<style:list-level-properties text:space-before="7.8cm" text:min-label-width="0.6cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="45%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="8" text:bullet-char="\xe2\x97\x8f">\n\t<style:list-level-properties text:space-before="9cm" text:min-label-width="0.6cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="45%"/>\n      </text:list-level-style-bullet>\n      <text:list-level-style-bullet text:level="9" text:bullet-char="\xe2\x97\x8f">\n\t<style:list-level-properties text:space-before="10.2cm" text:min-label-width="0.6cm"/>\n\t<style:text-properties fo:font-family="StarSymbol" style:use-window-font-color="true" fo:font-size="45%"/>\n      </text:list-level-style-bullet>\n    </text:list-style>\n  </office:document-content>')
        # tree = et.fromstring(o.default_styles())
        # xml = preso.to_xml(tree)
        # self.assertEquals(xml, '')

    def test_mixed_content(self):
        p = preso.Preso()
        s = p.add_slide()
        m = preso.MixedContent(s, 'p')
        m.write('This text is ')
        m.add_node('b')
        m.write('bold')
        m.pop_node()
        m.write('This is not')
        xml = preso.to_xml(m.get_node())
        self.assertEquals(xml, '<p><text:p text:style-name="P1">This text is <b>bold</b>This is not</text:p></p>')

    def test_code(self):
        p = preso.Preso()
        s = p.add_slide()
        s.add_code("print 'hello world'", 'python')
        self.assertEquals(s.to_xml(), '<draw:page draw:master-page-name="Default" draw:name="page1" draw:style-name="dp1" presentation:presentation-page-layout-name="AL1T0"><office:forms form:apply-design-mode="false" form:automatic-focus="false" /><draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P1"><text:span text:style-name="T0">print</text:span><text:span text:style-name="T1"> </text:span><text:span text:style-name="T2">\'hello world\'</text:span><text:line-break /></text:p></draw:text-box></draw:frame></draw:page>')

    def test_new_outline(self):
        p = preso.Preso()
        s = p.add_slide()
        o = preso.OutlineList(s)
        o.new_item('foo')
        o.new_item('bar')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L2"><text:list-item><text:p text:style-name="P3">foo</text:p></text:list-item><text:list-item><text:p text:style-name="P3">bar</text:p></text:list-item></text:list>')
        
        o.indent()
        o.new_item('barbie')
        self.assertEquals(o.to_xml(), '<text:list text:style-name="L2"><text:list-item><text:p text:style-name="P3">foo</text:p></text:list-item><text:list-item><text:p text:style-name="P3">bar</text:p></text:list-item><text:list-item><text:list><text:list-item><text:p text:style-name="P3">barbie</text:p></text:list-item></text:list></text:list-item></text:list>')

    def test_import(self):
        p = preso.Preso()
        p.import_slide('test/oooOutput/MICH Job Talk - Curiosity.odp', 3)
        p.to_file('/tmp/foo.odp')


    def test_code_ugly_indent(self):
        """
        test something like this:
        <paragraph>No:</paragraph><doctest_block xml:space="preserve">>>> def process_input(iterable):
...   results = []
...   for x in iterable:
...     results.append(process_x(x))
...   return results</doctest_block><paragraph>Yes:</paragraph><doctest_block xml:space="preserve">>>> def process_input(iterable):
...   for x in iterable:
...     yield process_x(x)</doctest_block>
        """
        p = preso.Preso()
        s = p.add_slide()
        s.write('foo:')

        s.add_node('text:line-break', {}) # depart_paragraph depart line
        s.pop_node()

        s.insert_line_break = True

        s.add_code("""print 'hello world'
print 'more stuff'""", 'python')
        pretty = preso.pretty_xml(s.to_xml(), add_ns=True)
        print pretty
        #self.assertEquals(pretty, '')
        self.assertEquals(s.to_xml(), '<draw:page draw:master-page-name="Default" draw:name="page1" draw:style-name="dp1" presentation:presentation-page-layout-name="AL1T0"><office:forms form:apply-design-mode="false" form:automatic-focus="false" /><draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P1">foo:<text:line-break /><text:line-break /><text:span text:style-name="T0">print</text:span><text:span text:style-name="T1"> </text:span><text:span text:style-name="T2">\'hello world\'</text:span><text:line-break /><text:span text:style-name="T0">print</text:span><text:span text:style-name="T1"> </text:span><text:span text:style-name="T2">\'more stuff\'</text:span><text:line-break /></text:p></draw:text-box></draw:frame></draw:page>')



    def test_same_paragraph(self):
        p = preso.Preso()
        s = p.add_slide()
        m = preso.MixedContent(s, 'p')
        m.write('This text is ')
        m.write('more text')
        xml = preso.to_xml(m.get_node())
        print 'same', preso.pretty_xml(m.to_xml(), add_ns=True)
        self.assertEquals(xml, '<p><text:p text:style-name="P1">This text is more text</text:p></p>')


if __name__ == "__main__":
    unittest.main()

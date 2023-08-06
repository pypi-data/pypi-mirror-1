"""
Whitespace

>>> from odplib import preso
>>> p = preso.Preso()
>>> s = p.add_slide()
>>> s.write('foo')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0">foo</text:p></draw:text-box></draw:frame>'

>>> s.write('bar ')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0">foobar </text:p></draw:text-box></draw:frame>'

Test newline
>>> s.add_node('text:line-break')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0">foobar <text:line-break /></text:p></draw:text-box></draw:frame>'

Test 2 spaces (after first space should be <text:s>
>>> s.write('  biz  ')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0">foobar <text:line-break> <text:s />biz <text:s /></text:line-break></text:p></draw:text-box></draw:frame>'

Test only spaces
>>> s = p.add_slide()
>>> s.write('   ')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0"> <text:s text:c="2" /></text:p></draw:text-box></draw:frame>'

add more spaces
>>> s.write('   ')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0"> <text:s text:c="2" /> <text:s text:c="2" /></text:p></draw:text-box></draw:frame>'



Test switching styles
>>> s = p.add_slide()
>>> s.write('foo')
>>> s.push_style(preso.ParagraphStyle(**{'fo:text-align':'end'}))
>>> s.write('bar')
>>> s.pop_node()

push same style again, should append rather than create new node
>>> s.push_style(preso.ParagraphStyle(**{'fo:text-align':'end'}))
>>> s.write('biz')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0">foo</text:p><text:p text:style-name="P1">barbiz</text:p></draw:text-box></draw:frame>'



Test sentence
>>> s = p.add_slide()
>>> s.write('The quick brown fox.  Went to the store')
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0">The quick brown fox. <text:s />Went to the store</text:p></draw:text-box></draw:frame>'


Test simple code
>>> s = p.add_slide()
>>> code = '''>>> print 1'''
>>> s.add_code(code, 'pycon')
>>> #print preso.pretty_xml(s.text_frames[0].to_xml(), True)
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0"><text:span text:style-name="T0">&gt;&gt;&gt; </text:span><text:span text:style-name="T1">print</text:span><text:span text:style-name="T2"> </text:span><text:span text:style-name="T3">1</text:span><text:line-break /></text:p></draw:text-box></draw:frame>'

Test indent code bug
>>> s = p.add_slide()
>>> code = '''>>> if foo:
... ...   print "bar"'''
>>> s.add_code(code, 'pycon')
>>> #print preso.pretty_xml(s.text_frames[0].to_xml(), True)
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0"><text:span text:style-name="T0">&gt;&gt;&gt; </text:span><text:span text:style-name="T1">if</text:span><text:span text:style-name="T2"> foo:</text:span><text:line-break /><text:span text:style-name="T0">... </text:span><text:span text:style-name="T2"> <text:s /></text:span><text:span text:style-name="T1">print</text:span><text:span text:style-name="T2"> </text:span><text:span text:style-name="T4">"bar"</text:span><text:line-break /></text:p></draw:text-box></draw:frame>'




Test line insert
>>> s = p.add_slide()
>>> s.write('foobar')
>>> s.insert_line_break = True
>>> code = '''>>> print 1'''
>>> s.add_code(code, 'pycon')
>>> #print preso.pretty_xml(s.text_frames[0].to_xml(), True)
>>> s.text_frames[0].to_xml()
'<draw:frame draw:layer="layout" presentation:class="subtitle" presentation:style-name="pr2" svg:height="13.86cm" svg:width="25.199cm" svg:x="1.4cm" svg:y="4.577cm"><draw:text-box><text:p text:style-name="P0">foobar<text:line-break /><text:span text:style-name="T0">&gt;&gt;&gt; </text:span><text:span text:style-name="T1">print</text:span><text:span text:style-name="T2"> </text:span><text:span text:style-name="T3">1</text:span><text:line-break /></text:p></draw:text-box></draw:frame>'



"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

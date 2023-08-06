Convert creole wiki text into html.

    >>> wiki_text = "//italics//"
    >>> self.performTransform(wiki_text)
    '<p><em>italics</em></p>\n'

Let's test all the wiki syntax.

    >>> wiki_text = "**bold**"
    >>> self.performTransform(wiki_text)
    '<p><strong>bold</strong></p>\n'

    >>> wiki_text = "^^super^^script"
    >>> self.performTransform(wiki_text)
    '<p><sup>super</sup>script</p>\n'
 
    >>> wiki_text = ",,sub,,script"
    >>> self.performTransform(wiki_text)
    '<p><sub>sub</sub>script</p>\n'

    >>> wiki_text = "##monospace##"
    >>> self.performTransform(wiki_text)
    '<p><tt>monospace</tt></p>\n'

    >>> wiki_text = """
    ... * Bullet list
    ... * Second item
    ... ** Sub item"""
    >>> self.performTransform(wiki_text)
    '<ul><li>Bullet list</li>\n<li>Second item\n<ul><li>Sub item</li></ul></li></ul>\n'
    
    >>> wiki_text = """
    ... # Numbered list
    ... # Second item
    ... ## Sub item"""
    >>> self.performTransform(wiki_text)
    '<ol><li>Numbered list</li>\n<li>Second item\n<ol><li>Sub item</li></ol></li></ol>\n'

    >>> wiki_text = """
    ... # Mixed list
    ... ** Sub bullet item
    ... # Numbered item"""
    >>> self.performTransform(wiki_text)
    '<ol><li>Mixed list\n<ul><li>Sub bullet item</li></ul></li>\n<li>Numbered item</li></ol>\n'

    >>> wiki_text = """
    ... ; Definition List
    ... : Definition"""
    >>> self.performTransform(wiki_text)
    '<dl><dt>Definition List</dt>\n<dd>Definition</dd>\n</dl>\n'

    >>> wiki_text = "Link to [[WikiPage]]"
    >>> self.performTransform(wiki_text)
    '<p>Link to <a href="WikiPage">WikiPage</a></p>\n'

    >>> wiki_text = "[[http://google.com|Google]]"
    >>> self.performTransform(wiki_text)
    '<p><a href="http://google.com">Google</a></p>\n'

    >>> wiki_text = """
    ... == Large heading
    ... === Medium Heading
    ... ==== Small heading"""
    >>> self.performTransform(wiki_text)
    '<h2>Large heading</h2>\n<h3>Medium Heading</h3>\n<h4>Small heading</h4>\n'

    >>> wiki_text = "----"
    >>> self.performTransform(wiki_text)
    '<hr />\n'
    
    >>> wiki_text = "{{logo.jpg|title}}"
    >>> self.performTransform(wiki_text)
    '<p><img src="logo.jpg" alt="title" /></p>\n'

    >>> wiki_text = """
    ... |=|=table|=header|
    ... |a|table|row|
    ... |b|table|row|"""
    >>> self.performTransform(wiki_text)
    '<table><tr><th></th><th>table</th><th>header</th></tr>\n<tr><td>a</td><td>table</td><td>row</td></tr>\n<tr><td>b</td><td>table</td><td>row</td></tr>\n</table>\n'

    >>> wiki_text = """
    ... {{{
    ... == [[Nowiki]]:
    ... //**don't format//
    ... }}}"""
    >>> self.performTransform(wiki_text)
    "<pre>== [[Nowiki]]:\n//**don't format//\n</pre>\n"


    >>> wiki_text = "use a tilde '~~' to ~**escape"
    >>> self.performTransform(wiki_text)
    "<p>use a tilde '~' to **escape</p>\n"

Let's throw in some non-ascii characters.

    >>> wiki_text = """== En Français
    ... ça va? ouais. l'hôtel California, Dieu **créa** le ciel et la terre"""
    >>> self.performTransform(wiki_text)
    "<h2>En Fran\xc3\xa7ais</h2>\n<p>\xc3\xa7a va? ouais. l'h\xc3\xb4tel California, Dieu <strong>cr\xc3\xa9a</strong> le ciel et la terre</p>\n"

    >>> wiki_text = u"ça va?"
    >>> self.performTransform(wiki_text)
    '<p>\xc3\x83\xc2\xa7a va?</p>\n'

    >>> wiki_text = """בְּרֵאש"""
    >>> self.performTransform(wiki_text)
    '<p>\xd7\x91\xd6\xb0\xd6\xbc\xd7\xa8\xd6\xb5\xd7\x90\xd7\xa9</p>\n'

    
Inter wiki link can be set up as well.

    >>> self.portal.portal_transforms.creole_to_html.set_parameters(interwiki=["wikipedia|http://en.wikipedia.org/wiki/", "trac|http://trac.edgewall.org/wiki/"])
    >>> dummy = self.portal.portal_transforms.reloadTransforms()
    >>> interwiki_text = "Link to [[wikipedia:Plone_(software)|Plone on wikipedia]]"
    >>> self.performTransform(interwiki_text)
    '<p>Link to <a href="http://en.wikipedia.org/wiki/Plone_(software)">Plone on wikipedia</a></p>\n'
    >>> interwiki_text = "Link to [[trac:TitleIndex|List of trac wiki pages]]"
    >>> self.performTransform(interwiki_text)
    '<p>Link to <a href="http://trac.edgewall.org/wiki/TitleIndex">List of trac wiki pages</a></p>\n'

Set a base for wiki links

    >>> self.portal.portal_transforms.creole_to_html.set_parameters(base_url="http://example.com/")
    >>> dummy = self.portal.portal_transforms.reloadTransforms()
    >>> wiki_text = "Link to [[foo-bar-baz|Some Page]]"
    >>> self.performTransform(wiki_text)
    '<p>Link to <a href="http://example.com/foo-bar-baz">Some Page</a></p>\n'

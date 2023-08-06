==================
Txt2tags transform
==================

Introduction
============
Convert txt2tags text into html.

    >>> txt2tags_text = "hello ``world``"
    >>> self.performTransform(txt2tags_text)
    u'<p>\nhello <code>world</code>\n</p>'

Diferences from txt2tags:

  - The first three lines of file, expected to be for header must be blank.
    Plone manages this data :-)
  - The target must be html or xhtml


Review
======
A quick review to txt2tags syntax:

    >>> text = """
    ... = Title level 1 =
    ... 
    ... == Title level 2 ==
    ... 
    ... === Title level 3 ===
    ... """
    >>> self.performTransform(text)
    u'<h1>Title level 1</h1>\n<h2>Title level 2</h2>\n<h3>Title level 3</h3>'

    >>> text = """
    ... + Numbered Title level 1 +
    ... 
    ... ++ Numbered Title level 2 ++
    ... 
    ... +++ Numbered Title level 3 +++
    ... """
    >>> self.performTransform(text)
    u'<h1>1. Numbered Title level 1</h1>\n<h2>1.1. Numbered Title level 2</h2>\n<h3>1.1.1. Numbered Title level 3</h3>'

    >>> text = """
    ... A paragraph is made by one or
    ... more lines.
    ... 
    ... A blank line separates them.
    ... """
    >>> self.performTransform(text)
    u'<p>\nA paragraph is made by one or\nmore lines.\n</p>\n<p>\nA blank line separates them.\n</p>'

    >>> text = """
    ... % start a line with
    ... a percent sign,
    ... % and it will be ignored
    ... useful for TODOs!
    ... """
    >>> self.performTransform(text)
    u'<p>\na percent sign,\nuseful for TODOs!\n</p>'

    >>> text = """
    ... For beautifiers we have **bold**
    ... and //italic//.
    ... 
    ... There is also __underline__ and
    ... ``monospaced``.
    ... """
    >>> self.performTransform(text)
    u'<p>\nFor beautifiers we have <b>bold</b>\nand <i>italic</i>.\n</p>\n<p>\nThere is also <u>underline</u> and\n<code>monospaced</code>.\n</p>'

    >>> text = """
    ... - This is a list of items
    ... - Just use hyphens
    ...   - More indent opens a sublist
    ... 
    ... 
    ... Two blank lines closes the lists.
    ... """
    >>> self.performTransform(text)
    u'<ul>\n<li>This is a list of items\n</li>\n<li>Just use hyphens\n  <ul>\n  <li>More indent opens a sublist\n  </li>\n  </ul>\n</li>\n</ul>\n\n<p>\nTwo blank lines closes the lists.\n</p>'

    >>> text= """
    ... + Change the hyphen by a plus
    ... + And you have a numbered list
    ...   + Same rules apply
    ...   +
    ... +
    ... An empty item closes the current list.
    ... """
    >>> self.performTransform(text)
    u'<ol>\n<li>Change the hyphen by a plus\n</li>\n<li>And you have a numbered list\n  <ol>\n  <li>Same rules apply\n  </li>\n  </ol>\n</li>\n</ol>\n\n<p>\nAn empty item closes the current list.\n</p>'

    >>> text = """
    ... : Definition list
    ...   A list with terms
    ... : Start term with colon
    ...   And its definition follows
    ... :
    ... """
    >>> self.performTransform(text)
    u'<dl>\n<dt>Definition list</dt><dd>\n  A list with terms\n</dd>\n<dt>Start term with colon</dt><dd>\n  And its definition follows\n</dd>\n</dl>\n\n<p></p>'

    >>> text = """
    ... \tA quoted paragraph is prefixed
    ... \tby a TAB.
    ...	\t\tMore TABs, more deep.
    ... No TAB or blank line, closes quote.
    ... """
    >>> self.performTransform(text)
    u'\t<blockquote>\n\tA quoted paragraph is prefixed\n\tby a TAB.\n\t\t<blockquote>\n\t\tMore TABs, more deep.\n\t\t</blockquote>\n\t</blockquote>\n<p>\nNo TAB or blank line, closes quote.\n</p>'

    >>> text = """
    ... ```
    ...   A verbatim area is enclosed
    ...       inside three backquotes.
    ... **Marks** are not interpreted
    ...      and spacing is preserved.
    ... ```
    ... """
    >>> self.performTransform(text)
    u'<pre>\n    A verbatim area is enclosed\n        inside three backquotes.\n  **Marks** are not interpreted\n       and spacing is preserved.\n</pre>\n<p></p>'

    >>> text = """
    ... Verbatim line is nice for commands:
    ... ``` $ cat /etc/passwd | tr : ,
    ... Just prefix it with 3 backquotes.
    ... """
    >>> self.performTransform(text)
    u'<p>\nVerbatim line is nice for commands:\n</p>\n<pre>\n  $ cat /etc/passwd | tr : ,\n</pre>\n<p>\nJust prefix it with 3 backquotes.\n</p>'

    >>> text = """
    ... \"\"\"
    ...        A raw area is enclosed
    ...     inside three doublequotes.
    ... 
    ... **Marks** are not interpreted
    ...  and spacing is not preserved.
    ... \"\"\"
    ... """
    >>> self.performTransform(text)
    u'       A raw area is enclosed\n    inside three doublequotes.\n\n**Marks** are not interpreted\n and spacing is not preserved.\n<p></p>'

    >>> text = '""" There is a **raw** line also.'
    >>> self.performTransform(text)
    u'There is a **raw** line also.'

    >>> text = """
    ... || Table Heading | Table Heading |
    ... |          Table |     align     |
    ... |          lines |      is       |
    ... |      with cell |     nice!     |
    ... """
    >>> self.performTransform(text)
    u'<table border="1" cellpadding="4">\n<tr>\n<th>Table Heading</th>\n<th>Table Heading</th>\n</tr>\n<tr>\n<td align="right">Table</td>\n<td align="center">align</td>\n</tr>\n<tr>\n<td align="right">lines</td>\n<td align="center">is</td>\n</tr>\n<tr>\n<td align="right">with cell</td>\n<td align="center">nice!</td>\n</tr>\n</table>\n'

    >>> text = """
    ... [t2t.png] Left aligned image
    ... 
    ... Center [t2t.png] aligned
    ... 
    ... Right aligned [t2t.png]
    ... """
    >>> self.performTransform(text)
    u'<p>\n<img align="left" src="t2t.png" border="0" alt=""/> Left aligned image\n</p>\n<p>\nCenter <img align="middle" src="t2t.png" border="0" alt=""/> aligned\n</p>\n<p>\nRight aligned <img align="right" src="t2t.png" border="0" alt=""/>\n</p>'

    >>> text = """
    ... A link is recognized@automaticaly.see?
    ... 
    ... A [named link www.myurl.com] is easy.
    ... 
    ... An image [[t2t.png] as-a-link.html].
    ... """
    >>> self.performTransform(text)
    u'<p>\nA link is <a href="mailto:recognized@automaticaly.see">recognized@automaticaly.see</a>?\n</p>\n<p>\nA <a href="http://www.myurl.com">named link</a> is easy.\n</p>\n<p>\nAn image <a href="as-a-link.html"><img align="middle" src="t2t.png" border="0" alt=""/></a>.\n</p>'

    >>> text = """
    ... A separator line:
    ... --------------------
    ... And a stronger one:
    ... ====================
    ... (At least 20 chars)
    ... """
    >>> self.performTransform(text)
    u'<p>\nA separator line:\n</p>\n<hr class="light" />\n<p>\nAnd a stronger one:\n</p>\n<hr class="heavy" />\n<p>\n(At least 20 chars)\n</p>'


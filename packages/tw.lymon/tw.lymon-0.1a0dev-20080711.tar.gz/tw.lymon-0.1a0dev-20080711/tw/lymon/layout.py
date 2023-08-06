from lymon.core import Document
from lymon.tw import Site
from tw.api import CSSLink

__all__ = ['LymonSite', 'template']

# Document template example for Lymon Project

# Link to the template CSS
style_template = CSSLink(modname=__name__, filename='static/css/layout/style.css')

# Document Definition
template = Document()
template.div(slot='content', id=False, attrs={'class': 'content'})
template.div(slot='content.top', id=False, attrs={'class': 'header'})
template.div(slot='content.top.info', id=False, attrs={'class': 'top_info'})
template.div(slot='content.top.info.right', id=False, attrs={'class': 'top_info_right'})

# You can look at the rendered page to see which slot correspond to each part of the page

# Header and Login
html_text = """<p><b>Login slot at:</b> content.top.info.right<br/>
<b>CSS Class:</b> top_info_right</p>"""

template.div(slot='content.top.info.right.text', id=False, attrs={'class': 'top_info_right'}, html=html_text)

html_text = """<p><b>Header in:</b> content.top.info.left.text<br /><b>CSS Class:</b> top_info_left</p>"""

template.div(slot='content.top.info.left.text', id=False, attrs={'class': 'top_info_left'}, html=html_text)

# Site Title, and reference
template.div(slot='content.top.logo', id=False, attrs={'class': 'logo'})
template.h1(slot='content.top.logo.title', id=False)

html_text = """<span class="dark">Ly</span>mon Project"""
template.a(slot='content.top.logo.title.link', id=False, attrs={'href': 'http://code.google.com/p/lymon/'}, html=html_text)

# Menu Items at content.bar
html_text = """
<ul>
	<li class="active">Menu item 1</li>
	<li><a href="#" accesskey="m">Menu item 2</a></li>

</ul>
"""

template.div(slot='content.bar', id=False, attrs={'class': 'bar'}, html=html_text)

# Search bar and From
html_text = """
			<form method="post" action="?">
				<div class="search_form">
				<p>Search: <input type="text" name="search" class="search" /> <input type="submit" value="Search" class="submit" /> <a class="grey" href="#">Advanced</a></p>
				</div>

			</form>
			<p>Search at: content.search<br/>CSS Class: search_field</p>
"""

template.div(slot='content.search', id=False, attrs={'class': 'search_field'}, html=html_text)

# Left side of the page (content.left)
template.div(slot='content.left', id=False, attrs={'class': 'left'})

# Two sides menu

#html_text = """Box at: content.left.title (h3)"""
#template.h3(slot='content.left.title', id=False, html=html_text)
#html_text = """<h2>Title at: content.left.left_side</h2><p>CSS Class: left_side</p>"""
#template.div(slot='content.left.left_side', id=False, attrs={'class': 'left_side'}, html=html_text)
#html_text = """<h2>Title at: content.left.right_side</h2><p>CSS Class: right_side</p>"""
#template.div(slot='content.left.right_side', id=False, attrs={'class': 'right_side'}, html=html_text)


html_text ="""Box at: content.left.box (h3)"""

#template.h3(slot='content.left.box', html=html_text)

#html_text = """<p>Class: left_box</p>"""

#template.div(slot='content.left.box', id=False, attrs={'class': 'left_box'}, html=html_text)

# Right side of the page (content.right)
template.div(slot='content.right', id=False, attrs={'class': 'right'})

html_text = """Right menu at: content.right (h3)"""
template.h3(slot='content.right.title', id=False, html=html_text)

#html_text = """<p>Class: right_articles</p>"""


html_text = """<p>Cuadro de mensajes y alertas, en construccion por el momento</p>"""



template.div(slot='content.right.right_articles_1', id=False, attrs={'class': 'right_articles'}, html=html_text)

html_text = """
<p> &copy; Copyright 2008 Laureano Arcanio<br />
Powered by <a href="http://code.google.com/p/lymon/">Lymon</a></p>
"""

template.div(slot='content.footer', id=False, attrs={'class': 'footer'}, html=html_text)

class LymonSite(Site):
	css = [style_template]


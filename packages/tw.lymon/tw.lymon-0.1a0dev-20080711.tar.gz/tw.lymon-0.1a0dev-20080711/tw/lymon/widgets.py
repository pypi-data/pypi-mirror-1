#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

# Thanks to the ToscaWidgets project for all they hard work and help !
 

from tw.api import Widget, JSLink, CSSLink


__all__ = [	"ColorTab", 
			"ArrowListMenu", 
			'Container', 
			'CSSContainer', 
			'StyledMenus', 
			'PageIndex', 
			'PopUp',
			'ListMenu'
		]




cssPopUp = CSSLink(modname=__name__, filename='static/css/popup/popup_link.css')


cssColorTab = CSSLink(modname=__name__, filename='static/css/colortab.css')
cssArrowMenu = CSSLink(modname=__name__, filename='static/css/arrowmenu.css')
cssContainer = CSSLink(modname=__name__, filename='static/css/container.css')

cssStyledMenu = CSSLink(modname=__name__, filename='static/css/styled_menu.css')

# StyledTable # Featured !
cssStyledTable = CSSLink(modname=__name__, filename='static/css/styled_table.css')

# Page Index CSS
cssPageIdex = CSSLink(modname=__name__, filename='static/css/page_index.css')





# A Tab style navigation Bar
class ListMenu(Widget):
	params=["items", 'current']
	# element = [('Title', 'Link')]
	current=0
	items=[('Item 1','#')]
	engine_name = "genshi"
	template = '''
	<div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip=''> 
    	<ul>
    		<?python
				is_current = lambda item: items.index(item) == current 
			?>
			<div py:for='item in items' py:strip=''>
				
				<li py:if='not is_current(item)'>
					<a py:attrs="{'href': item[1]}" py:content='item[0]'>  </a>
				</li>
				<li py:if='is_current(item)' py:attrs="{'href': item[1], 'class': 'active'}" py:content='item[0]'>

				</li>
				
			</div>
			

    	</ul>
    </div>
    '''
	# DD Color Tab II from: http://www.dynamicdrive.com/

#<div py:choose='' py:strip=''>
#<a py:if='item == 1 and (current -1) >0' href='${link % (current-1)}' class='page_index_next'> <span>&lt;&lt;</span></a>
#<a py:when='item == 0' class='page_index_dot'> <span>.......</span></a>
#<a py:when='item == current' class='page_index_selected'> <span>$item</span></a>
#<a py:otherwise='' href='${link % item}' class='page_index_item'> <span>$item</span> </a>
#<a py:if='item == pages and (current +1) &lt;pages' href='${link % (current+1)}' class='page_index_next'> <span>&gt;&gt;</span></a>
#</div>



# A Tab style navigation Bar
class ColorTab(Widget):
	css = [cssColorTab]
	params=["elements","id"]
	# element = [('Title', 'Link')]
	elements=[('Item 1','#')]
	id="bar"
	engine_name = "genshi"
	template = '''
    <div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip=''>
	<div id="invertedtabsline">&nbsp;</div>
	<div id="invertedtabs">
		<ul>
			<li py:for="element in elements" style="margin-left: 1px">
				<a py:attrs="{'href':element[1]}"> <span py:content="element[0]">Title</span></a>
			</li>
		</ul>
	</div>
	<br style="clear: left" />
    </div>
    '''
	# DD Color Tab II from: http://www.dynamicdrive.com/

# Arrow Menu
class StyledMenus(Widget):
	css = [cssStyledMenu]
	params=["elements","id", 'title']
	# element = [('Title', 'Link')]
	elements=[('Item 1','#')]
#	id="menu1"
	title = 'New Menu:'
	engine_name = "genshi"
	template = '''
    <div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip=''>
	<div py:attrs="{'id':id}">
		<ul>
			<li><a id="current">$title</a></li>
			<li py:for="element in elements">
				<a py:attrs="{'href':element[1]}"> <span py:content="element[0]">Title</span></a>
			</li>
		</ul>
	</div>
	</div>
    '''
    
#Arrow Bullet List Menu from: http://www.dynamicdrive.com/
class ArrowListMenu(Widget):
	css = [cssArrowMenu]
	params=["elements","id","title"]
	# element = [('Title', 'Link')]
	elements=[('Item 1','#')]
	id="menu"
	title="Menu:"
	engine_name = "genshi"
	template = '''
    <div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip=''>
	<div class="arrowlistmenu">
		<h3 class="headerbar">$title</h3>
		<ul>
			<li py:for="element in elements">
				<a py:attrs="{'href':element[1]}"> <span py:content="element[0]">Title</span></a>
			</li>
		</ul>
	</div>
	</div>
    '''
	#Arrow Bullet List Menu from: http://www.dynamicdrive.com/
	
	
# A CSS Container with HTML and CSS included
class Container(Widget):
	css = [cssContainer]
	params=["title", 'html']
	title = 'CSS Container'
	html = 'Contained HTML'
	engine_name = "genshi"
	template = """
	<div class="container">
		<div class="container_head">
			<img src="images/sidebar_left.jpg" alt="" class="float_left"/>
			<img src="images/sidebar_right.jpg" alt="" class="float_right"/>
			<div class="container_head_text">
				$title
			</div>
		</div>
		<div class="container_content">
			$html  
		</div>
	</div>
	"""
	# Container from http://infectthesystem.com/ ( Colors modified )


# A CSS Container only you need to have:
# div					|	class
#----------------------------------------------
# container				-> Parent div
# container_head		-> Title container div
# container_head_text	-> Title div
# container_content		-> Content div

class CSSContainer(Widget):
	css = [cssContainer]
	# Container from http://infectthesystem.com/ ( Colors modified )

# Featured, not yet Working
# From http://veerle.duoh.com/index.php/blog/comments/a_css_styled_table/
#class StyledTable(TableForm):
#	css = [cssStyledTable]


# Page index widgets, 1 2 3 ... 9
class PageIndex(Widget):
	params = ['current', 'pages', 'start', 'link', 'page_index']
	current = 1
	start = 1
	pages = 20
	link = '/index?page=%s'
	engine_name = 'genshi'
	css = [cssPageIdex]
	def update_params(self, d):
		pages = self.pages
		d['current'] = int(self.current)
#		if pages <= 8:	
		page_index = [(page+1) for page in range(pages)]
#		if pages > 8 and pages <=15:
#			page_index = [1,2,3,4,5,6,7,0,pages]	
#		if pages > 15:
#			page_index = [1,2,3,4,5,6,7,8,9,10,0,pages]	
		d['page_index'] = page_index
		super(PageIndex, self).update_params(d)
		
	template = """
	<div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/">
		<ul class='page_index'>
			<li py:for="item in page_index">
				<div py:choose='' py:strip=''>
					<a py:if='item == 1 and (current -1) >0' href='${link % (current-1)}' class='page_index_next'> <span>&lt;&lt;</span></a>
					<a py:when='item == 0' class='page_index_dot'> <span>.......</span></a>
					<a py:when='item == current' class='page_index_selected'> <span>$item</span></a>
					<a py:otherwise='' href='${link % item}' class='page_index_item'> <span>$item</span> </a>
					<a py:if='item == pages and (current +1) &lt;pages' href='${link % (current+1)}' class='page_index_next'> <span>&gt;&gt;</span></a>
				</div>
			</li>
		</ul>
	<br />
	</div>
	
	"""

# A pop up window Link. 
class PopUp(Widget):
	css = [cssPopUp]
	params = ['link', 'attrs', 'string', 'title', 'href']
	engine_name = 'genshi'
	link = '/'
	href= None
	title = 'Vista sin Marcos'
	attrs = {}
	defaults = {	'scrollbars': 0, 
					'status': 'no', 
					'titlebar': 'no', 
					'toolbar': 'no', 
					'resizable': 'yes', 
					'menubar': 'no', 
					'location': 'no', 
					'width': 300, 
					'height':200 
				 }
				 
	template = """
	<div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" class='popup_link'>
	<a py:attrs="{'href': href, 'class': 'cursor'}" onclick="window.open('$link','window', '$string')" > $title </a>
	</div>
	"""
	
	def update_params(self, d):
		d['link'] = self.link
		d['href'] = self.href
		string = ''
		self.defaults.update(self.attrs)
		for attr, value in self.defaults.items():
			string += "%s=%s, " % (attr, value)
		d['string'] = string
		super(PopUp, self).update_params(d)
		
		
		
		
	

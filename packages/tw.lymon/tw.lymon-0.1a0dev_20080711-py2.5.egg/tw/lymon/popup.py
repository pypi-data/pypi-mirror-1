from tw.lymon import LymonSite, template
from lymon.core import Document
from tw.api import CSSLink

style_popup = CSSLink(modname=__name__, filename='static/css/popup/popup.css')


__all__ = ['popup', 'PopupSite']

popup = Document()

popup.div(slot='content', id=False, attrs={'class': 'content'})
popup.div(slot='content.header', id=False, attrs={'class': 'header'})
popup.h3(slot='content.header.title', id=False, attrs={'class': 'header_title'})
popup.div(slot='content.container', id=False, attrs={'class': 'container'})
popup.div(slot='content.footer', id=False, attrs={'class': 'footer'})

class PopupSite(LymonSite):
	css = [style_popup]

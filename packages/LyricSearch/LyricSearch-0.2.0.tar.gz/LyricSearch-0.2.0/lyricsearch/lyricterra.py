# -*- coding: utf-8 -*-

import urllib2
import urllib
import sys

from BeautifulSoup import BeautifulSoup

letras = {'á':'aacute','â':'acirc','ã':'atilde','é':'eacute',
        'ê':'ecirc','í':'iacute','ó':'oacute','ô':'ocirc','õ':'otilde',
        'ú':'uacute','ç':'ccedil'}

class LyricsTerra:
    
    def __init__(self):
        self.url = "http://letras.mus.br"
        self.description = "Letras.mus.br"        
    
    def find(self,title, artist):
        self.title = title.lower().strip()
        self.artist = artist.lower().strip()
        title_find = self.title.replace(' ','+')
        pagina = urllib2.urlopen("http://letras.terra.com.br/?q=%s&tipo=1&busca=busca" % title_find)
        texto = pagina.read()
        pagina.close()
        link = self._parse_search(texto)
        if link:
            return self._parse_page_lyrics(link)
        else:
            return ''
        
    def _parse_search(self, texto):
        soup = BeautifulSoup(texto)
        t = soup.findAll('ul',{'class' :'res'})
        soup_lista = BeautifulSoup( str(t))
        t1 = soup_lista.findAll('li')
        busca = self._replace_symbols(self.artist) + ' - ' + \
            self._replace_symbols(self.title)
        for linha in t1:
            nome = str(linha.a.contents[0]).lower().strip()
            if nome == busca:
                return linha.a['href']
        return ''
        
        
    def _replace_symbols(self,text):
        texto = text
        for i in text:
            if '\xc3'+i in letras.keys():
                texto = texto.replace('\xc3'+i,'&'+letras['\xc3'+i]+';')
        return texto
        
    def _parse_page_lyrics(self,link):
        page_artista = urllib2.urlopen(link)
        pagina = page_artista.read()
        page_artista.close()
        soup = BeautifulSoup(pagina)
        t = soup.findAll('div', {'class':'ltr'})
        soup_local = BeautifulSoup(str(t))
        t1 = soup_local.findAll('p')
        return t1[1]
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: lyricterra.py artista titulo'
        sys.exit()
    plugin = LyricsTerra()
    artista = sys.argv[1]
    titulo = sys.argv[2]
    texto = plugin.find(titulo, artista)
    print texto
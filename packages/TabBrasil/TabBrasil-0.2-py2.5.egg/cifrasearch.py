# -*- coding: utf-8 -*-

import urllib2
import urllib
import sys

from BeautifulSoup import BeautifulSoup

letras = {'á':'aacute','â':'acirc','ã':'atilde','é':'eacute',
        'ê':'ecirc','í':'iacute','ó':'oacute','ô':'ocirc','õ':'otilde',
        'ú':'uacute','ç':'ccedil'}

class ClubCifra:
    
    def __init__(self):
        self.url = "http://cifraclub.terra.com.br"
        self.description = "CIFRACLUB - Seu site de cifras e tablaturas"        
    
    def find(self,title, artist):
        self.title = title.lower().strip()
        self.artist = artist.lower().strip()
        title_find = self.title.replace(' ','+')
        pagina = urllib2.urlopen("http://cifraclub.terra.com.br/cifra_lista.php?texto=%s&onde=1" % title_find)
        texto = pagina.read()
        pagina.close()
        link = self._parse_search(texto)
        if link:
            return self._parse_page_lyrics(link)
        else:
            return ''
        
    def _parse_search(self, texto):
        soup = BeautifulSoup(texto)
        t = soup.findAll('div',{'class' :'b b8'})
        soup_lista = BeautifulSoup( str(t))
        t1 = soup_lista.findAll('li')
        busca = self._replace_symbols(self.artist) + ' - ' + \
            self._replace_symbols(self.title)
        for linha in t1:
            conteudos = linha.a.b.contents
            nome = ''
            for c in conteudos:
                try:
                    nome = nome + c.renderContents()
                except AttributeError:
                    nome = nome + c
            nome = nome.lower().strip()
            print nome,' [] ', busca
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
        page_artista = urllib2.urlopen(self.url + link)
        pagina = page_artista.read()
        page_artista.close()
        soup = BeautifulSoup(pagina)
        t = soup.findAll('div', {'class':'b b8'})
        soup_local = BeautifulSoup(str(t))
        t1 = soup_local.findAll('pre')
        return t1[0]
    
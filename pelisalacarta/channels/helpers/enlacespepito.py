# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Helper para enlacespepito
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
#
from core import scrapertools
from core import config
from core import logger
import os, sys, re
import hashlib

SERIES_PEPITO    = 0
PELICULAS_PEPITO = 1

ENLACESPEPITO_REQUEST_HEADERS = [
    ["User-Agent" , "Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0"],
    ["Accept-Encoding","gzip, deflate"],
    ["Accept-Language" , "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"],
    ["Accept" , "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"],
    ["Connection" , "keep-alive"]
]


def get_cookie(html):
    import cookielib

    ficherocookies = os.path.join( config.get_setting("cookies.dir"), 'cookies.dat' )
    cj = cookielib.MozillaCookieJar()
    cj.load(ficherocookies,ignore_discard=True)

    cookie_pat = "cookie\('([a-zA-Z0-9]+)'\);"
    cookie_name = scrapertools.find_single_match(html, cookie_pat)

    cookie_value = ""

    for cookie in cj:
        if cookie.name == cookie_name:
            cookie_value = cookie.value
            break

    return cookie_value

# Busca el enlace correcto y lo procesa capturando los caracteres
# y posiciones del Javascript
#
def convert_link(html, link_type):
    hash_seed = get_cookie(html);

    hash = hashlib.sha256(hash_seed).hexdigest()
    if link_type == PELICULAS_PEPITO:
        hash += '0'

    HREF_SEARCH_PAT = '<a class=".' + hash + '" target="_blank" href="http://www.enlacespepito.com\/([^\.]*).html"><i class="icon-(?:play|download)">'

    href = list(scrapertools.find_single_match(html, HREF_SEARCH_PAT))

    CHAR_REPLACE_PAT = '[a-z]\[(\d+)\]="(.)";'

    matches = re.findall(CHAR_REPLACE_PAT , html, flags=re.DOTALL|re.IGNORECASE)
    for match in matches:
        href[int(match[0])] = match[1]

    href = ''.join(href)

    return 'http://www.enlacespepito.com/' + href + '.html'

def get_server_link(first_link, link_type):

    html = scrapertools.downloadpage(first_link, headers = ENLACESPEPITO_REQUEST_HEADERS)
    fixed_link = convert_link(html, link_type)

    # Sin el Referer da 404
    ENLACESPEPITO_REQUEST_HEADERS.append(['Referer', first_link])

    return scrapertools.get_header_from_response(fixed_link, header_to_get="location", headers = ENLACESPEPITO_REQUEST_HEADERS)

# Estas funciones son las únicas que deberían llamarse desde fuera
#
def get_server_link_series(first_link):
    return get_server_link(first_link, SERIES_PEPITO)

def get_server_link_peliculas(first_link):
    return get_server_link(first_link, PELICULAS_PEPITO)



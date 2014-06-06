# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para streaminto
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def test_video_exists( page_url ):
    logger.info("[streaminto.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    
    if "The file is being converted" in data:
        return False,"El fichero está en proceso"

    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[streaminto.py] url="+page_url)

    # Normaliza la URL
    try:
        if not page_url.startswith("http://streamin.to/embed-"):
            videoid = scrapertools.get_match(page_url,"streamin.to/([a-z0-9A-Z]+)")
            page_url = "http://streamin.to/embed-"+videoid+".html"
    except:
        import traceback
        logger.info(traceback.format_exc())
    
    # Lo pide una vez
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14']]
    data = scrapertools.cache_page( page_url , headers=headers )
    #logger.info("data="+data)
    
    #sources: [{file: "rtmp://95.211.95.238:1935/vod?h=t2i7k2olyhuzcg3h5e7cft5ly2ubyenv7dh6cfa2qgo5g6dl3dfuch4lvkka/flv:68/3185801774_n.flv?h=t2i7k2olyhuzcg3h5e7cft5ly2ubyenv7dh6cfa2qgo5g6dl3dfuch4lvkka"},{file: "http://95.211.95.238:8777/t2i7k2olyhuzcg3h5e7cft5ly2ubyenv7dh6cfa2qgo5g6dl3dfuch4lvkka/v.flv"}],
    patron = ',\{file\: "([^"]+)"'
    #patron_rtmp = '\[{file\: "([^"]+)"'
    #patron_flv = ',\{file\: "([^"]+)"'
    try:
        #media_url = scrapertools.get_match( data , 'file\: "([^"]+)"' )
        media_url = scrapertools.get_match( data , patron )
    except:
        op = scrapertools.get_match(data,'<input type="hidden" name="op" value="([^"]+)"')
        usr_login = ""
        id = scrapertools.get_match(data,'<input type="hidden" name="id" value="([^"]+)"')
        fname = scrapertools.get_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
        referer = scrapertools.get_match(data,'<input type="hidden" name="referer" value="([^"]*)"')
        hashstring = scrapertools.get_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
        imhuman = scrapertools.get_match(data,'<input type="submit" name="imhuman".*?value="([^"]+)"').replace(" ","+")
        
        import time
        time.sleep(10)
        
        # Lo pide una segunda vez, como si hubieras hecho click en el banner
        #op=download1&usr_login=&id=z3nnqbspjyne&fname=Coriolanus_DVDrip_Castellano_by_ARKONADA.avi&referer=&hash=nmnt74bh4dihf4zzkxfmw3ztykyfxb24&imhuman=Continue+to+Video
        post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
        headers.append(["Referer",page_url])
        data = scrapertools.cache_page( page_url , post=post, headers=headers )
        logger.info("data="+data)
    
        # Extrae la URL
        #media_url = scrapertools.get_match( data , 'file\: "([^"]+)"' )
        media_url = scrapertools.get_match( data , patron )
        
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [streaminto]",media_url])

    for video_url in video_urls:
        logger.info("[streamcloud.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    encontrados.add("http://streamin.to/embed-theme.html")
    encontrados.add("http://streamin.to/embed-jquery.html")
    encontrados.add("http://streamin.to/embed-s.html")
    encontrados.add("http://streamin.to/embed-images.html")
    encontrados.add("http://streamin.to/embed-faq.html")
    encontrados.add("http://streamin.to/embed-embed.html")
    encontrados.add("http://streamin.to/embed-ri.html")
    encontrados.add("http://streamin.to/embed-d.html")
    encontrados.add("http://streamin.to/embed-css.html")
    encontrados.add("http://streamin.to/embed-js.html")
    encontrados.add("http://streamin.to/embed-player.html")
    encontrados.add("http://streamin.to/embed-cgi.html")
    devuelve = []

    #http://streamin.to/z3nnqbspjyne
    patronvideos  = 'streamin.to/([a-z0-9A-Z]+)'
    logger.info("[streaminto.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streaminto]"
        url = "http://streamin.to/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'streaminto' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://streamin.to/embed-z3nnqbspjyne.html
    patronvideos  = 'streamin.to/embed-([a-z0-9A-Z]+)'
    logger.info("[streaminto.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streaminto]"
        url = "http://streamin.to/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'streaminto' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://streamin.to/z3nnqbspjyne")

    return len(video_urls)>0
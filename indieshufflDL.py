#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from multiprocessing.dummy import Pool as ThreadPool
from mutagen.id3 import ID3, TIT2, TPE1,TPE2,APIC,ID3NoHeaderError,TALB,TCMP
#from PIL import Image
#from io import BytesIO
from lxml import html
import os.path
#get latest trackid to get the playlist and dump music from this playlist
dom=html.fromstring(requests.get('http://www.indieshuffle.com/new-songs/').text)
mId=dom.xpath('//div[@class="cover col-4"]/div[2]/@data-track-id')[0]
mCount=100
url="http://www.indieshuffle.com/mobile/player?id={}&key=04ffdb11a4c54c729c743eccc46da873&count={}&page=1&type=newest&sort=order".format(mId,mCount)
print ("start downloading from: {}\n initial track id: {}\n count: {}".format(url,mId,mCount))
resp=requests.get(url)
jsonresp= resp.json()
def dumpIt(entry):
    try:
        r =requests.get(entry['source'],stream=True)
    except Exception:
        return
    #filename ='{}.mp3'.format(entry['slug'].encode('utf8'))
    filename ='{}.mp3'.format(entry['slug'])
    localSize=os.path.getsize(filename)
    remoteSize=int(r.headers['Content-Length'])
    print ("filename:{} local size:{} remote size:{}".format(filename,localSize,remoteSize))
    if os.path.isfile(filename) and remoteSize < localSize:
        return
    f = open(filename, 'wb')
    for chunk in r.iter_content(1024):
        f.write(chunk)
    f.truncate()

    #write id3 tags

    try:
        audio = ID3(filename)
    except ID3NoHeaderError:
        audio = ID3()
    audio.add(TIT2(encoding=3,text=entry['title']))
    audio.add(TPE1(encoding=3,text=entry['artist']))
    audio.add(TPE2(encoding=3,text="IndieShuffle"))
    # audio.add(TALB(encoding=3,text="IndieShuffle"))
    audio.add(TCMP(encoding=3,text="1"))
    try:
        r =requests.get(entry['artwork'],stream=True)
        r.raw.decode_content = True
####################################################################################################
        #inMemBuffer = BytesIO()
        #with Image.open(r.raw) as img:
            #img.save(inMemBuffer,'png')
        #inMemBuffer.seek(0)
        #encoding=3 is required to enable MacOs preview to show the coverart icon
        #audio.add(APIC(encoding=3,type=3,mime='image/png',data=inMemBuffer.read()))
####################################################################################################
        #encoding=3 is required to enable MacOs preview to show the coverart icon
        audio.add(APIC(encoding=3,type=3,mime='image/jpeg',data=r.raw.read()))
    except Exception:
        pass
    audio.save(filename)

pool =ThreadPool(10)
pool.map(dumpIt,jsonresp['posts'])
pool.close()
pool.join()

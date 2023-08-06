# -*- coding: utf-8 -*-
#
#       podget.py
#       
#       Copyright 2009 Rafael G. Martins <rafael@rafaelmartins.eng.br>
#       
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are
#       met:
#       
#       * Redistributions of source code must retain the above copyright
#         notice, this list of conditions and the following disclaimer.
#       * Redistributions in binary form must reproduce the above
#         copyright notice, this list of conditions and the following disclaimer
#         in the documentation and/or other materials provided with the
#         distribution.
#       * Neither the name of the author nor the names of its
#         contributors may be used to endorse or promote products derived from
#         this software without specific prior written permission.
#       
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#       A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#       THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""PodGet - A simple podcast client that runs on CLI

Configuration:

    Section podcast:
        names and urls of the RSS feeds

    Section config:
        limit_rate: Limit rate of the doownload bandwidth (on KB/s)
        media_dir: Directory to save the files

Example of config file (~/.podget):

[podcast]
na_geral = http://www.radiobandeirantes.com.br/rss/xmls/humor.xml
phpspcast = http://feeds2.feedburner.com/phpspcast
nerdcast = http://jovemnerd.ig.com.br/?feed=rss2&cat=42

[config]
limit_rate = 40
media_dir = /home/rafael/podcast

-------------------------------------------------------------------
If you want colors on CLI, please install PyColors.
"""

__all__ = ['PodGet', 'PodGetException']

__author__ = 'Rafael Goncalves Martins'
__email__ = 'rafael@rafaelmartins.eng.br'

__description__ = 'A simple podcast client that runs on CLI'
__url__ = 'http://rafaelmartins.eng.br/projetos/'
__copyright__ = '(c) 2009 %s' % __author__
__license__ = 'BSD'

__version__ = '0.1.1'

from os import makedirs, sep
from os.path import exists, join, expanduser
from shutil import move
from subprocess import call, Popen, PIPE
from urllib2 import urlopen
from xml.dom.minidom import parse as parseXML
from ConfigParser import ConfigParser

class PodGetException(Exception):
    pass

class PodGet:
    
    config = None
    
    def __init__(self):
        self.__have_bin(['wget', '--version'])
        self.__have_bin(['mplayer'])
        self.__load_config()
    
    def __have_bin(self, args=[]):
        try:
            p = Popen(
                args,
                stdout=PIPE,
                stderr=PIPE
            )
            if p.wait() != 0:
                if len(args) == 0:
                    args.append('undefined')
                raise PodGetException('You have to install %s.' % args[0])
        except:
            raise PodGetException('You have to install %s.' % args[0])

    def __load_config(self):
        file = '~/.podget'
        if self.config == None:
            self.config = ConfigParser()
            if not exists(expanduser(file)):
                self.config.add_section('config')
                self.config.set('config', 'media_dir', '')
                self.config.set('config', 'limit_rate', '')
                self.config.add_section('podcast')
                fp = open(expanduser(file), 'w')
                self.config.write(fp)
                fp.close()
                raise PodGetException('Missing config file: %s. The file will be created for you.' % file)
            else:
                fp = open(expanduser(file))
                self.config.readfp(fp)
                fp.close()
                self.media_dir = self.__get_config('media_dir', '')
                if self.media_dir == '':
                    raise PodGetException('Invalid media directory.')
                self.limit_rate = self.__get_config('limit_rate', '')
                if self.limit_rate == '':
                    self.limit_rate = None
                else:
                    try:
                        self.limit_rate = int(self.limit_rate)
                    except:
                        raise PodGetException('Invalid download limit rate.')
                podcasts = self.config.items('podcast')
                self.podcasts = {}
                cont = 1
                for pod in podcasts:
                    self.podcasts[cont] = pod
                    cont += 1
    
    def __get_config(self, option, default):
        if self.config.has_option('config', option):
            return self.config.get('config', option)
        else:
            return default
    
    def __unpack_podcast_tup(self, pod_id):
        try:
            name, url = self.podcasts[int(pod_id)]
        except:
            raise PodGetException('Invalid podcast ID.')
        return name, url
    
    def list_podcasts(self):
        ret = []
        for id in self.podcasts.keys():
            name, url = self.podcasts[id]
            ret.append((id, name))
        return ret
 
    def get_name_by_id(self, pod_id):
        name, url = self.__unpack_podcast_tup(pod_id)
        return name
 
    def get_latest(self, pod_id):
        latest = None
        name, url = self.__unpack_podcast_tup(pod_id)
        try:
            fp = urlopen(url)
            rss = parseXML(fp)
            fp.close()
        except:
            raise PodGetException('Failed to parse RSS feed.')
        chapters = rss.getElementsByTagName('enclosure')
        for chapter in chapters:
            if chapter.getAttribute('type').startswith('audio/'):
                latest = chapter.getAttribute('url')
                break
        if latest == None:
            raise PodGetException('No podcast available on RSS feed.')
        filename = latest.split('/')[-1]
        directory = join(self.media_dir, name)
        if not exists(directory):
            makedirs(directory)
        filepath = join(directory, filename)
        if exists(filepath):
            raise PodGetException('No newer podcast available.')
        return latest, filepath
    
    def download(self, url, filepath):
        args = [
            'wget',
            '--output-document=%s.part' % filepath,
            '--continue',
            url
        ]
        if self.limit_rate != None:
            args.insert(1, '--limit-rate=%sk' % self.limit_rate)
        if call(args) != 0:
            raise PodGetException('Failed to save the file.')
        move(filepath + '.part', filepath)
        filepath_list = filepath.split('/')
        fp = open(join(sep.join(filepath_list[:-1]), 'LATEST'), 'w')
        fp.write(filepath_list[-1])
        fp.close()
    
    def get_latest_to_play(self, pod_id):
        name, url = self.__unpack_podcast_tup(pod_id)
        latest_file = join(self.media_dir, name, 'LATEST')
        if not exists(latest_file):
            raise PodGetException('No chapter available to play.')
        fp = open(latest_file)
        latest = fp.read().strip()
        fp.close()
        return join(self.media_dir, name, latest)
    
    def play(self, podcast):
        if call(['mplayer', podcast]) != 0:
            raise PodGetException('Failed to play the chapter.')

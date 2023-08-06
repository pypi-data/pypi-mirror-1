# -*- coding: utf-8 -*-
"""Provides template skinning abilities for templates.

:Authors:
    - Bruce Kroeze
"""
"""
New BSD License
===============
Copyright (c) 2008, Bruce Kroeze http://solidsitesolutions.com

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of SolidSiteSolutions LLC, Zefamily LLC nor the names of its 
      contributors may be used to endorse or promote products derived from this 
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
__docformat__="restructuredtext"

from banjo.common.templatetags.media_tags import current_media_url
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from glob import glob
from threaded_multihost import threadlocals
from threaded_multihost.utils import current_media_url
import livesettings as config
import logging
import os
import simplejson
import utils

log = logging.getLogger('skins.skin')

_CACHE = {}

class Skin(object):
    
    def __init__(self, path):
        
        self.path = path
        self.key = self.path.split(os.path.sep)[-1]
        self.info = self._skin_info()
        self.name = self.info['name']
        self.version = self.info.get('version', 1)
        self.author = self.info.get('author', 'Unknown')

    def _skin_info(self):
        config = os.path.join(self.path, 'CONFIG.json')
        skindata = {}
        if utils.is_file(config):
            cf = open(config, 'r')
            data = cf.read()
            try:
                skindata = simplejson.loads(data)
            except Exception, e:
                log.debug('%s\n%s', e, data)

        name = skindata.get('name', None)
        if not name:
            name = self.key
            skindata['name'] = name

        return skindata
        
    def _media_url(self):
        return utils.url_join(current_media_url(), 'skins', self.key, '/')
        
    media_url = property(fget=_media_url)
                
    def __cmp__(self, other):
        return cmp((self.name, self.version), (other.name, other.version))
        
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

def active_skin():
    key = threadlocals.get_thread_variable('skin', None)
    if not key:
        try:
            key = config.config_value('SKIN','DEFAULT_SKIN')
        except config.SettingNotSet:
            key = 'default'
    keys = get_skin_keys()
    if not key in keys:
        if len(keys) > 0:
            log.warn("Cannot find active skin '%s' in skin list, using default skin '%s'", key, keys[0])
            key = keys[0]
        else:
            log.fatal("No Skins found - cannot return any default skin.")
        
    return get_skin(key)
    
def get_skin(path):
    load_skins()
    return _CACHE[path]    

def get_skin_choices():
    load_skins()
    choices = _CACHE.values()
    choices.sort()
    return [(skin.key, skin.name) for skin in choices]
    
def get_skin_keys():
    load_skins()
    choices = _CACHE.values()
    choices.sort()
    return [skin.key for skin in choices]

def load_skins():
    global _CACHE
    if not len(_CACHE)>0:

        try:
            skindirs = settings.SKIN_DIRS
        except:
            log.error('No SKIN_DIRS in settings')
            raise ImproperlyConfigured('No skins loaded - you must add SKIN_DIRS to settings')

        skindirs = utils.get_flat_list(skindirs)
        skindirs = [os.path.join(s, '*') for s in skindirs if s]
        for skindir in skindirs:
            for path in glob(skindir):
                if utils.is_dir(path):
                    skin = Skin(path)
                    log.debug('adding %s' % skin.key)
                    _CACHE[skin.key] = skin
                        
        if len(_CACHE) == 0:
            log.error('No skins found in %s', skindirs)
            raise ImproperlyConfigured('No skins loaded - noting found in skin directories, searched: %s', "\n".join(skindirs))
    
        log.debug('Loaded skins')
        

def remember_skin(key):
    threadlocals.set_thread_variable('skin', key)
    
# -*- coding: utf-8 -*-
"""Provides secure-aware skinned media url tags.

:Authors:
    - Bruce Kroeze
"""
"""
New BSD License
===============
Copyright (c) 2008, Bruce Kroeze http://coderseye.com

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

from banjo.common.templatetags import media_tags
from banjo.common.util import logs
from banjo.common.util.files import url_join
from django import template
from django.utils import translation
from skins import skin
from threaded_multihost import threadlocals

log = logs.getLogger("skin_tags")
register = template.Library()

def _skin_media_url():
    return skin.active_skin().media_url


class SkinMediaURLNode(template.Node):
    def __init__(self, url):
        self.url = url

    def render(self, context):
        if self.url:
            return url_join(_skin_media_url(), self.url)
        else:
            return _skin_media_url()

@register.tag
def skin_media_url(parser, token):
    parts = token.contents.split(None)
    if len(parts) > 1:
        url = parts[1:]
    else:
        url = None
    return SkinMediaURLNode(url)

@register.filter
def skin_media(val):
    return url_join(_skin_media_url(), val)

class SkinMediaLocaleURLNode(template.Node):
    def __init__(self, url):
        self.url = url

    def render(self, context):
        prefix = skin_media_url()

        language = translation.get_language()

        if self.url:
            return url_join(prefix, self.url, language)
        else:
            return url_join(prefix, language)

@register.tag
def skin_media_locale_url(parser, token):
    parts = token.contents.split(None)
    if len(parts) > 1:
        url = parts[1:]
    else:
        url = None
    return SkinMediaLocaleURLNode(url)

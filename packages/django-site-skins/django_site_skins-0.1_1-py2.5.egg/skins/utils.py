# -*- coding: utf-8 -*-
"""Provides utility functions for skins.

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
import os, os.path
import stat

def can_loop_over(maybe):
    """Test value to see if it is list like"""
    try:
        iter(maybe)
    except:
        return 0
    else:
        return 1

def is_scalar(maybe):
    """Test to see value is a string, an int, or some other scalar type"""
    return is_string_like(maybe) or not can_loop_over(maybe)

def flatten_list(sequence, scalarp=is_scalar, result=None):
    """flatten out a list by putting sublist posts in the main list"""
    if result is None:
        result = []

    for item in sequence:
        if scalarp(item):
            result.append(item)
        else:
            flatten_list(item, scalarp, result)

def get_flat_list(sequence):
    """flatten out a list and return the flat list"""
    flat = []
    flatten_list(sequence, result=flat)
    return flat

def is_dir(path, follow_links=1):
    """Tests that path exists and is a dir"""
    ret = 0
    path = resolve_path(path)
    if os.path.exists(path):
        fs = os.stat(path)[stat.ST_MODE]
        if stat.S_ISDIR(fs):
            ret = 1

        elif (stat.S_ISLNK(fs)
            and follow_links > 0
            and follow_links < 10):
            next = os.readlink(path)
            follow_links += 1
            ret = is_dir(next, follow_links)

    return ret

def is_file(path, follow_links=1):
    """Tests that path exists, and is a file"""
    ret = 0
    path = resolve_path(path)
    if os.path.exists(path):
        fs = os.stat(path)[stat.ST_MODE]
        if stat.S_ISREG(fs):
            ret = 1

        elif (stat.S_ISLNK(fs)
            and follow_links > 0
            and follow_links < 10):
            next = os.readlink(path)
            follow_links += 1
            ret = is_file(next, follow_links)

    return ret

def is_string_like(maybe):
    """Test value to see if it acts like a string"""
    try:
        maybe+""
    except TypeError:
        return 0
    else:
        return 1

def resolve_path(fname):
    """Expands all environment variables and tildes, returning the absolute path."""
    fname = os.path.expandvars(fname)
    fname = os.path.expanduser(fname)
    if fname.startswith("./"):
        fname = "%s%s" % (os.getcwd(), fname[1:])
    return os.path.abspath(fname)

def url_join(*args):
    """Join any arbitrary strings into a forward-slash delimited list.
    Do not strip leading / from first element, nor trailing / from last element."""
    if len(args) == 0:
        return ""

    args = get_flat_list(args)

    if len(args) == 1:
        return str(args[0])

    else:
        args = [str(arg).replace("\\", "/") for arg in args]

        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    return joined.replace("\\", "/")

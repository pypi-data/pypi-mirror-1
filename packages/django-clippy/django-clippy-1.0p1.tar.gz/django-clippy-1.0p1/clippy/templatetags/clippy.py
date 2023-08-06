#!/usr/bin/env python
# encoding: utf-8
"""
clippy.py

Created by Maximillian Dornseif on 2010-02-27.
Copyright (c) 2010 HUDORA. Consider it MIT licensed.
"""

from django import template
from django.conf import settings


register = template.Library()
@register.simple_tag
def clippy(htmlElementId, bgcolor='#ffffff'):
    media_url = settings.MEDIA_URL
    if not bgcolor:
        bgcolor = settings.get('CLIPPY_BGCOLOR', '#ffffff')
    return \
    """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
                width="110"
                height="14"
                id="clippy_%(htmlElementId)s" >
        <param name="movie" value="%(media_url)s/clippy.swf"/>
        <param name="allowScriptAccess" value="always" />
        <param name="quality" value="high" />
        <param name="scale" value="noscale" />
        <param NAME="FlashVars" value="id=%(htmlElementId)s">
        <param name="bgcolor" value="%(bgcolor)s">
        <embed src="%(media_url)s/clippy.swf?x=23"
               width="110"
               height="14"
               name="clippy"
               quality="high"
               allowScriptAccess="always"
               type="application/x-shockwave-flash"
               pluginspage="http://www.macromedia.com/go/getflashplayer"
               FlashVars="id=%(htmlElementId)s"
               bgcolor="%(bgcolor)s"
        />
        </object>""" % locals()

# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: asset_tag.py 66 2008-01-03 23:47:36Z s0undt3ch $
# =============================================================================
#             $URL: http://pastie.ufsoft.org/svn/sandbox/MinificationWebHelpers/trunk/minwebhelpers/asset_tag.py $
# $LastChangedDate: 2008-01-03 23:47:36 +0000 (Thu, 03 Jan 2008) $
#             $Rev: 66 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import re
import os
import logging
import StringIO
from jsmin import JavascriptMinify
import cssutils
from cssutils.serialize import CSSSerializer
from pylons import config
from pylons.decorators.cache import beaker_cache

from webhelpers.rails.asset_tag import javascript_include_tag as \
                                       __javascript_include_tag
from webhelpers.rails.asset_tag import stylesheet_link_tag as \
                                       __stylesheet_link_tag

log = logging.getLogger(__name__)

__all__ = ['javascript_include_tag', 'stylesheet_link_tag']

def javascript_include_tag(*sources, **options):

    @beaker_cache(key='sources', expire='never', type='dbm')
    def combine_sources(sources, fs_root):
        if len(sources) < 2:
            log.debug('No need to combine, only one source provided')
            return sources

        log.debug('combining javascripts: %r', sources)
        httpbase = os.path.commonprefix(['/'.join(s.split('/')[:-1])+'/'
                                         for s in sources])
        jsbuffer = StringIO.StringIO()
        names = []
        bases = os.path.commonprefix([b.split('/')[:-1] for b in sources])
        log.debug('Base: %s', httpbase)
        for source in sources:
            log.debug('appending %s', source)
            _source = os.path.join(fs_root, *(source).split('/'))
            names.append(source.split('/')[-1:][0][:-3])
            jsbuffer.write(open(_source, 'r').read())
            jsbuffer.write('\n')
        fname = '.'.join(names+['COMBINED', 'js'])
        log.debug('Names: %r', names)
        log.debug('Combined Name: %s', fname)
        fpath = os.path.join(fs_root, *((httpbase+fname).split('/')))
        log.debug('writing %s', fpath)
        open(fpath, 'w').write(jsbuffer.getvalue())
        return [httpbase + fname]

    @beaker_cache(key='sources', expire='never', type='dbm')
    def get_sources(sources, fs_root=''):
        log.debug('Generating minified sources if needed')
        jsm = JavascriptMinify()
        _sources = []

        for source in sources:
            _source = os.path.join(fs_root, *(source[:-3]+'.min.js').split('/'))
            if os.path.exists(_source):
                _sources.append(source[:-3]+'.min.js')
            else:
                _source = os.path.join(fs_root, *source.split('/'))
                minified = _source[:-3]+'.min.js'
                log.debug('minifying %s -> %s', source,
                            source[:-3]+'.min.js')
                jsm.minify(open(_source, 'r'), open(minified, 'w'))
                _sources.append(source[:-3]+'.min.js')
        return _sources

    if not config.get('debug', False):
        fs_root = root = config.get('pylons.paths').get('static_files')
        if options.pop('combined', False):
            sources = combine_sources([source for source in sources], fs_root)

        if options.pop('minified', False):
            sources = get_sources([source for source in sources], fs_root)
    return __javascript_include_tag(*sources, **options)

def stylesheet_link_tag(*sources, **options):

    @beaker_cache(key='sources', expire='never', type='dbm')
    def combine_sources(sources, fs_root):
        if len(sources) < 2:
            log.debug('No need to combine, only one source provided')
            return sources

        log.debug('combining javascripts: %r', sources)
        httpbase = os.path.commonprefix(['/'.join(s.split('/')[:-1])+'/'
                                         for s in sources])
        jsbuffer = StringIO.StringIO()
        names = []
        log.debug('Base: %s', httpbase)
        for source in sources:
            log.debug('appending %s', source)
            _source = os.path.join(fs_root, *(source).split('/'))
            names.append(source.split('/')[-1:][0][:-4])
            jsbuffer.write(open(_source, 'r').read())
            jsbuffer.write('\n')
        fname = '.'.join(names+['COMBINED', 'css'])
        log.debug('Names: %r', names)
        log.debug('Combined Name: %s', fname)
        fpath = os.path.join(fs_root, *((httpbase+fname).split('/')))
        log.debug('writing %s', fpath)
        open(fpath, 'w').write(jsbuffer.getvalue())
        return [httpbase + fname]

    @beaker_cache(key='sources', expire='never', type='dbm')
    def get_sources(sources, fs_root):
        log.debug('Generating minified sources if needed')
        _sources = []

        for source in sources:
            _source = os.path.join(fs_root, *(source[:-4]+'.min.css').split('/'))
            if os.path.exists(_source):
                _sources.append(source[:-4]+'.min.css')
            else:
                _source = os.path.join(fs_root, *source.split('/'))
                minified = _source[:-4]+'.min.css'
                log.debug('minifying %s -> %s', source,
                            source[:-4]+'.min.css')
                sheet = cssutils.parse(_source)
                sheet.setSerializer(CSSUtilsMinificationSerializer())
                cssutils.ser.prefs.useMinified()
                log.debug('writing %s', minified)
                open(minified, 'w').write(sheet.cssText)
                _sources.append(source[:-4]+'.min.css')
        return _sources

    if not config.get('debug', False):
        fs_root = root = config.get('pylons.paths').get('static_files')
        if options.pop('combined', False):
            sources = combine_sources([source for source in sources], fs_root)

        if options.pop('minified', False):
            sources = get_sources([source for source in sources], fs_root)
    return __stylesheet_link_tag(*sources, **options)


class CSSUtilsMinificationSerializer(CSSSerializer):
    def __init__(self, prefs=None):
        CSSSerializer.__init__(self, prefs)

    def do_css_CSSStyleDeclaration(self, style, separator=None):
        log.debug('Style: %r, %r', style, style.seq)
        try:
            log.debug('Color: %r', style.getPropertyValue('color'))
            color = style.getPropertyValue('color')
            if color and color is not u'':
                color = self.change_colors(color)
                log.debug('Returned Color: %r', color)
                style.setProperty('color', color)
        except:
            pass
        return re.sub(r'0\.([\d])+', r'.\1',
                      re.sub(r'(([^\d][0])+(px|em)+)+', r'\2',
                      CSSSerializer.do_css_CSSStyleDeclaration(self, style,
                                                               separator)))

    def change_colors(self, color):
        log.debug("changing color for color: %r", color)
        colours = {
            'black': '#000000',
            'fuchia': '#ff00ff',
            'yellow': '#ffff00',
            '#808080': 'gray',
            '#008000': 'green',
            '#800000': 'maroon',
            '#000800': 'navy',
            '#808000': 'olive',
            '#800080': 'purple',
            '#ff0000': 'red',
            '#c0c0c0': 'silver',
            '#008080': 'teal'
        }
        if color.lower() in colours:
            color = colours[color.lower()]

        if color.startswith('#') and len(color) == 7:
            log.debug('Trying to reduce color length')
            if color[1]==color[2] and color[3]==color[4] and color[5]==color[6]:
                log.debug('Reduced from %s to #%s%s%s', color, color[1],
                          color[3], color[5])
                color = '#%s%s%s' % (color[1], color[3], color[5])
        return color

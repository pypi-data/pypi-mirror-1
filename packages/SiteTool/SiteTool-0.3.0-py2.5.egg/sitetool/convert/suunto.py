"""
A simple module for parsing the XML files contained within Suunto .SDE files
from Dive Manager. Just rename the .SDE as .zip and extract the files to a
directory, put this file in that directory and run it.

A set of graphs from Google Charts showing your dive profiles will be generated
with the Suunot dive number as the filename.

It doesn't parse the <HEADER> tag because I couldn't see what use it was.
"""

import os.path
from xml.dom.minidom import parse, parseString
import logging
import urllib2
import zipfile

import logging
import re
import os
import sys

from sitetool.template.dreamweaver import DreamweaverTemplateInstance

from sitetool.exception import PluginError
from sitetool.convert.plugin import Plugin

log = logging.getLogger(__name__)

class Dive(object):
    def __init__(self, dom):
        self.dom = dom
        self.properties = {}
        self.samples = []
        self.current_sample = {}
        suunto = self.dom.childNodes[0]
        for child in suunto.childNodes:
            if child.nodeName == 'MSG':
                self.handle_msg(child)
            elif child.nodeName == 'HEADER':
                # Just ignore it
                pass
            elif child.nodeType != child.TEXT_NODE:
                log.warning('Ignoring unexpected suunto node %r'%child)
        if self.current_sample:
            self.samples.append(self.current_sample)

    def get_text(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def handle_property(self, node):
        self.properties[node.nodeName] = self.get_text(node.childNodes)

    def handle_sample_item(self, node):
        self.current_sample[node.nodeName] = self.get_text(node.childNodes)

    def handle_sample(self, node):
        if self.current_sample:
            self.samples.append(self.current_sample)
            self.current_sample = {}
        for child in node.childNodes:
            if child.nodeName in sample_names:
                self.handle_sample_item(child)
            elif child.nodeType != child.TEXT_NODE:
                log.warning('Ignoring unexpected sample node %r'%child)

    def handle_msg(self, node):
        for child in node.childNodes:
            if child.nodeName in properties:
                self.handle_property(child)
            elif child.nodeName == 'SAMPLE':
                self.handle_sample(child)
            elif child.nodeType != child.TEXT_NODE:
                log.warning('Ignoring unexpected msg node %r'%child)

sample_names = [
    'SAMPLETIME',
    'DEPTH',
    'PRESSURE',
    'TEMPERATURE',
    'BOOKMARK',
    'SACRATE',
    'CYLPRESS',
    'BOOKMARKTYPE',
    'OXYGENPCT',
]
properties = [
    'WRISTOPID',
    'SAMPLECNT',
    'DATE', 
    'TIME',
    'MAXDEPTH',
    'MEANDEPTH',
    'SAMPLEINTERVAL',
    'LOGTITLE',
    'LOGNOTES',
    'FOLDER',
    'LOCATION',
    'SITE',
    'WEATHER',
    'WATERVISIBILITY',
    'AIRTEMP',
    'WATERTEMPMAXDEPTH',
    'WATERTEMPATEND',
    'PARTNER',
    'DIVEMASTER',
    'BOATNAME',
    'CYLINDERDESCRIPTION',
    'CYLINDERSIZE',
    'CYLINDERUNITS',
    'CYLINDERWORKPRESSURE',
    'CYLINDERSTARTPRESSURE',
    'CYLINDERENDPRESSURE',
    'DIVENUMBER',
    'DCDIVENUMBER',
    'DIVESERIES',
    'DEVICEMODEL',
    'DIVETIMESEC',
    'PERSONALINFO',
    'GASMODE',
    'ALTMODE',
    'PMODE',
    'WATERVISIBILITYDESC',
    'SACRATE',
    'OLFPCT',
    'WEIGTH',
    'O2PCT',
    'O2PCT_2',
    'O2PCT_3',
    'OTUPCT',
    'CNSPCT',
    'PO2MAX',
    'RGBMPCT',
    'HPTRANSMITTER',
    'SURFACETIME',
    'NOPROFILE',
    'PREVTPRESSURE_1',
    'PREVTPRESSURE_2',
    'PREVTPRESSURE_3',
    'PREVTPRESSURE_4',
    'PREVTPRESSURE_5',
    'PREVTPRESSURE_6',
    'PREVTPRESSURE_7',
    'PREVTPRESSURE_8',
    'PREVTPRESSURE_9',
    'CUSTOM1',
    'CUSTOM2',
    'CUSTOM3',
    'CUSTOM4',
    'CUSTOM5',
]

def get_dives_in_directory(path):
    dives = []
    for filename in os.listdir(path):
        if not os.path.isdir(filename) and filename.endswith('.xml'):
            dom = parse(filename)
            dive = Dive(dom)
            dives.append(dive)
    return dives

def make_chart(dive, filename):
    max_x = 0
    max_y = 0
    data = []
    for sample in dive.samples:
        depth = float(sample['DEPTH'])
        if depth > max_y:
            max_y = depth
        time = int(sample['SAMPLETIME'])
        if time > max_x:
            max_x = time
        data.append((time, depth))
    data.sort()
    x_max = max_x
    while True:
        parts = str(x_max).split('.')
        if parts[0][-1] in ['0','5'] and int(parts[0])>=max_x:
            break
        x_max=int(parts[0])+1
    y_max = max_y
    while True:
        parts = str(y_max).split('.')
        if parts[0][-1] in ['0','5'] and int(parts[0])>=max_y:
            break
        y_max=int(parts[0])+1
    xs = []
    ys = []
    for x, y in data:
        perc_x = round((x*100.0)/float(x_max),2)
        perc_y = round((y*100.0)/float(y_max),2)
        log.debug('%r %r %r %r %r %r', x, y, max_x, max_y, perc_x, perc_y)
        xs.append(str(perc_x).replace('.0,',','))
        ys.append(str(100-round(perc_y,3)).replace('.0,',','))
    y_axis = [str(y_max*i/5) for i in range(1,6)]
    y_axis.reverse()
    url = 'http://chart.apis.google.com/chart?cht=lxy&chxt=x,y&chs=750x300&chd=t:%s|%s&chco=224499&chm=B,76A4FB,0,0,0&chxl=0:|%s|1:|%s|&chg=50,50'%(
        ','.join(xs),
        ','.join(ys),
        '|'.join(['0']+[str(x_max*i/600) for i in range(1,11)]),
        '|'.join(y_axis),
    )
    save_url(url, filename)

def save_url(url, filename):
    log.debug(url)
    try:
        fp=urllib2.urlopen(url)
        data = fp.read()
        fp.close()
        fp = open(filename, 'wb')
        fp.write(data)
        fp.close()
    except urllib2.URLError, e:
        log.error('Could not get chart for %r: %r', filename, str(e))

class SuuntoPlugin(Plugin):

    def parse_config(self, config):
        if not config:
            return None
        result = {}
        if config.has_key('DEFAULT_TEMPLATE'):
            template = config['DEFAULT_TEMPLATE']
            if '..' in template:
                raise PluginError('Blog template paths cannot contain .. characters')
            if template.startswith('/'):
                raise PluginError('Blog template paths cannot start with /')
            result['template'] = os.path.join(self.site_root, template)
        if not result.get('template'):
            raise Exception('No default template specified for Suunto plugin')
        return result

    def on_file(self, path):
        if not self.generated_files:
            log.debug('DefaultPlugin: Skipping %r, --ignore-user-files set', path)
            return False
        if not path.endswith('.SDE'):
            log.debug("Don't know how to convert %r files"%(path.split('.')[-1]))
            return False
        sde = zipfile.ZipFile(path)
        for file in sde.infolist():
            if file.orig_filename.endswith('.xml'):
                content = sde.read(file.orig_filename)
                dom = parseString(content)
                dive = Dive(dom)
                log.debug(
                    'Extracted dive %s, %d properties, %d data points',
                    dive.properties['DIVENUMBER'],
                    len(dive.properties),
                    len(dive.samples)
                )
                dest_page = os.path.join(os.path.split(path)[0], 'log_%s.suunto.html'%dive.properties['DIVENUMBER'])
                if os.path.exists(dest_page) and\
                   (not os.stat(path).st_mtime > os.stat(dest_page).st_mtime) and not self.force:
                    log.debug('Skipping %s since an HTML file of the same name already exists', dest_page)
                else:
                    page = DreamweaverTemplateInstance(self.config['template'])
                    page['doctitle'] = '<title>Computer Log '+dive.properties['DIVENUMBER']+'</title>'
                    page['section_navigation'] = page['section_navigation_bottom'] = ''
                    page['heading'] = 'Computer Log '+dive.properties['DIVENUMBER']
                    content = []
                    content.append('<h2>Dive Profile</h2><p><img src="%s" /></p>'%('log_%s.png'%(dive.properties['DIVENUMBER'])))
                    content.append('<h2>Properties</h2><table border="0">')
                    a = dive.properties.items()
                    a.sort()
                    for k, v in a:
                        if k and v:
                            content.append('<tr><td><b>%s:</b></td><td>%s</td></tr>'%(k, v))
                    content.append('</table>')
                    page['content'] = '\n'.join(content)
                    page.save_as_page(dest_page)
                dest_chart = os.path.join(os.path.split(path)[0], 'log_%s.png'%dive.properties['DIVENUMBER'])
                if os.path.exists(dest_chart) and\
                   (not os.stat(path).st_mtime > os.stat(dest_chart).st_mtime) and not self.force:
                    log.debug('Skipping %s since an chart of the same name already exists', dest_chart)
                else:
                    make_chart(dive, dest_chart)
        return True


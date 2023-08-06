##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved.
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation; either version 2 of the License, or            
#    (at your option) any later version.                                          
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from collective.imstransport.utilities.imsinterchange import IMSReader
from collective.imstransport.utilities.packagingio import ZipfileReader
from collective.imstransport.utilities.bb.bbreader import BBReader
from zope.component import getUtility
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from xml.parsers.expat import ExpatError
from collective.imstransport.IMS_exceptions import ManifestError
from BeautifulSoup import BeautifulSoup
from Products.CMFCore.interfaces import ISiteRoot
import htmlentitydefs
from configbb import EMBEDDED_STRING
import re

class IMSBBReader(IMSReader):
    """ Create objects from IMS manifest. """

    def readPackage(self, file, context):
        """ Read the manifest """
        source = ZipfileReader(file)
        objDict = {}
        if not source:
             return False, 'Internal error. No source object specified'
        bbreader = BBReader()
        manifest = source.readManifest()
        if not manifest:
            raise ManifestError, 'Could not locate manifest file "imsmanifest.xml" in the zip archive.'
        try:
            doc = bbreader.parseManifest(manifest)
        except ExpatError, e:
            raise ManifestError, str(e)
        tocpages = []
        orgs = bbreader.readOrganizations(doc)
        resources = bbreader.readResources(doc)
        for x in resources:
            resid, restype, bbfile, bbtitle, bbase = bbreader.readResourceAttributes(x)
            doctext = filetoc = restoc = ''
            metadata = {}
            if restype == 'resource/x-bb-document':
                metadata = {}
                # read the data file
                if bbfile:
                    dataxml = source.readFile(bbfile)
                    resnode = bbreader.parseDataFile(dataxml)
                    metadata = bbreader.readMetadata(resnode)
                if metadata.has_key('text') and metadata['text']:
                    mtext = metadata['text']                    
                    if type(mtext) == type(u''):
                        mtext = mtext.encode('utf-8')
                    ptext = unquotehtml(mtext)
                    utils = getUtility(ISiteRoot).plone_utils
                    soup = BeautifulSoup(ptext)
                    doctext = bbreader.runDocumentFilters(utils, soup, [(EMBEDDED_STRING, 'embedded'),], bbase)
                # Handle Files
                files = bbreader.readFiles(x, bbase)
                entries = []
                for y in files:
                    dhash = resid + y
                    objDict[dhash] = {}
                    dexcludeFromNav = True
                    dfile = y
                    dfileparts = y.split('/')
                    # File is embedded
                    if 'embedded' in y:
                        # Link is encrypted
                        if len(dfileparts) > 0 and dfileparts[-1][0] == '!' and doctext:
                            soup = BeautifulSoup(doctext)
                            embeddedpath = bbreader.readEmbeddedTags(soup)
                            if embeddedpath:
                                dfile = embeddedpath
                    dfilepath = self.createPathFromFile(dfile)
                    did = self.createIdFromFile(dfile)
                    dtype = self.determineType(objDict[dhash], dfile)
                    portal = getUtility(ISiteRoot)
                    utils = portal.plone_utils
                    did = utils.normalizeString(did)
                    dtitle = did
                    if dfilepath:
                        linkpath = '%s/%s' %(dfilepath, did)
                    else:
                        linkpath = did
                    binfile = y
                    folder_files = source.getFolderFiles(dfilepath)
                    if len(folder_files) == 1:
                        binfile = folder_files[0]
                    entries.append((linkpath, dtitle))
                    self.applyCoreMetadata(objDict[dhash], did, dfilepath, dexcludeFromNav, dtype, dtitle, file=binfile)
                if entries:
                    filetoc = bbreader.createTocPage(entries)
            # Handle links
            if metadata.has_key('bbtype') and metadata['bbtype'] == 'Link':
                hash = resid
                objDict[hash] = metadata
                filepath = ''
                id = resid + '.link'
                excludeFromNav = True
                ptype = metadata['bbtype']
                if orgs.has_key(resid):
                    title = orgs[resid]
                else:
                    title = id
                self.applyCoreMetadata(objDict[hash], id, filepath, excludeFromNav, ptype, title)
            elif restype in ['resource/x-bb-document', 'course/x-bb-coursetoc']:
                # Handle normal bb-documents
                hash = resid
                objDict[hash] = metadata
                filepath = ''
                excludeFromNav = True
                ptype = 'Document'
                id = resid + '.html'
                if orgs.has_key(resid):
                    title = orgs[resid]
                else:
                    title = id
                # It's a folder object:
                isFolder = metadata.has_key('bbtype') and metadata['bbtype'] == 'Folder'
                if isFolder or restype == 'course/x-bb-coursetoc':
                    tocpages.append(resid)
                # It's a table of contents object
                if restype == 'course/x-bb-coursetoc':
                    if orgs.has_key(resid):
                        excludeFromNav = False
                        orgstitle = orgs[resid].split('.')
                        # Rewrite label tag
                        if len(orgstitle) > 1 and orgstitle[-1] == 'label':
                            title = re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', ' \\1', orgs[resid].split('.')[1])
                text = doctext
                if type(filetoc) == type(u''):
                    text += filetoc.encode('utf-8')
                self.applyCoreMetadata(objDict[hash], id, filepath, excludeFromNav, ptype, title, text=text)
        # Build table of contents pages
        for z in tocpages:
            tocitems = bbreader.readTocItem(doc, z)
            entries = []
            for titem in tocitems:
                if objDict.has_key(titem):
                    met = objDict[titem]
                    path = met['path']
                    if path:
                        linkpath = '%s/%s' %(path, objDict[titem]['id'])
                    else:
                        linkpath = objDict[titem]['id']
                    entries.append((linkpath, met['title']))
            if entries:
                if objDict[z].has_key('text') and objDict[z]['text']:
                    gtext = objDict[z]['text']
                    if type(gtext) == type(u''):
                        gtext = gtext.encode('utf-8')
                    objDict[z]['text'] = bbreader.createTocPage(entries).encode('utf-8') + gtext
                else:
                    objDict[z]['text'] = bbreader.createTocPage(entries).encode('utf-8')
            else:
                objDict[z]['excludeFromNav'] = True
        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)

    def applyCoreMetadata(self, metadata, id, path, excludeFromNav, type, title, file=None, text=None):
        """ Helper function for applying metadata """
        portal = getUtility(ISiteRoot)
        utils = portal.plone_utils
        metadata['id'] = utils.normalizeString(id)
        metadata['path'] = path
        metadata['excludeFromNav'] = excludeFromNav
        metadata['type'] = type
        if not (metadata.has_key('title') and metadata['title']):
            metadata['title'] = title
        if file:
            metadata['file'] =  file
        if text:
            metadata['text'] = text

def convertentity(m):
    """Convert a HTML entity into normal string (ISO-8859-1)"""
    if m.group(1)=='#':
        try:
            return chr(int(m.group(2)))
        except ValueError:
            return '&#%s;' % m.group(2)
    try:
        return htmlentitydefs.entitydefs[m.group(2)]
    except KeyError:
        return '&%s;' % m.group(2)

def unquotehtml(s):
    """Convert a HTML quoted string into normal string (ISO-8859-1).

    Works with &#XX; and with &nbsp; &gt; etc."""
    return re.sub(r'&(#?)(.+?);',convertentity,s) 

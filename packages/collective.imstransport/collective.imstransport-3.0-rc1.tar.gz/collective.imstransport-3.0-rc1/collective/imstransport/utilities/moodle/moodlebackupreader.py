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

from collective.imstransport.utilities.packagingio import ZipfileReader
from collective.imstransport.utilities.imsinterchange import IMSReader
from collective.imstransport.utilities.interfaces import IIMSObjectCreator
from collective.imstransport.utilities.moodle.backupreader import BackupReader
from zope.component import getUtility
from xml.parsers.expat import ExpatError
from collective.imstransport.IMS_exceptions import ManifestError

class MoodleBackupReader(IMSReader):
    """ Create objects from Moodle backup package """

    def readPackage(self, file, context):
        """ Read in the package """
        source = ZipfileReader(file)
        objDict = {}
        if not source:
            raise ManifestError, 'Internal error. No source object specified'
        backupreader = BackupReader()
        moodlexml = source.readFile('moodle.xml')
        if not moodlexml:
            raise ManifestError, 'Could not locate the "moodle.xml" file in the zip archive.'            
        main = backupreader.parseMoodleXML(moodlexml)
        mods = backupreader.readMods(main)
        visibleids = backupreader.readSections(main)
        for mod in mods:
            metadata = {}
            metadata = backupreader.readResourceMetadata(mod)
            modid = backupreader.readModAttributes(mod)
            objDict[modid] = metadata
            objDict[modid]['id'] = modid
            type = self.determineType(metadata, str(modid))
            objDict[modid]['type'] = type
            if modid in visibleids:
                objDict[modid]['excludeFromNav'] = False
            else:
                objDict[modid]['excludeFromNav'] = True
        objcreator = getUtility(IIMSObjectCreator)
        objcreator.createObjects(objDict, context, source)
                                

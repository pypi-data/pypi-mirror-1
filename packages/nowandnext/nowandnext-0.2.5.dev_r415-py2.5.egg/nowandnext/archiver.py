#####################################################################
# archiver.py module
# for www.archive.org classes
# please do not use yet - this is work in progress 
#
# jctt 5th June 2008 - 6th June 2008
# james@tregaskis.org
#
#####################################################################
import ftplib
import os
import traceback
from elementtree.ElementTree import Element, SubElement, ElementTree as ET

# singleton pattern
class ArchiveOrgHandler:
    instance = None

    def __init__(self, username, password):
        if not ArchiveOrgHandler.instance:
            ArchiveOrgHandler.instance = ArchiveOrgHandler.__ArchiveOrgHandler(username, password)
        else:
            ArchiveOrgHandler.instance._password = password
            ArchiveOrgHandler.instance._username = username
        def __getattr__(self, username, password):
            return __getattr__(self, username, password)

    class __ArchiveOrgHandler:
        def __init__(self, username, password):
            self._username = username 
            self._password = password
        
        #test data for dictionary key value pairs for metatdata xml file
        MetaDataSettings={"identifier":"Myprog2008-06-05A", 
            "collection":" ", 
            "title":"MyProgramme",
            "subject":" ",
            "mediatype":"etree",
            "year":"2008",
            "publicdate":"2008-06-05 15:54:00",
            "creator":"jctt",
            "description":"a fab show which makes your hair curl",
            "coverage":" ",
            "md5s":"",
            "date":"yyyy-mm-dd hh:mm:ss",
            "uploader":"station_bod",
            "addeddate":"",
            "adder":"",
            "pick":"",
            "updateddate":"",
            "updater":"",
            "notes":"",
            "source":"original",
            "lineage":"",
            "venue":"resonanceFm",
            "stream_only":"0",
            "discs":"",
            "has_mp3":"1",
            "shndiscs":"2",
            "public":"1",
            "collection":"etree",
            "publisher":"",
            "taper":"",
            "transferer":"",
            "runtime":"30:00",
            "format":"128bps MP3"}
    
        #@classmethod
        def outerUpload(self, dict_metadata):
            # this takes care of uploading the files including xml files
            #MyHomeMovie/
            #MyHomeMovie/MyHomeMovie_files.xml
            #MyHomeMovie/MyHomeMovie_meta.xml
            #MyHomeMovie/MyHomeMovie.mpeg
            self.writeMetadataXml(dict_metadata)
            self.writeFileXml(dict_metadata)
            self.uploadFile("/home/james/workspace/trunk/src/nowandnext/" + dict_metadata.get("identifier") )
            self.uploadFile("/home/james/workspace/trunk/src/nowandnext/"+ dict_metadata.get("identifier") )

        @classmethod
        def writeFileXml(self, dict_metadata):
            try:
                files = Element("files")
                file = SubElement(files,'file')
                file.attrib["name"]=dict_metadata.get("identifier")
                file.attrib["source"]='original'
                runtime = SubElement(file,'runtime')
                runtime.text = dict_metadata.get("runtime")
                format = SubElement(file,'format')
                format.text = dict_metadata.get("format")
                
                
                ET(files).write(dict_metadata.get("identifier"), encoding='UTF-8')
            except:
                traceback.print_exc()



        # the filename is the fully qualified path of file
        # needs some refactoring to reduce code    
        @classmethod
        def writeMetadataXml( self, dict_metatdata ):
            try:
                _metadata = Element("metadata")
                identifier = SubElement(_metadata,"identifier")
                identifier.text = dict_metatdata.get("identifier")
                mediatype = SubElement(_metadata,'mediatype')
                mediatype.text = dict_metatdata.get("mediatype")
                collection = SubElement(_metadata, "collection")
                collection.text = dict_metatdata.get("collection")
                title = SubElement(_metadata,"title")
                title.text = dict_metatdata.get("title")
                subject = SubElement(_metadata,"subject")
                subject.text = dict_metatdata.get("subject")
                year = SubElement(_metadata,"year")
                year.text = dict_metatdata.get("year")
                publicdate= SubElement(_metadata, "publicdate")
                publicdate.text = dict_metatdata.get("publicdate")
                creator = SubElement(_metadata, "creator")
                creator.text = dict_metatdata.get("creator")
                description = SubElement(_metadata, "description")
                description.text = dict_metatdata.get("description")
                coverage = SubElement(_metadata, "coverage")
                coverage.text = dict_metatdata.get("coverage")
                md5s = SubElement(_metadata, "md5s")
                md5s.text = dict_metatdata.get("md5s")
                date = SubElement(_metadata, "date")
                date.text = dict_metatdata.get("date")
                uploader = SubElement(_metadata, "uploader")
                uploader.text = dict_metatdata.get("uploader")
                addeddate = SubElement(_metadata, "addeddate")
                addeddate.text = dict_metatdata.get("addeddate")
                pick = SubElement(_metadata, "pick")
                pick.text = dict_metatdata.get("pick")
                updateddate = SubElement(_metadata, "updateddate")
                updateddate.text = dict_metatdata.get("updateddate")
                adder = SubElement(_metadata, "adder")
                adder.text = dict_metatdata.get("adder")
                updater = SubElement(_metadata, "updatater")
                updater.text = dict_metatdata.get("updater")        
                notes = SubElement(_metadata, "notes")
                notes.text = dict_metatdata.get("notes")
                lineage = SubElement(_metadata, "lineage")
                lineage.text = dict_metatdata.get("lineage")        
                venue = SubElement(_metadata, "venue")
                venue.text = dict_metatdata.get("venue")
                stream_only = SubElement(_metadata, "stream_only")
                stream_only.text = dict_metatdata.get("stream_only")
                discs = SubElement(_metadata, "discs")
                discs.text = dict_metatdata.get("discs")
                has_mp3 = SubElement(_metadata, "has_mp3")
                has_mp3.text = dict_metatdata.get("has_mp3")
                shndiscs = SubElement(_metadata, "shndiscs")
                shndiscs.text = dict_metatdata.get("shndiscs")
                public = SubElement(_metadata, "public")
                public.text = dict_metatdata.get("public")
                publisher = SubElement(_metadata, "publisher")
                publisher.text = dict_metatdata.get("publisher")
                taper = SubElement(_metadata, "taper")
                taper.text = dict_metatdata.get("taper")
                transferrer = SubElement(_metadata, "transferrer")
                transferrer.text = dict_metatdata.get("transferrer")
               
                ET(_metadata).write( dict_metatdata.get("identifier"), encoding='UTF-8')
            except:
                traceback.print_exc()
                            
        @classmethod
        def uploadFile (self, filetosend):
            print 'logging in '
            ftp= ftplib.FTP()
            ftp.connect('www.tregaskis.org', '')
            print ftp.getwelcome()
            print '---------------'
            try:
                try:
                    print 'in try block'
                    ftp.login(ArchiveOrgHandler.instance._username, ArchiveOrgHandler.instance._password)
                    print 'logged in'
                    print 'currently in ' + ftp.pwd()
                    ftp.cwd('/web/code')
                    fullname = filetosend
                    name = os.path.split(fullname)[1]
                    f = open(fullname, "rb")
                    ftp.storbinary('STOR ' + name, f)
                    f.close()
                    print "ok"
                    print "Files:"
                    print ftp.retrlines('LIST')
                finally:
                    print "Quitting..."
                    ftp.quit()
            except:
                traceback.print_exc()
            #session=ftplib.FTP('85.233.160.70', 'tregaskis.org', 'trouble')
            #f=open(filetosend,'rb')
            #session.storbinary('STOR metadata.xml',f)
            #f.close()
            #session.quit()
            
            print ('finished ftp')
    
        @classmethod
        def tester ( self ):
            ArchiveOrgHandler.instance.writeMetadataXml(ArchiveOrgHandler.instance.MetaDataSettings)
            ArchiveOrgHandler.instance.writeFileXml(ArchiveOrgHandler.instance.MetaDataSettings)
    
        @classmethod
        def iter (self):
            keys= self.MetaDataSettings.keys()
            for x in keys:
                    print x, "-->", self.MetaDataSettings[x]
    
        
        
            
############################################################################
# username and password to be included here
x=ArchiveOrgHandler( "xxxxxxxx", "xxxxxx"  )
#x.tester
x.instance.tester()
x.instance.tester()
x.instance.uploadFile('/home/james/workspace/trunk/src/nowandnext/mymetadata.xml')
x.instance.uploadFile('/home/james/workspace/trunk/src/nowandnext/mymetadata.xml')
#x.iter()
#x.uploadFile('/home/james/workspace/trunk/src/nowandnext/mymetadata.xml' )
#x.uploadFile('/home/james/workspace/trunk/src/nowandnext/myFileData.xml' )



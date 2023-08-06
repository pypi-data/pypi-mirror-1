"""
$Id: generator.py 1632 2006-09-03 03:19:13Z hazmat $

A code and configuration generator for default mime registrations
with annotatable thingies
"""
import interfaces as i
import os

file_template = """
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:ore="http://namespaces.objectrealms.net/ore">
    %s
</configure>
"""
    
mime_template = """
   <ore:mimetype
        mimetype="%(mimetype)s" """


def generate( mime_files, outfile ):
    conf_file = open( outfile, 'w+')

    configs = []
    mimes = []
    for f in mime_files:
        if not os.path.exists( f ):
            continue
        fh = open( f )
        fs = fh.read()
        type_info = [ info for info in
                      [l.split() for l in fs.splitlines() if l.strip() and not l.startswith('#')]
                      if len(info) > 1 ]
        mimes.extend( type_info )

    for m in mimes:
        mimetype = m[0]
        m = root.get( mimetype )

        if not m:
            m = default_mime.clone( mimetype=mimetype )
        else: # major modes need mime reset
            m = m.clone( mimetype= mimetype )
            
        templates = []
        
        if 'icon' in m.options:
            templates.append( '\n        icon="%(icon)s"' )

        if 'adapter' in m.options:
            templates.append( '\n        adapter="%(adapter)s"')

        if 'interface' in m.options:
            templates.append( '\n        interface="%(interface)s"')

        templates.append('\n        />\n')
        templates.insert( 0, mime_template )
        template = ''.join( templates )
        
        mconf = template%m.options
        configs.append( mconf )

    config = ''.join( configs )
    conf = file_template%config
    conf_file.write( conf )
    conf_file.close()
    
class MimeRoot( object ):
    def __init__(self):
        self._m = {}
        
    def __setitem__(self, n, m):
        self._m[n] = m

    def get( self, mime_type ):
        major, minor = mime_type.split('/')
        return self._m.get(mime_type, self._m.get( major, None ) )
        
root = MimeRoot()

class MimeNode( object ):

    def __init__( self, name="", **options ):
        self.name = name
        options['mimetype'] = name
        self.options = options
        root[ self.name ] = self

    def __getattr__(self, name):
        try:
            return self.options[name]
        except KeyError:
            raise AttributeError(name)

    def clone( self, overrides={}, **kw ):
        overrides = overrides.copy()
        overrides.update( kw )
        if 'mimetype' in overrides:
            name = overrides['mimetype']
        else:
            name = self.name
        options = self.options.copy()
        options.update( overrides )
        return self.__class__( name, **options )
            
default_mime = MimeNode('')
#office_mime = MimeNode('', interface=i.OfficeContent )

m = MimeNode

#################################
# Definitions
#################################

# define icons for common types
icon_doc = '/++resource++mimeicons/doc.png'
icon_present = "/++resource++mimeicons/present.png"
icon_office = "/++resource++mimeicons/office.png"
icon_spread = "/++resource++mimeicons/spreadsheet.png"
icon_pdf = "/++resource++mimeicons/pdf.png"
icon_xml = "/++resource++mimeicons/xml.png"
icon_archive = "/++resource++mimeicons/archive.png"
icon_audio = "/++resource++mimeicons/audio.png"
icon_video = "/++resource++mimeicons/video.png"
icon_image = "/++resource++mimeicons/image.png"

#icon_cal   = "++resource++ical.png"
#icon_vcard = "++resource++vcard.png"

m('application/msword', icon=icon_doc )
m('application/vnd.ms-powerpoint', icon=icon_present )
m('application/vnd.ms-office', icon=icon_office )
m('application/vnd.ms-excel', icon=icon_spread )
m('application/xml', icon=icon_xml )
m('application/pdf', icon=icon_pdf )
m('application/zip', icon=icon_archive )
m('application/x-tar', icon=icon_archive )
m('application/x-gtar', icon=icon_archive )

m('image', icon=icon_image )
m('video', icon=icon_video )
m('audio', icon=icon_audio )
m('application/ogg',icon=icon_audio )

# open office document formats
for dtype, dicon in ( ('text', icon_doc ),
                      ('spreadsheet', icon_spread ),
                      ('presentation', icon_present ),
                      ):
    m('application/vnd.oasis.opendocument.'+dtype, icon=dicon )

# staroffice and oov1
for dtype, dicon in ( ('writer', icon_doc ),
                      ('calc', icon_spread ),
                      ('impress', icon_present )
                      ):
    m('application/vnd.sun.xml.'+dtype, icon=dicon )    




#m('application/vnd.ms-powerpoint', icon="++resource++present.png", **office_mime.options )
#m('application/vnd.ms-office', icon="++resource++office.png", **office_mime.options )

# define source types transforms
for i in ['x-python',
          'x-tcl',
          'x-ruby',
          'x-java',
          'x-c++src',
          'x-c++hdr',
          'x-boo',
          'x-latex',
          'x-troff',
          'x-bibtext']:
    pass


#m('application/msword', icon='++resource++word.png', **office_mime.options )
#m('application/vnd.ms-powerpoint', icon="++resource++present.png", **office_mime.options )
#m('application/vnd.ms-office', icon="++resource++office.png", **office_mime.options )
#m('video', interface = i.IVideoContent )
#m('audio', interface = i.IAudioContent )


if __name__ == '__main__':
    generate( ['/etc/mime.types'], 'mimetypes.zcml')    

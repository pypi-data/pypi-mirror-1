
When collective.collage.easyslider is installed dependencies are installed,

    >>> 'collective.collage.easyslider' in [i['title'] for i in portal.portal_quickinstaller.listInstalledProducts()]
    True
    >>> 'collective.easyslider' in [i['title'] for i in portal.portal_quickinstaller.listInstalledProducts()]
    True

    >>> #self.ipython(locals())
    
XXX: fix this...
    >>> 'Collage' in [i['title'] for i in portal.portal_quickinstaller.listInstalledProducts()]
    True
    
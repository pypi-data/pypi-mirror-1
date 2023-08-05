import doctest

def suite():
    return doctest.DocFileSuite('views.txt', 
                                'templatetags.txt',
                                'shortcuts.txt',
                                'setup.txt',
#                                 'settings.txt',
#                                 'shortcuts.txt',
                                package='kss.django',
                                optionflags=doctest.ELLIPSIS)

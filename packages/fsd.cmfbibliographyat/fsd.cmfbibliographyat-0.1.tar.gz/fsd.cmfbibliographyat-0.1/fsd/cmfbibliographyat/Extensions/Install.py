# -*- coding: utf-8 -*-

__author__ = """Andreas Jung <info@zopyx.com>"""
__docformat__ = 'plaintext'

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName


def install(self, reinstall=False):
    """ External Method to install FacultyStaffDirectory """
    
    out = StringIO()
    print >> out, "Installation log of fsd.cmfbibliographyat"

    # CMFBibliography integration:
    # making BibliographyFolder available on the FSD and person level
    try:
        import Products.CMFBibliographyAT
        have_cmfbib_at = True
    except ImportError:
        have_cmfbib_at = False

    if have_cmfbib_at:
        pt = getToolByName(self, 'portal_types', None)
        for name in ('FSDPerson', 'FSDFacultyStaffDirectory'):
            types = list(getattr(pt, name).allowed_content_types)
            types.append('BibliographyFolder')
            getattr(pt, name).allowed_content_types = types

        # Add person_publications_view to BibFolder
        vm = list(pt.BibliographyFolder.view_methods)
        vm.append('person_publications_view')
        pt.BibliographyFolder.view_methods = vm

    return out.getvalue()


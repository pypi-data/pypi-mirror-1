##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Compile gettext catalogs from .po files.
"""

import os
import logging
import zc.buildout
from pythongettext.msgfmt import Msgfmt

class PoFile(object):
    """Helper class to extract metadata from a PO File."""
    
    def __init__(self, filename):

        self.filename = filename
        self.header = {}
        
        # read the header lines
        for line in file(self.filename,'r'):
            line = line.strip()
            
            if not(line):
                
                if self.header != {}:
                    # bail when we hit the first blank after parsing the header
                    break
                
                else:
                    # pass over blank lines that occur before header metadata
                    continue

            if line[0] == line[-1] == '"':
                # this is a metadata line
                try:
                    key, value = line[1:-1].split(':', 1)
                except ValueError:
                    continue
                
                self.header[key.strip().replace(r'\n', '')] = \
                                         value.strip().replace(r'\n','')
        
    @property
    def domain(self):
        return self.header['Domain']

    @property
    def language(self):
        return self.header['Language-code']
    
class MsgFmtRecipe:

    def __init__(self, buildout, name, options):

        self.name, self.buildout, self.options = buildout, name, options
        
        # perform sanity checking on parameters
        if 'po_path' not in options:
            # no po_path provided; use our default
            options['po_path'] = os.path.join(
                buildout['buildout']['directory'], 'i18n')
            logging.getLogger(name).info(
                "No source path for .po files specified; using %s",
                options['po_path'])
        else:
            # make sure the path is absolute
            options['po_path'] = os.path.abspath(options['po_path'])

        if 'mo_path' not in options:
            # no mo_path provided; use our default
            options['mo_path'] = os.path.join(
                buildout['buildout']['directory'], 'locales')
            logging.getLogger(name).info(
                "No target path for .mo files specified; using %s",
                options['mo_path'])
        else:
            # make sure the path is absolute
            options['mo_path'] = os.path.abspath(options['mo_path'])


        # make sure mo_path and po_path exist
        if not(os.path.exists(options['po_path'])):
            logging.getLogger(name).error(
                "Specified po_path %s does not exist.",
                options['po_path'])

            raise zc.buildout.UserError("Invalid path.")

        if not(os.path.exists(options['mo_path'])):
            logging.getLogger(name).warn(
                "Specified mo_path %s does not exist; attempting to create.",
                options['mo_path'])
            os.makedirs(options['mo_path'])

    def install(self):
        """Scan the po_path for .po files and compile them using msgfmt."""

        paths = []
        
        for dirpath, dirname, filenames in os.walk(self.options['po_path']):

            for po_fn   in filenames:
                if po_fn[-3:] != '.po': continue

                po_file = PoFile(os.path.join(dirpath, po_fn))
                
                mo_fn = os.path.join(self.options['mo_path'], po_file.language,
                                     'LC_MESSAGES', '%s.mo' % po_file.domain)
                if not(os.path.exists(os.path.dirname(mo_fn))):
                    os.makedirs(os.path.dirname(mo_fn))
                
                # run msgfmt for each .po file
                file(mo_fn, 'wb').write(Msgfmt(po_file.filename).get())
                paths.append(mo_fn)
                
        return paths

    # XXX: Update should really check timestamps or something smart like that
    update = install

    

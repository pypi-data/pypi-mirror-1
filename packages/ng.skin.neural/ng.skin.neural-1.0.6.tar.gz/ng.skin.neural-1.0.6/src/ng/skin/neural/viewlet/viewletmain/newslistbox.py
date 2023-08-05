# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: newslistbox.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49797 $"
__date__    = "$Date: 2008-01-30 01:52:29 +0300 (Срд, 30 Янв 2008) $"


from mainbox import MainBox


class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"

    @property
    def values(self) :
        ls = self.folder.values()[-10:]
        ls.reverse()
        return ls                


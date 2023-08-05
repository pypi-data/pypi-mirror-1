# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: newslistbox.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__    = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"


from mainbox import MainBox


class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"

    @property
    def values(self) :
        ls = self.folder.values()[-10:]
        ls.reverse()
        return ls                


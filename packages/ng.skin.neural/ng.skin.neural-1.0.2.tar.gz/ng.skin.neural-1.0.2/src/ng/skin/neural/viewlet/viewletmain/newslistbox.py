# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: newslistbox.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__    = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"


from mainbox import MainBox


class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"

    @property
    def values(self) :
        ls = self.folder.values()[-10:]
        ls.reverse()
        return ls                


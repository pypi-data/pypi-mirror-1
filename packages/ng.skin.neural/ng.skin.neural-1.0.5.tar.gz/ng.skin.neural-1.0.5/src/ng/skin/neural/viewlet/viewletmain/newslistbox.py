# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: newslistbox.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"


from mainbox import MainBox


class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"

    @property
    def values(self) :
        ls = self.folder.values()[-10:]
        ls.reverse()
        return ls                


# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: newslistbox.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
__date__    = "$Date: 2008-01-24 11:48:03 +0300 (Чтв, 24 Янв 2008) $"


from mainbox import MainBox


class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"

    @property
    def values(self) :
        ls = self.folder.values()[-10:]
        ls.reverse()
        return ls                


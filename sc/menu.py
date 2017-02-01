"""The SuttaCentral Menu.

Example:
    >>> import sc.menu
    >>> menu = sc.menu.get_menu()
    >>> len(menu)
    3
    >>> menu[0].pitaka.name
    'Sutta'
    >>> menu[1].pitaka.name
    'Vinaya'
    >>> menu[1][2].lang.name
    'Sanskrit'
    >>> menu[1][2][0].sect.name
    'Mahāsaṅghika'
    >>> menu[1][2][0][1].name
    'Śrīghanācārasaṁgrahaṭīkā'
"""

from collections import namedtuple, OrderedDict

import sc.scimm

class Menu(list):
    pass

class PitakaMenu(list):
    def __init__(self, pitaka):
        self.pitaka = pitaka

class LanguageMenu(list):
    def __init__(self, lang):
        self.lang = lang


class SectMenu(list):
    def __init__(self, sect, divisions):
        self.sect = sect
        super().__init__(divisions)

def build_menu():
    """Build and return the SuttaCentral menu."""
    imm = sc.scimm.imm()
    menu = Menu()
    pitaka_menu = None
    lang_menu = None
    for collection in imm.collections.values():
        if not pitaka_menu or pitaka_menu.pitaka != collection.pitaka:
            pitaka_menu = PitakaMenu(collection.pitaka)
            menu.append(pitaka_menu)
        if not lang_menu or lang_menu.lang != collection.lang:
            lang_menu = LanguageMenu(collection.lang)
            pitaka_menu.append(lang_menu)
        sect_menu = SectMenu(collection.sect, collection.divisions)
        lang_menu.append(sect_menu)
    return menu


_menu = None
def get_menu():
    """Return the cached SuttaCentral menu."""
    global _menu
    if _menu is None:
        _menu = build_menu()
    return _menu



    
    
    
    
    
    
    
    

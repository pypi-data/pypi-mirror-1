#!/usr/bin/env python
# encoding: utf-8

############################################################################
#    Copyright (C) 2007 by Achim Zien und Arne Babenhauserheide            #
#    arne_bab@web.de                                                       #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

# Wir müssen tags parsen können. 
import tag_zu_objekt

# Außerdem müssen wir Pfade Plattformunabhängig verbinden können. 
from os.path import join

# Wir brauchen noch den Nutzerordner. 
from user import home

BASISORDNER = home

TRENNER_ORDNER = '/'
TRENNER_VERSION = '-'
TRENNER_JAHR = '-'
TRENNER_URL = '-'
ENDUNG_DATEI = '.yml'

class Datei(): 
    def __init__(self, tag="tag:1w6.org,2007:Menschen", kategorie="Vorlagen", version="0.1", speicherordner_rel_zu_home=".amov"):
        self.tag = tag
        self.kategorie = kategorie
        self.version = version
        self.basisordner = join(BASISORDNER, speicherordner_rel_zu_home)
        self.tag_zum_objekt = tag_zu_objekt.tag_zu_objekt(self.tag)
        self.tag_objekt = self.tag_zum_objekt.tag_objekt()

    def dateipfad(self): 
        return join(self.basisordner, self.kategorie)
    
    def dateiname_ohne_version_und_pfad(self): 
        dateiname_ohne_version_und_pfad = self.tag_objekt['Name'] + TRENNER_URL + self.tag_objekt['URL'] + TRENNER_JAHR + self.tag_objekt['Jahr']
        return dateiname_ohne_version_und_pfad

    def dateiname_ohne_version(self): 
        dateiname_ohne_version = join(self.dateipfad(), self.dateiname_ohne_version_und_pfad())
        return dateiname_ohne_version

    def dateiname_ohne_version_mit_trenner(self): 
        return self.dateiname_ohne_version() + TRENNER_VERSION

    def dateiname_ausgeben(self): 
        # Mit dem Tag_objekt und dem Eingabe-Wörterbuch können wir nun den Datei-String erzeugen. 
        datei = self.dateiname_ohne_version_mit_trenner() + str(self.version) + ENDUNG_DATEI
        return datei

#### Self-Test ####

if __name__ == "__main__": 
    datei = Datei(tag="tag:1w6.org,2007:Menschen", kategorie="Vorlagen", version="0.1")
    print datei.dateiname_ausgeben()
    print datei.dateiname_ohne_version_mit_trenner()
    print datei.dateiname_ohne_version()

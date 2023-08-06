#!/bin/env python
# encoding: utf-8

# Charakterverwaltung - Verwalte Charaktere im lesbaren YAML Format
# Copyright © 2007 - 2007 Arne Babenhauserheide

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

"""Manage Versions of saved objects. 

This class gets a tag and a cathegory and returns the full ID (including the version). Likely it will mostly be used to retrieve the most recent Version. """

#### Imports ####

import os

# Um die Dateien zu laden, nutzen wir die Objekt-Klasse. 
import Skripte.Kernskripte.ein_und_ausgabe.tag_zu_datei_von_tag as tag_zu_datei

#### Imports ####

#### Constants ####

TRENNER_ORDNER = "/"

#### Constants ####

#### Classes ####

class Versionen: 
    """Manage Versions. 
    
    ToDo: Rewrite, so that data about the file-path is taken from an ID object again (self.finde_neuste_datei())."""
    def __init__(self, tag=u"tag:1w6.org,2007:Menschen", kategorie=u"Armeen"): 
        #: the unique identifier for content, barring the cathegory. 
        self.tag = tag 
        #: The type of objekt we want to retrieve. 
        self.kategorie = kategorie 
        #: The ID including the most recent version of the objekt. 
        self.neuste = self.neuste_version() 
        #: The filepacth to the file with the most recent version. ToDo: Check and Remove, since this breaks the levels, which state that on this level only tag strings and ID dicts should be exchanged. 
        self.neuste_datei = self.lade_neuste_datei()

    def liste_quelldateien_auf(self, name, pfad): 
        result_list = []
        # print "name =", name, ", pfad =", pfad
        # list all files. 
        if not os.path.isdir(pfad): 
            os.makedirs(pfad)
        for i in os.listdir(pfad):
            # If the file begins with the name and ends with ".yml" add it to the list of matching files. 
            if i.find(name, 0, len(name)) != -1 and i[-4:] == ".yml":
                result_list.append(pfad + TRENNER_ORDNER + i) # TODO: Use os.path.join()
        return result_list

    def finde_neuste_datei(self, tag, pfad):
        """Return the YAML file (suffix: ".yml") in path which begins with name which has the highest version number (sorted by [].sort )."""
        datei = tag_zu_datei.Datei(tag=tag, kategorie=pfad)
        name = datei.dateiname_ohne_version_und_pfad()
        result_list = self.liste_quelldateien_auf(name, pfad)
        #: Die neuste Datei. Wenn es keine Datei gibt: False
        neuste_datei = False
        # return the one with the highest version number (major.minor) from the list of matching files. 
        #: A list containing the filepath and the major and minor versions of each file. 
        versions_list = []
        # create a versions array which contains the file path, the major versiona nd the minor version. 
        for i in result_list: 
            #: The major version of the object
            hauptversion = self.hauptversion(self.version_von_pfad(i))
            #: the minor version of the object
            unterversion = self.unterversion(self.version_von_pfad(i))
            versions_list.append((i, hauptversion, unterversion))
        # find the file with the highest version by comparing all against a highest version array and recording always the highest version. 
        #: The highest recorded version (major.minor). 
        hoechste_version = [0,0]
        for i in versions_list: 
            # if the major version is higher than the last recorded major version, this is the most recent file and we set et as neuste_datei. 
            if i[1] > hoechste_version[0]: 
                hoechste_version[0] = i[1]
                #: The most recent file. 
                neuste_datei = i[0]
            # if the major version is equal to the highest recorded major and the minor versino is higher than the last recorded minor version, set this as the most recent file. 
            elif i[1] == hoechste_version[0] and i[2] > hoechste_version[1]: 
                hoechste_version[1] = i[2]
                neuste_datei = i[0]
        if neuste_datei: 
            return neuste_datei
        else: 
            return False
    
    def lade_neuste_datei(self): 
        """Return the most recent file (by versionnumber) which matches tag and ID."""
        #: The most recent file
        neuste_datei = self.finde_neuste_datei(self.tag, self.kategorie)
        return neuste_datei
    
    def neuste_version(self):
        """return the most recent version in an ID dict."""
        #: The ID dict
        ID = {}
        ID[u"ID"] = self.tag
        ID[u"Kategorie"] = self.kategorie
        neuste_datei = self.lade_neuste_datei()
        # Set the range we found in the version-part of the filename as version. If no file exists yet, use Version 0.0
        if neuste_datei: 
            ID[u"Version"] = self.version_von_pfad(neuste_datei)
        else: 
            ID[u"Version"] = 0.0
        return ID
        
    def version_minor_eins_hoeher(self): 
        """return an ID with a minor version 1 higher than any already existing file."""
        # First get the most recent ID
        ID = self.neuste_version()
        # Then get the version
        version = ID[u"Version"]
        # Now get the major and minor version
        hauptvers = self.hauptversion(version)
        untervers = self.unterversion(version)
        # Increment the minor versino by 1
        untervers += 1
        # construct the version again
        version = str(hauptvers) + "." + str(untervers)
        # And change the ID
        ID[u"Version"] = version
        # And return it. 
        return ID
        
    
    def version_von_pfad(self, pfad): 
        """Return the version of the file whoose path was referenced."""
        # Check every char backwards from the suffix, if it is a number or a dot. 
        i = -4
        while self.is_number(pfad[i]) or pfad[i] == ".": 
            i-= 1
        return pfad[i+1:-4]

    def hauptversion(self, version): 
        """Return the major version number."""
        vers = str(version)
        i = 0
        while self.is_number(vers[i]): 
            i += 1
        return int(vers[:i])

    def unterversion(self, version): 
        """Return the major version number."""
        vers = str(version)
        i = -1
        while self.is_number(vers[i]): 
            i -= 1
        return int(vers[i+1:])
    
    def is_number(self, i): 
        """Test if the provided char/string/int is a number."""
        for j in str(range(10)): 
            if i == j: 
                return True
        return False
        
        

#### Classes ####

#### Self-Test ####

if __name__ == "__main__": 
    from yaml import dump
    versionen = Versionen()
    print "Datei:", versionen.neuste_datei
    print "ID:\n", dump(versionen.neuste, default_flow_style=False)

#### Self-Test ####

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#       Copyright (C) 2008 GFORGX <gforgx@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.Built on Wed Dec 19 19:43:57 2007.

__version__   = "0.9"
__date__      = "2008/03/25"
__author__    = "GFORGX (gforgx@gmail.com)"
__copyright__ = "Copyright 2008, GFORGX"
__license__   = "GPL"

import os, string
#TODO: port import()
#from shutil import copy
from time import localtime

today = str(localtime()[0]) + '-' + str(localtime()[1]) + '-' + str(localtime()[2])
path = os.path.expanduser('~/Notes/Date')
tag_path = os.path.expanduser('~/Notes/Tag')

class Note:
    def __init__(self, name):
        self.name = name

    def getDate(self):
        ''' Returns creation date of selected note '''
        for date in os.listdir(path):
            if os.path.exists(os.path.join(path, date, self.name)):
                return Date(date)
    
    def getPath(self):
        ''' Returns file path for selected note '''
        ''' Returns creation date of selected note '''
        for date in os.listdir(path):
            checkpath = os.path.join(path, date, self.name)
            if os.path.exists(checkpath):
                return checkpath

    def getText(self):
        text = None
        ''' Returns full text for selected note '''
        if self.getPath() !=None:
            file = open(self.getPath(), 'r')
            text = ''.join(file.readlines())
        return Text(text)

    def getTags(self):
        ''' Returns tags applied to selected note '''
        tags = []
        if self.getPath() != None:
            for tag in os.listdir(tag_path):
                if os.path.exists(os.path.join(tag_path, tag, self.name)):
                    tags.append(Tag(tag))
        return tags
    
    def getKeywords(self):
        ''' Returns list containing 5 most commonly used words in text '''
        keywords = []
        if self.getPath() != None:
            words = {}
            for line in open(self.getPath(), 'r'):
                line = string.strip(line, " \n")
                for word in line.split(" "):
                    try:
                        words[word] += 1
                    except KeyError:
                        words[word] = 1
            pairs = words.items()
            pairs.sort(lambda a, b: b[1]-a[1]) 
            for p in pairs[:5]:
                keywords.append(p[0])
        return keywords

    def remove(self):
        ''' Removes note and date/tag dirs if empty '''
        if self.getPath() != None:
            os.remove(self.getPath())
            self.getDate().remove()
            for tag in self.getTags():
                os.unlink(os.path.join(tag_path, tag.value, self.name))
                tag.remove()

    def write(self, text):
        ''' Writes some text to note '''
        if self.getPath() is None:
            Date(today).create()
            file = open(os.path.join(path, today, self.name), 'w')
            file.write(text)
            file.close()
        else:
            file = open(self.getPath(), 'w')
            file.write(text)
            file.close()

    def tag(self, tags):
        ''' Applies user given tags to note '''
        if self.getPath() != None:
            src = self.getTags()
            for tag in tags:
                try:
                    Tag(tag).create()
                    os.symlink(self.getPath(), os.path.join(tag_path, tag, self.name))
                except OSError:
                    pass
            for tag in src:
                if tag.value not in tags:
                    os.unlink(os.path.join(tag_path, tag.value, self.name))
                    tag.remove()

class Date:
    def __init__(self, date):
        self.value = date

    def getNotes(self):
        notes = []
        if self.value != None:
            date_dir = os.path.join(path, self.value)
            if os.path.exists(date_dir):
                for note in os.listdir(date_dir):
                    notes.append(Note(note))
        return notes
    
    def getNumber(self):
        return len(self.getNotes())
    
    def remove(self):
        date_dir = os.path.join(path, self.value)
        if os.path.exists(date_dir) and self.number == 0:
            os.rmdir(os.path.join(path, self.value))
    
    def create(self):
        date_dir = os.path.join(path, self.value)
        if not os.path.exists(date_dir):
            os.mkdir(date_dir)

class Tag:
    def __init__(self, tag):
        self.value = tag

    def getNotes(self):
        notes = []
        if self.value != None:
            tag_dir = os.path.join(tag_path, self.value)
            if os.path.exists(tag_dir):
                for note in os.listdir(tag_dir):
                    notes.append(Note(note))
        return notes
    
    def getNumber(self):
        return len(self.getNotes())

    def remove(self):
        tag_dir = os.path.join(tag_path, self.value)
        if os.path.exists(tag_dir) and self.number == 0:
            os.rmdir(tag_dir)
    
    def create(self):
        tag_dir = os.path.join(tag_path, self.value)
        if not os.path.exists(tag_dir):
            os.mkdir(tag_dir)

class Text:
    def __init__(self, text):
        self.value = text

    def getNotes(self):
        notes = []
        if self.value != None:
            for dir in os.listdir(path):
                for note in os.listdir(os.path.join(path, dir)):
                    if self.value in ''.join(open(os.path.join(path, dir, note)).readlines()):
                        notes.append(Note(note))
        return notes
    
    def getNumber(self):
        return len(self.getNotes())

class Search:
    def __init__(self, date, tag, text):
        self.date = date
        self.tag = tag
        self.text = text

    def getNotes(self):
        dateResults = Date(self.date).getNotes()
        tagResults = Tag(self.tag).getNotes()
        textResults = Text(self.text).getNotes()
        results = []
        if self.tag is None and self.text is None:
            for result in dateResults:
                results.append(result)
        elif self.date is None and self.text is None:
            for result in tagResults:
                results.append(result)
        elif self.date is None and self.tag is None:
            for result in textResults:
                results.append(result)
        elif self.date is None:
            for result in tagResults:
                if result in textResults:
                    results.append(result)
        elif self.tag is None:
            for result in dateResults:
                if result in textResults:
                    results.append(result)
        elif self.text is None:
            for result in dateResults:
                if result in tagResults:
                    results.append(result)
        else:
            for result in dateResults:
                if result in tagResults and result in textResults:
                    results.append(result)
        return results

    def getNumber(self):
        return len(self.getNotes())
#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import scriptures
import json
import random

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

bible = []

def readVerse(reference):
	with open('ESV.json') as data:
		bible = json.load(data)
	ref = scriptures.extract(reference) 
	if ref != []:
		print(ref)
		verse = bible[ref[0][0]][str(ref[0][1])][str(ref[0][2])]
		return verse
	else:
		return('This is not a valid reference')

def readPassage(reference):
	with open('ESV.json') as data:
		bible = json.load(data)
	ref = scriptures.extract(reference)
	print(ref)
	passage = ''
	if ref != []:
		print(ref)
		verse = ref[0][2]
		for chapter in range(ref[0][1],ref[0][3]+1):
			if chapter < ref[0][3]:
				while 1:
					try:
						passage+=bible[ref[0][0]][str(chapter)][str(verse)]
						passage+=' '
						verse+=1
					except:
						break
			else:
				while verse <= ref[0][4]:
					passage+=bible[ref[0][0]][str(chapter)][str(verse)]
					passage+=' '
					verse+=1
			chapter+=1
			verse = 1
		return passage
	else:
		return('This is not a valid reference')

def readRandomPassage_callback(hermes, intentMessage):
	with open('ESV.json') as data:
		bible = json.load(data)
	try:
		book = intentMessage.slots.book[0].slot_value.value.value
	except:
		books = bible.keys()
		book = books[random.randint(0,len(books))]
	try:
		chapter = intentMessage.slots.chapter[0].slot_value.value.value
	except:
		chapters = bible[book].keys()
		chapter = chapters[random.randint(0,len(chapters))]
	verses = bible[book][chapter].keys()
	verse = verses[random.randint(0,len(verses))]
	
	message = readPassage(book + " " + chapter + ":" + verse)
	hermes.publish_end_session(intentMessage.session_id, message)
	
def readPassage_callback(hermes, intentMessage):
	book = intentMessage.slots.book[0].slot_value.value.value
	if book in ('Jude', '3 John', 'Philemon'):
		verse = intentMessage.slots.chapter[0].slot_value.value.value
		chapter = 1.0
		second_chapter = 1.0
		try:
			second_verse = intentMessage.slots.verse[0].slot_value.value.value
		except:
			second_verse = verse
	else:
		chapter = intentMessage.slots.chapter[0].slot_value.value.value
		try:
			verse = intentMessage.slots.verse[0].slot_value.value.value
		except:
			verse = ''
		try:
			second_chapter = intentMessage.slots.chapter[1].slot_value.value.value
		except:
			second_chapter = ''
		try:
			second_verse = intentMessage.slots.verse[1].slot_value.value.value
		except:
			second_verse = ''
	reference = book + ' ' + str(int(chapter))
	if type(verse)==float:
		reference+=":" + str(int(verse))
	if type(second_chapter) ==  float:
		reference+="-" + str(int(second_chapter)) + ":"
	if type(second_verse)==float:
		if  type(second_chapter)!=float:
			reference+="-"
		reference+= str(int(second_verse))
	print(reference)
	message = readPassage(reference)
	hermes.publish_end_session(intentMessage.session_id, message)

if __name__=="__main__":
	with Hermes("localhost:1883") as h:
		h.subscribe_intent("toxip:readPassage",readPassage_callback) \
		 .subscribe_intent("toxip:readRandomPassage",readRandomPassage_callback) \
		 .start()

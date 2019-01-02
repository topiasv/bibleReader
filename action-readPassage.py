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

def changeBookName(book):
	if book[:2] == "I " or book[:2] == "1 ":
		return "first " + book[2:]
	elif book[:3] == "II " or book[:3] == "2 ":
		return "second " + book[3:]
	elif book[:4] == "III " or book[:4] == "III ":
		return "third " + book[4:]
	else:
		return book

def readRandomPassage_callback(hermes, intentMessage):
	with open('ESV.json') as data:
		bible = json.load(data)
	if intentMessage.slots.book:
		book = str(intentMessage.slots.book[0].slot_value.value.value)
		print("User book selected " + str(book))
	else:
		books = bible.keys()
		book = books[random.randint(0,len(books)-1)]
	if intentMessage.slots.chapter:
		chapter = str(int(intentMessage.slots.chapter[0].slot_value.value.value))
		print("User chapter selected " + str(int(chapter)))
	else:
		chapters = bible[book].keys()
		chapter = chapters[random.randint(0,len(chapters)-1)]
	verses = bible[book][chapter].keys()
	verse = verses[random.randint(0,len(verses)-1)]
	
	reference = "{} chapter {}, verse {}. ".format(changeBookName(str(book)), \
		str(chapter),str(verse))
	message = reference + readPassage(book + " " + chapter + ":" + verse)
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

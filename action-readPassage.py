#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import scriptures
import json
import random
import io
from dotmap import DotMap

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

bible = []
bibleIndex = []
cxtFileName = ""


# Context variable
cxt = DotMap()

class ChapterError(Exception):
	pass
class BookError(Exception):
	pass

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

def bookLen(book):
	return bibleIndex[book]["length"]

def chapterLen(book, chapter):
	if type(chapter) is not str:
		chapter = str(chapter)
	return bibleIndex[book][chapter]["length"]

def initContext(filename=None):
	if filename:
		print("Filename found")
		with open(filename) as data:
			print("Opening file")
			cxtJson = json.load(data)
			updateContext(cxtJson["book"],cxtJson["chapter"],cxtJson["verse"], \
						  cxtJson["chapter2"],cxtJson["verse2"])
	else:
		updateContext()

def updateContext(book='', chapter='', verse='', chapter2='', verse2=''):
	print("New context: {} {} {} {} {}".format(str(book),str(chapter),str(verse),str(chapter2),str(verse2)))
	cxt.book = str(book)
	if chapter == '':
		cxt.chapter = ''
	else:
		cxt.chapter = int(chapter)
	if verse == '':
		cxt.verse = ''
	else:
		cxt.verse = int(verse)
	if chapter != '' and chapter2 == '':
		cxt.chapter2 = int(chapter)
	elif chapter2 == '':
		cxt.chapter2 = ''
	else:
		cxt.chapter2 = int(chapter2)
	if verse != '' and verse2 == '':
		cxt.verse2 = int(chapter)
	elif verse2 == '':
		cxt.verse2 = ''
	else:
		cxt.verse2 = int(verse2)
	
	with open(cxtFileName, 'w') as data:
		print("Saving context file")
		json.dump(cxt, data)
	print("Context updated!")
	

def getNearPassages(direction, length, book, chapter, verse):
	newChapter, newVerse = getOffsetPassage(direction, 1, book, chapter, verse)
	if newChapter > bookLen(book):
		raise ChapterError(direction)
	elif newChapter < 1:
		raise ChapterError(direction)
	newChapter2, newVerse2 = getOffsetPassage(direction, length, book, chapter, verse)
	if direction == -1:
		return (book, newChapter2, newVerse2, newChapter, newVerse)
	else:
		return (book, newChapter, newVerse, newChapter2, newVerse2)

def getOffsetPassage(direction, length, book, chapter, verse):
	curChapterLen = chapterLen(book,chapter)
	if direction == -1:
		try:
			verseMod = chapterLen(book,chapter - 1)
		except:
			verseMod = chapterLen(book,chapter)
	elif direction == 1:
		verseMod = chapterLen(book,chapter)
	else:
		raise ValueError('Direction out of range')
	versesLeft = length
	while versesLeft > 0:
		if verse + length * direction > verseMod or \
		   verse + length * direction < 1:
			versesLeft -= chapterLen(book, chapter) - verse + 1
			chapter += direction
			if direction == -1:
				verse = verseMod
			elif direction == 1:
				verse = 1
			
			if chapter < 1:
				return (1, 1)
			elif chapter > bookLen(book):
				return (bookLen(book), chapterLen(book,chapter-1))
		else:
			verse += versesLeft	* direction
			versesLeft = 0
	return (chapter, verse)

def getAdjacentBook(direction, book):
	index = bibleIndex[book].index
	if index == 0 or index == 65:
		print "Book index out of range"
		return -1
	return bibleIndex.sections["Bible"].keys()[index + direction]

def readNextPassage_callback(hermes, intentMessage):
	if intentMessage.slots.passage_amount:
		passages = int(intentMessage.slots.passage_amount[0].slot_value.value.value)
	else:
		passages = 1
	if cxt.book == '' or cxt.chapter == '':
		message = "Sorry, I forgot what you were reading. Ask me a new one"
		hermes.publish_end_session(intentMessage.session_id, message)
		return None
	else:
		try:
			ref = getNearPassages(1, passages, cxt.book, cxt.chapter2, cxt.verse2)
			updateContext(*ref)
			message = readPassage(buildReference(*ref))
			hermes.publish_end_session(intentMessage.session_id, message)
		except ChapterError:
			message = "Reached the end of the book."
			hermes.publish_end_session(intentMessage.session_id, message)

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
	
	ref = "{} chapter {}, verse {}. ".format(changeBookName(str(book)), \
		str(chapter),str(verse))
	updateContext(book, chapter, verse, chapter, verse)
	message = ref + readPassage(book + " " + chapter + ":" + verse)
	hermes.publish_end_session(intentMessage.session_id, message)
	
def buildReference(book, chapter, verse='', second_chapter='', second_verse=''):
	reference = book + ' ' + str(int(chapter))
	if type(verse) == int:
		reference+=":" + str(int(verse))
	if type(second_chapter) == int and second_chapter != chapter:
		reference+="-" + str(int(second_chapter)) + ":"
	if type(second_verse) == int and second_verse != verse:
		if type(second_chapter) == int or second_chapter == chapter:
			reference+="-"
		reference+= str(int(second_verse))
	return reference

def readPassage_callback(hermes, intentMessage):
	book = intentMessage.slots.book[0].slot_value.value.value
	if book in ('Jude', '3 John', 'Philemon'):
		verse = int(intentMessage.slots.chapter[0].slot_value.value.value)
		chapter = 1
		second_chapter = 1
		try:
			second_verse = int(intentMessage.slots.verse[0].slot_value.value.value)
		except:
			second_verse = verse
	else:
		chapter = int(intentMessage.slots.chapter[0].slot_value.value.value)
		try:
			verse = int(intentMessage.slots.verse[0].slot_value.value.value)
		except:
			verse = ''
		try:
			second_chapter = int(intentMessage.slots.chapter[1].slot_value.value.value)
		except:
			second_chapter = ''
		try:
			second_verse = int(intentMessage.slots.verse[1].slot_value.value.value)
		except:
			second_verse = ''
	reference = buildReference(book, chapter, verse, second_chapter, second_verse)
	print(reference)
	updateContext(book, chapter, verse, second_chapter, second_verse)
	message = readPassage(reference)
	hermes.publish_end_session(intentMessage.session_id, message)

if __name__=="__main__":
	with open('bible-index2.json') as data:
		bibleIndex = json.load(data)
	cxtFileName = "context.json"
	initContext(cxtFileName)
	
	with Hermes("localhost:1883") as h:
		h.subscribe_intent("toxip:readPassage",readPassage_callback) \
		 .subscribe_intent("toxip:readRandomPassage",readRandomPassage_callback) \
		 .subscribe_intent("toxip:readNextPassage",readNextPassage_callback) \
		 .start()

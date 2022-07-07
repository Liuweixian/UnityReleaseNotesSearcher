#!/usr/bin/python
# -*- coding: UTF-8 -*
import sys
import os
import requests
from bs4 import BeautifulSoup
import codecs
from selenium import webdriver

url_prefix = 'https://docs.unity3d.com/ScriptReference/'
entry_url = url_prefix + 'index.html'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(R'/Users/liuweixian/Downloads/chromedriver',options=options)

def pull_class_list_from_module(url):
	module_url = url_prefix + url;
	print('pulling ... ' + module_url)
	browser.get(module_url)
	soup = BeautifulSoup(browser.page_source, 'lxml')
	classesBlock = None
	for k in soup.find_all('h3'):
		if k.text == 'Classes':
			classesBlock = k

	if classesBlock == None:
		return

	return classesBlock.parent.find_all('a')


def main():
	browser.get(entry_url)
	soup = BeautifulSoup(browser.page_source, 'lxml')
	scrollbarList = soup.find('div', id='customScrollbar')
	unityEngineList = None
	for k in scrollbarList.find_all('li'):
		spanTag = k.find('span')
		if spanTag and spanTag.text == 'UnityEngine':
			unityEngineList = k.find('ul')

	if unityEngineList == None:
		return

	aHrefList = None
	for k in unityEngineList.find_all('span'):
		if k and k.text == 'Assemblies':
			aHrefList = k.next_sibling

	if aHrefList == None:
		return

	for k in aHrefList.find_all('a'):
		class_list = pull_class_list_from_module(k['href'])
		for classInfo in class_list:
			print(classInfo)
		return

main()
#ull_class_list_from_module('UnityEngine.AIModule.html')
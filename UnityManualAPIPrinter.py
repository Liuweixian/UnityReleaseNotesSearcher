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
	module_url = url_prefix + url
	#print('pulling module ... ' + module_url)
	browser.get(module_url)
	soup = BeautifulSoup(browser.page_source, 'lxml')
	classesBlock = None
	for k in soup.find_all('h3'):
		if k.text == 'Classes':
			classesBlock = k

	if classesBlock == None:
		return

	return classesBlock.parent.find_all('a')

def pull_method_list_from_class(url):
	class_url = url_prefix + url
	#print('pulling class ... ' + class_url)
	browser.get(class_url)
	soup = BeautifulSoup(browser.page_source, 'lxml')
	method_list = []
	for k in soup.find_all('h3'):
		if k.text == 'Inherited Members':
			break

		if k.text == 'Public Methods' or k.text == 'Static Methods':
			method_block = k.parent.find_all('a')
			for methodInfo in method_block:
				method_list.append(methodInfo)
			continue

	return method_list;


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
		module_name = k.text
		class_list = pull_class_list_from_module(k['href'])
		if class_list == None:
			continue
		
		for classInfo in class_list:
			class_name = classInfo.text
			method_list = pull_method_list_from_class(classInfo['href'])
			for methodInfo in method_list:
				method_name = methodInfo.text
				print(module_name + "," + class_name + "," + method_name)

main()
#pull_class_list_from_module('UnityEngine.AIModule.html')
#pull_method_list_from_class('AI.NavMeshAgent.html')

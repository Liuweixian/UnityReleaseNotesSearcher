#!/usr/bin/python
# -*- coding: UTF-8 -*
import sys
import os
import requests
import argparse
from bs4 import BeautifulSoup
import codecs

parser = argparse.ArgumentParser(description="e.g. Python UnityReleaseNotesSearcher.py -fv 2018.4.14 -tv 2019.4.4 -ss VideoPlayer")
parser.add_argument('-nc', '--noCache', default=False)
parser.add_argument('-fv', '--fromVersion', default='2017.1.0', required=True)
parser.add_argument('-tv', '--toVersion', default='2020.4.40')
parser.add_argument('-ss', '--searchString', nargs='+', required=True)
args = parser.parse_args()

def makesure_cache_dir_exist():
	cache_dir = os.getcwd() + "/cache"
	if not os.path.exists(cache_dir):
		os.makedirs(cache_dir)
	return cache_dir

def pull_and_save(file, version_url_postfix):
	release_notes_url = "https://unity3d.com" + version_url_postfix
	release_notes_response = requests.get(release_notes_url)
	if release_notes_response.status_code != 200:
		print('Cannot get response from ' + release_notes_url)
		return
	notes_soup = BeautifulSoup(release_notes_response.text, 'lxml')

	for k in notes_soup.find_all('ul'):
		if 'issuetracker' not in str(k):
			continue
		for j in k.find_all('p'):
			file.write(j.text.replace('\n', '').replace('\r', '') + "\n")

def main():
	patch_release_url = 'https://unity3d.com/get-unity/download/archive?_ga=1.53535144.1865728451.1487830397'
	patch_release_response = requests.get(patch_release_url)
	if patch_release_response.status_code != 200:
		print('Url is not valid:' + patch_release_url)
		return

	existing_version_list = []
	soup = BeautifulSoup(patch_release_response.text, 'lxml')
	for k in soup.find_all('a'):
		if k.string == 'Release notes':
			existing_version_list.append(k['href'])

	existing_version_count = len(existing_version_list)
	startIndex = existing_version_count - 1
	endIndex = 0

	for index in range(existing_version_count):
		if args.fromVersion in existing_version_list[index]:
			startIndex = index
		if args.toVersion in existing_version_list[index]:
			endIndex = index

	print('Searching from ' + existing_version_list[startIndex] + ' to ' + existing_version_list[endIndex])

	cache_dir = makesure_cache_dir_exist()
	for index in range(startIndex, endIndex - 1, -1):
		version_url_postfix = existing_version_list[index]
		version = version_url_postfix[version_url_postfix.rindex("/") + 1 : ];
		version_file = cache_dir + "/" + version + ".txt"
		exist_version_file = os.path.exists(version_file)
		if args.noCache or not exist_version_file:
			file = codecs.open(version_file, "w", 'utf-8')
			pull_and_save(file, version_url_postfix)
			file.close()

		file = codecs.open(version_file, "r", 'utf-8')
		line = file.readline()
		content_result = ''
		while line:
			for search_string in args.searchString:
				if search_string in line:
					content_result += "\t*" + line
			line = file.readline()

		if content_result != '':
			print('release notes of ' + version + ':')
			print(content_result)
		file.close()

main()
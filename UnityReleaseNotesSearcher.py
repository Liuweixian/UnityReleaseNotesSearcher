#!/usr/bin/python
# -*- coding: UTF-8 -*
import sys
import requests
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="e.g. Python UnityReleaseNotesSearcher.py -fv 2018.4.14 -tv 2019.4.4 -ss VideoPlayer")
parser.add_argument('-fv', '--fromVersion', default='2017.1.0', required=True)
parser.add_argument('-tv', '--toVersion', default='2020.4.40')
parser.add_argument('-ss', '--searchString', nargs='+', required=True)
args = parser.parse_args()

def main():
	patch_release_url = 'https://unity3d.com/get-unity/download/archive?_ga=1.53535144.1865728451.1487830397'
	patch_release_response = requests.get(patch_release_url)
	if patch_release_response.status_code != 200:
		print 'Url is not valid:' + patch_release_url
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

	print 'Searching from ' + existing_version_list[startIndex] + ' to ' + existing_version_list[endIndex]

	for index in range(startIndex, endIndex - 1, -1):
		#print 'Searching release notes of ' + existing_version_list[index]
		release_notes_url = "https://unity3d.com" + existing_version_list[index]
		release_notes_response = requests.get(release_notes_url)
		if release_notes_response.status_code != 200:
			print 'Cannot get response from ' + release_notes_url
			continue
		notes_soup = BeautifulSoup(release_notes_response.text, 'lxml')
		content_result = ''
		for k in notes_soup.find_all('ul'):
			if 'issuetracker' not in str(k):
				continue
			for j in k.find_all('p'):
				for search_string in args.searchString:
					if search_string in j.text:
						content_result += '\t*' + j.text.replace('\n', '').replace('\r', '') + '\r\n'
		if content_result != '':
			print 'release notes of ' + existing_version_list[index] + ':'
			print content_result

main()
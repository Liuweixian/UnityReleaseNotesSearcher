#!/usr/bin/python
# -*- coding: UTF-8 -*
import sys
import os
import requests
import argparse
from bs4 import BeautifulSoup
import codecs
import time
import re

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
	release_notes_url = f'https://unity.com/cn/releases/editor/whats-new/{version_url_postfix}#notes'

	start_time = time.time()
	release_notes_response = requests.get(release_notes_url)
	if release_notes_response.status_code != 200:
		print('Cannot get response from ' + release_notes_url)
		return

	print(f'Finish get release note for {version_url_postfix}, cost:{time.time() - start_time}s')
	notes_soup = BeautifulSoup(release_notes_response.text, 'lxml')
	for k in notes_soup.find_all('script'):
		if '### Known Issues' not in k.text:
			continue
		final_notes = k.text.replace('self.__next_f.push([1,"', '')
		final_notes = final_notes[:-3]
		final_notes = final_notes.replace('\\n', '\n')
		file.write(final_notes)

def version_info_convertor(version_info):
	return version_info.replace('\\"unityhub://', '')

def version_info_sort(version_info):
	num_list = version_info.split('.')
	ret = int(num_list[0]) * 10000 + (int(num_list[1]) + 1) * 100 + int(num_list[2])
	return ret

def main():
	need_fetch_version = False
	patch_release_file_cache = 'patch_release_url.html'

	if os.path.exists(patch_release_file_cache):
		modification_time = os.path.getmtime(patch_release_file_cache)
		need_fetch_version = (time.time() - modification_time) > 24 * 60 * 60
	else:
		need_fetch_version = True;

	if need_fetch_version:
		patch_release_url = 'https://unity.com/cn/releases/editor/archive'
		print('Getting all release version from ' + patch_release_url)
		start_time = time.time()
		patch_release_response = requests.get(patch_release_url)
		if patch_release_response.status_code != 200:
			print('Url is not valid:' + patch_release_url)
			return
		print(f'Finish request url, cost:{time.time() - start_time}s')
		fo = open(patch_release_file_cache, 'w')
		text = fo.write(patch_release_response.text)
		fo.close()

	#open the cache file to read all the version
	fo = open(patch_release_file_cache, 'r')
	version_cache_text = fo.read()
	fo.close()

	#use pattern to get all the version
	search_pattern = '\\\\"unityhub://\\d*\\.\\d\\.\\d*'
	existing_version_list = re.findall(search_pattern, version_cache_text)
	#remove prefix for each string in list
	existing_version_list = list(map(version_info_convertor, existing_version_list))
	#sort all the version
	existing_version_list = sorted(existing_version_list, key=version_info_sort)
	#remove duplicate
	existing_version_list = list(dict.fromkeys(existing_version_list))

	existing_version_count = len(existing_version_list)
	startIndex = 0
	endIndex = existing_version_count - 1
	for index in range(existing_version_count):
		if args.fromVersion in existing_version_list[index]:
			startIndex = index
		if args.toVersion in existing_version_list[index]:
			endIndex = index
	print('Searching from ' + existing_version_list[startIndex] + ' to ' + existing_version_list[endIndex])

	cache_dir = makesure_cache_dir_exist()

	for index in range(startIndex, endIndex + 1, 1):
		version_url_postfix = existing_version_list[index]
		version_file = cache_dir + "/" + version_url_postfix + ".html"
		exist_version_file = os.path.exists(version_file)
		if exist_version_file:
			version_file_stat = os.stat(version_file)
			exist_version_file = version_file_stat.st_size > 0
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
				if search_string.lower() in line:
					content_result += "\t*" + line
				if search_string.upper() in line:
					content_result += "\t*" + line
			line = file.readline()

		if content_result != '':
			print('release notes of ' + version_url_postfix + ':')
			print(content_result)
		file.close()

main()
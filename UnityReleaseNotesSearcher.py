#!/usr/bin/python
# -*- coding: UTF-8 -*
import sys
import requests

def GetResponseFromUnityDotCom(versionString):
	curUrl1 = "https://unity3d.com/unity/whats-new/unity-" + versionString
	r = requests.get(curUrl1)
	if r.status_code != 200:
		curUrl2 = "https://unity3d.com/unity/whats-new/" + versionString
		r = requests.get(curUrl2)
		
	if r.status_code != 200:
		print 'Can not find ' + versionString + ' Checked Urls: ' + curUrl1 + ' ' + curUrl2
		return None
	return r

class UnityVersion(object):
	def __init__(self, versionString):
		self.versionNums = []
		versionStringArray = versionString.split(".")
		if len(versionStringArray) != 3:
			print 'Invalid Version String:', versionString
			return

		for i in range(len(versionStringArray)):
			self.versionNums.append(int(versionStringArray[i]))

	def IsEqualOrNewer(self, unityVersion):
		selfLength = len(self.versionNums)
		tmpLength = len(unityVersion.versionNums)
		if selfLength != tmpLength:
			print 'lengths not equals:', selfLength, ' != ', tmpLength
			return False

		for i in range(selfLength - 1, -1, -1):
			if self.versionNums[i] < unityVersion.versionNums[i]:
				return False
		return True

	def GetResponse(self):
		versionString = ".".join(map(str, self.versionNums))
		if len(self.versionNums) != 3:
			print 'Invalid Version String:', versionString
			return None
		r = GetResponseFromUnityDotCom(versionString)
		return r

	def NextVersion(self):
		versionString = ".".join(map(str, self.versionNums))
		if len(self.versionNums) != 3:
			print 'Invalid Version String:', versionString
			return
		currentVersionString = str(self.versionNums[0]) + "." + str(self.versionNums[1]) + "." + str(self.versionNums[2] + 1)
		r = GetResponseFromUnityDotCom(currentVersionString)
		if r != None:
			self.versionNums[2] += 1
			return

		currentVersionString = str(self.versionNums[0]) + "." + str(self.versionNums[1] + 1) + "." + str(self.versionNums[2])
		r = GetResponseFromUnityDotCom(currentVersionString)
		if r != None:
			self.versionNums[1] += 1
			return

		currentVersionString = str(self.versionNums[0] + 1) + "." + str(self.versionNums[1]) + "." + str(self.versionNums[2])
		r = GetResponseFromUnityDotCom(currentVersionString)
		if r != None:
			self.versionNums[0] += 1
			return


def main():
	defaultFromVersion = UnityVersion("2017.1.1")
	defaultToVersion = UnityVersion("2020.4.40")
	if len(sys.argv) > 4:
		defaultFromVersion = UnityVersion(sys.argv[1])
		defaultToVersion = UnityVersion(sys.argv[2])
	elif len(sys.argv) == 4:
		defaultFromVersion = UnityVersion(sys.argv[1]) 

	defaultFromVersion.NextVersion()
	r = defaultFromVersion.GetResponse()
	'''while True:
		r = defaultFromVersion.GetResponse()
		if r == None:
			break
		if defaultFromVersion.IsEqualOrNewer(defaultToVersion):
			break
		defaultFromVersion.NextVersion()'''

main()
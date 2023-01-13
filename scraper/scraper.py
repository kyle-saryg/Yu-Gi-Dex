import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import time
import lxml
import pandas
import pickle

objSeenURL = {}
scraped = set()

def main():
	strSeed = "https://yugioh.fandom.com/wiki/Special:AllPages"
	intPageAmount = 10
	intStartTime = time.time()

	#create new directory to store all page files
	try:
		os.mkdir("./files")
	except OSError as error:
		print(error) 

	crawler(strSeed, intPageAmount)
	print("Crawler took ", time.time() - intStartTime, " to run")

def crawler(strSeed, intPageAmount):
	intCurrentPageNumber = 0
	strExtensionPrefix = "https://"
	strDocType = "text/html"

	#init queue with seed
	objMasterUrlQueue = set()
	objMasterUrlQueue.add(strSeed)

	#init set for all robots.txt links
	objRobotsLinks = set()

	while intCurrentPageNumber < intPageAmount:
		for url in objMasterUrlQueue:
			if len(url) >= 240: continue
			if "yugioh" not in url: continue
			if "tumblr" in url: continue
			if "reddit" in url: continue
			if "youtube" in url: continue
			if "google" in url: continue
			if "discord" in url: continue
			if "twitch" in url: continue
			if "archive" in url: continue
			if "forums" in url: continue
			if "twitter" in url: continue
			if "auth" in url: continue
			if "image" in url: continue
			if "login" in url: continue
			if "Template:" in url: continue
			if "blog" in url: continue
			if "steam" in url: continue
			if "facebook" in url: continue
			if "CreateAccount" in url: continue
			if "UserLogin" in url: continue
			if "edit" in url: continue
			if "CreatePage" in url: continue
			if "&oldid=" in url: continue

			#obey robots.txt
			strDomain = strExtensionPrefix + urlparse(url).netloc
			strRobotsUrl = strDomain + "/robots.txt"

			#scrape robots.txt if that domain has not been added previously
			if strRobotsUrl not in objRobotsLinks:
				try:
					strRobotsRawText = requests.get(strRobotsUrl).text
					strRobotsText = BeautifulSoup(strRobotsRawText, "lxml")
					strSplitRobots = str(strRobotsText).splitlines()

					for line in strSplitRobots:
						if "Disallow:" in line and len(line) > 11:
							strNewRobotsLink =  strDomain + line[10:]
							objRobotsLinks.add(strNewRobotsLink)
				except:
					print(f"{url} Has No Robots.txt")
					continue
			
			#make sure current url is not in robots.txt or has already been visited
			if url in objRobotsLinks or url in objSeenURL: continue

			print(f"Currently Crawling Page #: {intCurrentPageNumber}")
			print(url)
			print("----------------------------------------------------------")

			#get raw text from page
			try:
				strRawText = requests.get(url)
				if strRawText.status_code != 200: continue

				#get plain text from current page
				strBS = BeautifulSoup(strRawText.text, "lxml")
				strContent = strBS.get_text(" ", strip=True)

				if strBS.find('div', class_='mw-parser-output') is not None:
					pageText = strBS.find('div', class_='mw-parser-output').get_text(" ")
				else:
					pageText = strContent

				#don't crawl current page if not html doc
				if strDocType not in strRawText.headers.get("content-type", ""): continue

				imgageList = []
				if strBS.find(class_='mw-parser-output') is not None:
					linksList = strBS.find(class_='mw-parser-output').find_all('img')
					for imgSrc in linksList:
						imgageList.append(imgSrc.get('src'))
				
				if strBS.find('ul', class_='categories') is not None:
					categories = strBS.find('ul', class_='categories').get_text(', ', strip=True)[14:]
				else:
					categories = ""

				#write each page to file
				strPath = url.replace('/','').replace(':','')
				with open(f'files/{strPath}.txt', 'w') as f:
					f.write(f"{pageText}\nPAGEDONEKEY\n IMG: {imgageList}\n URL: {url}\n CATEGORIES: {categories}")
				f.close()
				
				#initialize a set for current pages url's
				objNewUrlQueue = set()

				#add current url to seen url dictionary
				objSeenURL[url] = []

				#save all links on current page
				for link in strBS.find_all("a"):
					strPageLink = str(link.get("href"))
					if strPageLink.startswith(strExtensionPrefix):
						objNewUrlQueue.add(strPageLink)
						objSeenURL[url].append(strPageLink)

				scraped.add(url)

				#add all new url's to existing url queue
				objMasterUrlQueue = objMasterUrlQueue.union(objNewUrlQueue)
				intCurrentPageNumber += 1

				#don't overload API
				time.sleep(1.3)
			except:
				continue
			
			#turn off crawler once desired # of pages is crawled
			if intCurrentPageNumber >= intPageAmount: break

	#generate augumented matrix
	createMatrix()

def createMatrix():
	# Remove links in key items that are not in our scraped set(for building adjacency matrix)
	for i in objSeenURL:
		objSeenURL[i] = set(objSeenURL[i]).intersection(scraped)
		if not objSeenURL[i]:
			objSeenURL[i] = [i]

	with open('linkDictionary.pickle', 'wb') as handle:
		pickle.dump(objSeenURL, handle, protocol=-1)
		
	linkSets = [(j,k) for j , i in objSeenURL.items() for k in i]
	df = pandas.DataFrame(linkSets)
	matrix = pandas.crosstab(df[0], df[1])

	# Write adjacency matrix to csv file
	matrix.to_csv('matrix.csv')

if __name__ == '__main__':
	main()
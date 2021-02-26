from bs4 import BeautifulSoup
import json
import urllib2


BASE_URL = "https://www.eclasscontent.com/index.php" #Url of the homepage to be scraped.
visited = [] #visited pages.

"""
Function to initialise the parent nodes (pages).
key: Unique Primary key to identify the node. 
href: url to the node.
level: depth of the node.
child: list of child nodes and their metadata
"""
def initialize(data):
	print "------------------------ Fetching level: 0 ------------------------"
	home_page = urllib2.urlopen(BASE_URL)
	soup = BeautifulSoup(home_page,'html.parser')
	ulTag = soup.find('ul',attrs={'class':'tree'})
	for liTag in ulTag.find_all('li'):
		key = str(liTag['id']).strip()
		if(key not in visited):
			for aTag in liTag.find_all('a'):
				href = str(aTag['href']).strip()
				name = str(aTag.text).strip()
				data[key] = {}
				data[key]['href'] = href
				data[key]['name'] = name
				data[key]['level'] = 0
				data[key]['child'] = []
				data[key]['parent'] = ''
			visited.append(key)

"""
Function to scrape the metadata of the nodes.
The meta data is stored in a HTML table.
Note: Only leaf node have a table attached to them.
"""
def scrapeMetaData(tableTag):
	metaData = {}
	for trTag in tableTag.find_all('tr'):
			thTag = trTag.find('th')
			tdTag = trTag.find('td')
			if(thTag and tdTag):
				metaData[str(thTag.text).strip()] = tdTag.text
			elif(thTag):
				metaData[str(thTag.text).strip()] = {}
			else:
				pTag = trTag.find('p',attrs={'class':'center'})
				imgTag = trTag.find('img',attrs={'class':'imageCategory'})
				imgName = str(pTag.text).strip()
				metaData['Properties:']['img'] = {}
				metaData['Properties:']['img']['src'] = str(imgTag['src']).strip()
				metaData['Properties:']['img']['name'] = imgName
				ulTag = trTag.find('ul',attrs={'class':'classic'})
				if(ulTag):
					for liTag in ulTag.find_all('li'):
						try: 
							aTag = liTag.find('a')
							href = aTag['href']
							key = str(aTag.text).strip()
							name = liTag.text
							metaData['Properties:'][key] = {}
							metaData['Properties:'][key]['href'] = href
							metaData['Properties:'][key]['name'] = name
						except:
							print "Error in metadata at:",liTag
	return metaData


"""
BFS functions to traverse the tree level by level.
While traversal store the primary key of each child node in the parentObj
"""
def bfs(parentKey, parentObj, level, newData):
	url = BASE_URL + parentObj['href']
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page,'html.parser')
	liTag = soup.find('li',attrs={'id': parentKey})
	ulTag = liTag.find('ul')
	tableTag = soup.find('table',attrs={'class':'table cart'})
	if(tableTag):
		metadata = scrapeMetaData(tableTag)
		parentObj['metadata'] = metadata
	if(ulTag):
		for childLiTag in ulTag.find_all('li'):
			childKey = childLiTag['id']
			parentObj['child'].append(childKey)
			if(childKey not in visited):
				for childATag in childLiTag.find_all('a'):
					try:
						childHref = str(childATag['href']).strip()
						childName = childATag.text
						newData[childKey] = {}
						newData[childKey]['href'] = childHref
						newData[childKey]['name'] = childName
						newData[childKey]['level'] = level
						newData[childKey]['child'] = []
						newData[childKey]['parent'] = parentKey 
					except:
						print "Error in bfs at:",childLiTag
				visited.append(childKey)


def main():
	data = {} #Dictionary to store the scraped data.
	COUNT = 0
	
	initialize(data)
	level = 1;
	while(data!={} and level<10):
		print "------------------------ Fetching level: " + str(level) + " ------------------------"
		newData = {}
		for key in data.keys():
			bfs(key,data[key],level+1,newData)
		
		print "------------------------ level: "+ str(level) + " Count: " + str(len(newData)) + " ------------------------"
		
		#Dump the data into a json file
		print "------------------------ Dumping level: " + str(level-1) + " ------------------------"
		with open('level'+str(level-1)+'.json','w') as fp:
				json.dump(data,fp)
		
		level = level+1
		data = newData


main()
from flask import Flask, render_template, url_for, request
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
import pickle

f = open('scoreDict.pickle', 'rb')
scoreDict = pickle.load(f)

app = Flask(__name__)
with open("./categories.pickle", "rb") as hehe:
	categories = pickle.load(hehe)

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html', categories=categories)


@app.route('/results/', methods=['GET', 'POST'])
def results():
	global mySearcher
	
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args

	query = data.get('searchterm')

	mySearcher = MyWhooshSearcher()
	titles, description = mySearcher.search(query)
	print("You searched for: " + query)

	parsedTitles = list()
	for title in titles:
		startInd = title.find("wiki") + len("wiki")
		endInd = title.find(".txt")

		parsedTitles.append(title[startInd : endInd].replace('%', ' ').replace('_', ' '))
	
	selected_animal = request.form.get('name')
	print(selected_animal)

	summaries, links = getSummariesAndLinks(description, 150)

	return render_template('results.html', query=query, results=zip(parsedTitles, links, summaries), categories=categories)


@app.route('/sergate', methods=['GET', 'POST'])
def sergate():
	if request.method == 'get':
		data = request.form
	else:
		data = request.args
	
	return render_template('sergate.html')

def getSummariesAndLinks(description, summary_length):
	#Parsing description for summary and link	
	links = list()
	summaries = list()
	for foo in description:
		bar = foo.split(' ')
		for i in range(len(bar)):
			# Finding and getting link
			if bar[i] == "Link:":
				links.append(bar[i + 1])
				i = i + 2
	
			# Creating summary
			ctr = 0
			# empty string summary is created into
			summary = ""
	
			while i < len(bar):
				if not bar[i].isspace():
					summary += bar[i] + ' '
					ctr += 1

				if ctr >= summary_length:
					summary += ". . ."
					break

				i = i + 1
		
			summaries.append(summary)
	return summaries, links

def Sort_Tuple(tup):
    lst = len(tup)
    for i in range(0, lst):
         
        for j in range(0, lst-i-1):
            if (tup[j][1] > tup[j + 1][1]):
                temp = tup[j]
                tup[j]= tup[j + 1]
                tup[j + 1]= temp
    return tup

class MyWhooshSearcher(object):
	def __init__(self):
		super(MyWhooshSearcher, self).__init__()
		
	def search(self, queryEntered):
		title = list()
		description = list()
		indexer = whoosh.index.open_dir("myIndex")
		
		
		with indexer.searcher() as search:
			query = MultifieldParser(['title', 'textdata'], schema=indexer.schema)
			# query = QueryParser("textdata", indexer.schema)
			queryEntered = queryEntered.replace(" ", " OR ")
			query = query.parse(queryEntered)
			results = search.search(query, limit=None)
			sortList = []
			print(results)
			for i in results:
				if i['title'] in scoreDict:
					sortList.append((i, i.score/scoreDict[i["title"]]))

			Sort_Tuple(sortList)
			sortList.reverse()

			for x in sortList:
				title.append(x[0]['title'])
				description.append(x[0]['textdata'])
		
		return title[:10], description[:10]

if __name__ == '__main__':
	global mySearcher
	mySearcher = MyWhooshSearcher()
	app.run(host='0.0.0.0', port=8000 ,debug=True)


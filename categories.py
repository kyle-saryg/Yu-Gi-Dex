import os
import csv
import lxml
import pickle
# generate list of all catergories
counter = 0
filePaths = [os.path.join('./files', i) for i in os.listdir('./files')]
categories = []
for file in filePaths:
	with open(file) as fp:
		for line in fp:
			pass
		last_line = line[12:len(line)-14]
		cats = last_line.split(',')
		for category in cats:
			if category not in categories:
				categories.append(category)

print(len(categories))
categories.sort()
print(categories)
with open("categoryList.pickle", "wb") as handle:
	pickle.dump(categories, handle, protocol = -1)

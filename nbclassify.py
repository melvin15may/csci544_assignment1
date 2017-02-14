
import sys
import json
from collections import Counter
from string import punctuation
from math import log

"""
	positive = 1
	negative = 0
	truthful = 1
	deceptive = 0
	p/n t/d
	0 0 = 0 n d
	0 1 = 1 n t
	1 0 = 2 p d
	1 1 = 3 p t
"""
"""
	model = {  [n,p,d,t]
		"abc": [0,0,0,0]
	}
"""

def classify(model, test, prior):
	classified = {}
	for tt in test:
		n = -float("inf") if prior["negative"] == 0 else log(prior["negative"])
		p = -float("inf") if prior["positive"] == 0 else log(prior["positive"])
		d = -float("inf") if prior["deceptive"] == 0 else log(prior["deceptive"])
		t = -float("inf") if prior["truthful"] == 0 else log(prior["truthful"])
		for i in test[tt]:
			if i in model:
				n += model[i][0] * test[tt][i]
				p += model[i][1] * test[tt][i]
				d += model[i][2] * test[tt][i]
				t += model[i][3] * test[tt][i]
		classified[tt] = 0
		if p > n:
			classified[tt] = 2
		if t > d:
			classified[tt] += 1

	return classified

def tokenizer(words):
	ignore_words = ['a', 'about', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'computer', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thick', 'thin', 'third', 'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves']
	new_word = [x.lower().translate(None,punctuation) for x in words if x.lower() not in ignore_words]
	return new_word

def main():
	try:
		if sys.argv[0] != 'nblearn.py':
			print sys.argv
			test_file = sys.argv[1]
			test = {}

			with open(test_file) as l:
				lines = l.readlines()
				for lline in lines:
					split_line = lline.split()
					test[split_line[0]] = dict(Counter(tokenizer(split_line[1:])))
			with open('nbmodel.txt') as m:
				data = json.load(m)

			classified = classify(data["model"], test, data["prior"])

			with open('nboutput.txt','w+') as o:
				for i in classified:
					o.write('{} {} {}\n'.format(i, 'deceptive' if(classified[i]%2==0) else 'truthful',  'positive' if (classified[i] >= 2) else 'negative'))
	except IndexError, ValueError:
		pass

main()
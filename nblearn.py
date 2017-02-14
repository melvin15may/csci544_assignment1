
import sys
from collections import Counter
from json import dump
from math import log
from nbclassify import classify, tokenizer
from random import sample


def position(value):
	p = 1 if (value >= 2) else 0
	t = 2 if (value % 2 == 0) else 3
	return [p,t]

def calculate_f1(pred_label, true_label):
	"""
		recall = tp / (tp + fn)
		Precision = tp / tp+fp

			truth
		cal	tp fp
		l	fn tn

		F1 = 2PR/(P+R)

	"""
	#	 [n,p,d,t]
	tp = [0,0,0,0]
	fn = [0,0,0,0]
	tn = [0,0,0,0]
	fp = [0,0,0,0]

	for i in pred_label:
		if i in true_label:
			true_pos = position(true_label[i])
			pred_pos = position(pred_label[i])
			if true_pos[0] == pred_pos[0]:
				tp[true_pos[0]] += 1
				tn[1 - true_pos[0]] += 1
			elif true_pos[0] - pred_pos[0] > 0:
				fn[true_pos[0]] += 1
			else:
				fp[true_pos[0]] += 1

			if true_pos[1] == pred_pos[1]:
				tp[true_pos[1]] += 1
				tn[true_pos[1] + pow(-1,true_pos[1])] += 1
			elif true_pos[1] - pred_pos[1] > 0:
				fn[true_pos[1]] += 1
			else:
				fp[true_pos[1]] += 1

	recall = [0,0,0,0]
	precision = [0,0,0,0]
	f1 = [0,0,0,0]

	print (str(tp)+' '+ str(fn) +' '+ str(tn) +' '+ str(fp) +' ')

	for i in range(4):
		recall[i] = tp[i] * 1.0 / (tp[i]+fn[i])
		precision[i] = tp[i] * 1.0 / (tp[i]+fp[i])
		f1[i] = 2.0 * recall[i] * precision[i] / (recall[i] + precision[i])
	
	print sum(f1)/4.0
	return sum(f1)/4.0

#percentage of data to be used for training 
def main(training_percentage=0.75):
	#read label and training data

	training_file = sys.argv[1]
	label_file = sys.argv[2]
	prior_total_positive = 0
	prior_total_truthful = 0
	development = {}
	true_label = {}

	model = {}
	label = {}
	prior = {}
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
	no_training_data = 0;
	with open(label_file) as l:
		lines = l.readlines()
		no_total_data = len(lines)
		no_training_data = int(training_percentage * no_total_data)

		#training_lines = sample(lines,no_training_data)

		#for lline in lines[0:no_training_data]:
		for lline in lines:
			line = lline.strip('\n').strip('\r').split(' ')
			label[line[0]] = 0
			if line[2] == 'positive':
				label[line[0]] = 2
				prior_total_positive += 1
			if line[1] == 'truthful':
				label[line[0]] += 1
				prior_total_truthful += 1
		"""
		development_lines = list(set(lines) - set(training_lines))
		#for lline in lines[no_training_data:]:
		for lline in development_lines:
			line = lline.strip('\n').split(' ')
			true_label[line[0]] = 0
			if line[2] == 'positive':
				true_label[line[0]] = 2
			if line[1] == 'truthful':
				true_label[line[0]] += 1
		"""	
	"""
		model = {  [n,p,d,t]
			"abc": [0,0,0,0]
		}
		total =    [0,0,0,0]
	"""
	#print len(label.keys())
	total = [0,0,0,0]
	with open(training_file) as l:
		lines = l.readlines()
		for lline in lines:
			split_line = lline.strip('\n').strip('\r').split(' ')
			#if split_line[0] in label:
			label_out = label[split_line[0]]
			
			#trying lower
			count_dict_line = dict(Counter(tokenizer(split_line[1:])))
			p = 1 if (label_out >= 2) else 0
			t = 2 if (label_out % 2 == 0) else 3
			for i in count_dict_line:
				if not i in model:
					model[i] = [0, 0, 0, 0]
				model[i][p] += count_dict_line[i]
				model[i][t] += count_dict_line[i]
				total[p] += count_dict_line[i]
				total[t] += count_dict_line[i]
			#else:
				#development[split_line[0]] = dict(Counter(tokenizer(split_line[1:])))

	# add to denominator for smoothing
	B = len(model.keys())


	for i in model:
		model[i][0] = log((model[i][0] + 1.0)/(total[0] + B))
		model[i][1] = log((model[i][1] + 1.0)/(total[1] + B))
		model[i][2] = log((model[i][2] + 1.0)/(total[2] + B))
		model[i][3] = log((model[i][3] + 1.0)/(total[3] + B))

	# what if all are positive or all negative
	prior = {
		"negative": ((no_training_data - prior_total_positive) * 1.0/no_training_data),
		"positive": (prior_total_positive * 1.0/no_training_data),
		"deceptive":((no_training_data - prior_total_truthful) * 1.0/no_training_data),
		"truthful": (prior_total_truthful * 1.0/no_training_data),
	}

	#pred_label = classify(model,development,prior)
	#calculate F1

	new_model = {
				"meta": {
					"format": "'word': ['negative','positive','deceptive','truthful']",
					"training_precent": i
				},
				"prior": prior,
				"model": model
			}

	with open('nbmodel.txt','w+') as f:
		dump(new_model,f)

main()

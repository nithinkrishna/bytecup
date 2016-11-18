import numpy as np
import pandas as pd
import sys
from os import listdir
from os.path import isfile, join

from sklearn.feature_extraction.text import CountVectorizer

import libpmf.libpmf as libpmf

def run(TYPE, K, lb):
  print "TESTING: {0}".format(K)

  question_info = pd.read_csv("data/question_info.txt", sep="\t", header=None, names=[
    "question_id", "tag", "word_id", "char_id", "upvotes", "answers", "top_answers"
  ])
  user_info = pd.read_csv("data/user_info.txt", sep="\t", header=None, names=[
    "user_id", "expert_tags", "word_id", "char_id"
  ])

  vctorizer = CountVectorizer(lambda s: s.split('/'))

  if TYPE == "qW":
    data = vctorizer.fit_transform(question_info['word_id'])

  if TYPE == "qC":
    data = vctorizer.fit_transform(question_info['char_id'])

  if TYPE == "uW":
    data = vctorizer.fit_transform(user_info['word_id'])

  if TYPE == "uC":
    data = vctorizer.fit_transform(user_info['char_id'])

  if TYPE == "uT":
    data  = vctorizer.fit_transform(user_info['expert_tags'])

  model = libpmf.train(data, '-k {0} -l {1} -t 10 -T 10 -N 1'.format(K / 100 * data.shape[ 1 ], lb))

  dMAtrix = data.todense()
  factorized = np.dot( model['W'], model['H'].transpose() )

  ERROR = np.square(dMAtrix - factorized).mean()

  return ERROR

TYPE = sys.argv[1]
lb   = 0.1

def hill_climbing(k, step, prev_error=np.inf, iter=0, MAX_ITER=1000):
  if iter == MAX_ITER:
    return k

  error = run(TYPE, k, lb)

  if error == prev_error:
    return k

  if error < prev_error:
    return hill_climbing(k+step, step, error, iter+1)

  if error > prev_error:
    step = float(-step) / 10
    return hill_climbing(k+step, step, error, iter+1)

print "BEST K : ".format( hill_climbing(25.0, 1.0) )



import pickle
import argparse
import numpy as np
import normalize as nm
import feature_selection as fs
from sys import stdout
from collections import Counter
from nltk.tokenize import word_tokenize


def train(pdata):
    print("Started training..")
    # Extract vocabulary
    V = get_text(pdata, True)
    # Number of docs
    N = len(pdata.index)
    # Dict of prior probabilities
    prior = {}
    # Dict of conditional probabilities
    condprob = {}

    for mclass in pdata['ministerie'].unique():
        print("Training {}".format(mclass))
        cdata = pdata.loc[pdata['ministerie'] == mclass]
        N_c = len(cdata.index)
        prior[mclass] = N_c / N
        text_c = get_text(cdata)
        counts = Counter(text_c)
        for i, word in enumerate(V):
            # i+1: on the last iteration the print is not updated
            stdout.write("\r%d / %d" % (i+1, len(V)))
            stdout.flush
            if word not in condprob:
                condprob[word] = {}
            T_ct = counts[word]
            condprob[word][mclass] = (T_ct + 1) / len(text_c)
        stdout.write("\n")

    saveData(V, prior, condprob)
    return V, prior, condprob


def test(prior, condprob, pdata, test_data):
    correct = 0
    FP, TP, FN, TN = (0,0,0,0)
    for i, row in enumerate(test_data.iterrows()):
        scores = apply(prior, condprob, pdata, row[1])
        winner = max(scores, key=scores.get)
        print("{} versus {}".format(winner, row[1]['ministerie']))
        if winner == row[1]['ministerie']:
            correct += 1

        print("{} / {} ".format(correct, (i+1)))

    pre = correct / i
    rec = correct / i
    f1 = 2 * pre * rec / pre + rec
    return pre, rec, f1


def apply(prior, condprob, pdata, newdoc):
    W = get_single_text(newdoc)
    score = {}
    for mclass in pdata['ministerie'].unique():
        score[mclass] = np.log10(prior[mclass])
        for word in W:
            if word in condprob.keys():
                score[mclass] += np.log10(condprob[word][mclass])
            else:
                # Skip words that we have not encountered before.
                continue
    return score


def saveData(V, prior, condprob):
    with open('trained_data.pik', 'wb') as f:
        pickle.dump([V, prior, condprob], f, -1)
        print("!! Wrote training data to trained_data.pik.")


def get_single_text(pdata):
    voc = word_tokenize(pdata['titel'])
    voc.extend(word_tokenize(pdata['vraag']))
    voc.extend(word_tokenize(pdata['antwoord']))
    return voc


def get_text(pdata, unique=False):
    voc = accum_words('titel', pdata)
    voc.extend(accum_words('vraag', pdata))
    voc.extend(accum_words('antwoord', pdata))
    if unique is True:
        voc = set(voc)
    return voc


def accum_words(name, pdata):
    wordlist = []
    for sentence in pdata[name]:
        wordlist.extend(word_tokenize(sentence))
    return wordlist


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('data', help='data folder for KVR.csv.gz')
    parser.add_argument('test_per', help='test data folder for KVR',
                        type=float)
    parser.add_argument('--load', help='load data from pickle file',
                        metavar='file', nargs=1)
    args = parser.parse_args()
    print(args)
    # normalize ministeries
    data = nm.normalize_min(args.data)
    cutoff = round(len(data.index)*args.test_per)
    train_data, test_data = data[:cutoff], data[cutoff:]
    if args.load is not None:
        with open(args.load[0], 'rb') as f:
            V, prior, condprob = pickle.load(f)
    else:
        V, prior, condprob = train(train_data)

    # pr, re, f1 = test(prior, condprob, data, test_data)
    # print("-------------------")
    # print(pr)
    # print(re)
    # print(f1)
    print("-------------------")
    print("Selecting features..")
    print(fs.get_top(V, train_data, 10))

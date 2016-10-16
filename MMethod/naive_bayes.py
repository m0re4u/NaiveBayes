import pickle
import argparse
import numpy as np
import normalize as nm
from nltk.tokenize import word_tokenize


def train(pdata):
    print("Started training..")
    # Extract vocabulary
    V = get_text(pdata)
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
        for i, word in enumerate(V):
            if word not in condprob:
                condprob[word] = {}
            T_ct = text_c.count(word)
            condprob[word][mclass] = (T_ct + 1) / len(text_c)

    saveData(V, prior, condprob)
    return V, prior, condprob


def apply(V, prior, condprob, pdata, newdoc):
    W = get_text(newdoc)
    score = {}
    for mclass in pdata['ministerie'].unique():
        score[mclass] = np.log(prior[mclass])
        for word in W:
            if word in condprob.keys():
                score[mclass] += np.log(condprob[word][mclass])
            else:
                # Skip words that we have not encountered before.
                continue
    return score


def saveData(V, prior, condprob):
    with open('trained_data.pik', 'wb') as f:
        pickle.dump([V, prior, condprob], f, -1)
        print("!! Wrote training data to trained_data.pik.")


def get_text(pdata):
    voc = accum_words('titel', pdata)
    voc.extend(accum_words('vraag', pdata))
    voc.extend(accum_words('antwoord', pdata))
    return voc


def accum_words(name, pdata):
    wordlist = []
    for sentence in pdata[name]:
        wordlist.extend(word_tokenize(sentence))
    return wordlist


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('data', help='data folder for KVR')
    parser.add_argument('--load', help='load data from pickle file',
                        metavar='file', nargs=1)
    args = parser.parse_args()
    print(args)
    data = nm.normalize_min(args.data)
    if args.load is not None:
        with open(args.load[0], 'rb') as f:
            V, prior, condprob = pickle.load(f)
    else:
        V, prior, condprob = train(data)

    scores = apply(V, prior, condprob, data.iloc[:-1], data.iloc[-1])
    print("-------------------")
    print(data.iloc[-1])
    print(max(scores))
    print(max(scores, key=scores.get))

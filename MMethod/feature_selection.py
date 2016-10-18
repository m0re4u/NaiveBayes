import numpy as np
from sys import stdout
from nltk import word_tokenize
from naive_bayes import get_text
from collections import Counter, defaultdict


def select_features(V, pdata, mclass, k):
    A = {}
    # C_1
    print("Getting text")
    mdata = pdata[pdata['ministerie'] == mclass]
    ndata = pdata[~(pdata['ministerie'] == mclass)]
    mtext = get_text(mdata)
    ntext = get_text(ndata)
    mCounter = Counter(mtext)
    nCounter = Counter(ntext)

    for i, term in enumerate(V):
        stdout.write("\r%d / %d" % (i+1, len(V)))
        stdout.flush
        A[term] = get_utility(mdata, ndata, term, mclass)
    stdout.write('\n')
    print([(k, v) for (k, v) in A.items() if v != 0])
    return sorted(A, key=A.__getitem__)[:k]


def get_utility(mCounter, nCounter, term, mclass):
    # All documents
    N = sum(mCounter.values().extend(nCounter.values()))

    # Number of documents where term is in the document, but document not in
    # class
    if term in nCounter:
        N10 = nCounter[term]
    else:
        N10 = 0

    # Number of documents where term is in the document and document is in
    # class
    if term in nCounter:
        N11 = mCounter[term]
    else:
        N11 = 0

    # Number of documents where term not in document, and document is not in
    # class
    N00 = N - len(nCounter.keys())

    # Number of documents where term not in document, but document is in class
    N01 = N - len(mCounter.keys())

    a, b, c, d = (0, 0, 0, 0)
    if N11 != 0:
        a = N11 / N * np.log2((N*N11) / ((N10 + N11) * (N01 + N11)))
    if N01 != 0:
        b = N01 / N * np.log2((N*N01) / ((N01 + N00) * (N01 + N11)))
    if N10 != 0:
        c = N10 / N * np.log2((N*N10) / ((N10 + N11) * (N10 + N00)))
    if N00 != 0:
        d = N00 / N * np.log2((N*N00) / ((N01 + N00) * (N10 + N00)))

    return a + b + c + d


def get_top(V, pdata, k):
    for mclass in pdata['ministerie'].unique():
        print("Getting util for {}".format(mclass))
        f = select_features(V, pdata, mclass, k)
        print(f)

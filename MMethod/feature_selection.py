import numpy as np
from nltk import word_tokenize
from sys import stdout
from naive_bayes import get_text


def select_features(V, pdata, mclass, k):
    A = {}
    # C_1
    print("Getting text")
    mdata = pdata[pdata['ministerie'] == mclass]
    ndata = pdata[~(pdata['ministerie'] == mclass)]
    mtext = get_text(mdata)
    ntext = get_text(ndata)

    for i, term in enumerate(V):
        stdout.write("\r%d / %d" % (i+1, len(V)))
        stdout.flush
        A[term] = get_utility(mdata, ndata, term, mclass)
    stdout.write('\n')
    print([(k, v) for (k, v) in A.items() if v != 0])
    return sorted(A, key=A.__getitem__)[:k]


def get_utility(mdata, ndata, term, mclass):
    # All documents
    N = len(mdata.index) + len(ndata.index)

    # Number of documents where term is in the document, but document not in
    # class
    if (term in ndata['titel']) or (term in ndata['vraag']) or (term in ndata['antwoord']):
        print("found non-null")
        sdata = ndata[(term in ndata['titel']) | (term in ndata['vraag']) | (term in ndata['antwoord'])]
        print("qdata: {}".format(sdata))
        N10 = len(sdata.index)
    else:
        N10 = 0

    # Number of documents where term is in the document and document is in
    # class
    if (term in mdata['titel']) or (term in mdata['vraag']) or (term in mdata['antwoord']):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!found non-null")
        tdata = mdata[(term in mdata['titel']) | (term in mdata['vraag']) | (term in mdata['antwoord'])]
        # print("tdata: {}".format(tdata))
        N11 = len(tdata.index)
    else:
        N11 = 0

    # Number of documents where term not in document, and document is not in
    # class
    if (term not in ndata['titel']) and (term not in ndata['vraag']) and (term not in ndata['antwoord']):
        N00 = len(ndata.index)
    else:
        N00 = 0

    # Number of documents where term not in document, but document is in class
    if (term not in mdata['titel']) and (term not in mdata['vraag']) and (term not in mdata['antwoord']):
        N01 = len(mdata.index)
    else:
        N01 = 0

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

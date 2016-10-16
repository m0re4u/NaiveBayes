import argparse
import pandas as pd

ministeries = [
    "Algemene Zaken",
    "Binnenlandse Zaken en Konkrijksrelaties",
    "Buitenlandse Zaken",
    "Defensie",
    "Economische Zaken",
    "Financien",
    "Infrastructuur en Milieu",
    "Onderwijs, Cultuur en Wetenschappen",
    "Sociale Zaken en Werkgelegenheid",
    "Veiligheid en Justitie",
    "Volksgezondheid, Welzijn en Sport",
    "Economische Zaken, Landbouw en Innovatie",
    "Verkeer en Waterstaat",
    "Volkshuisvesting, Ruimtelijke Ordening en Milieubeheer",
    "Vreemdelingenzaken en Integratie",
    "Landbouw, Natuur en Voedselkwaliteit",
             ]


def normalize_min(data):
    # Rules rule
    rules_dict = {
        'algemene zaken (az)': 'Algemene Zaken',
        'bestuurlijke vernieuwing en koninkrijksrelaties (bvk)': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'binnenlandse zaken en koninkrijksrelaties': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'binnenlandse zaken en koninkrijksrelaties (bzk)': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'binnenlandse zaken': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'buitenlandse zaken (buza)': 'Buitenlandse Zaken',
        'defensie (def)': 'Defensie',
        'meldingsplicht': 'Defensie',
        'economische zaken (ez)': 'Economische Zaken, Landbouw en Innovatie',
        'europese zaken (euz)': 'Buitenlandse Zaken',
        'financiën': 'Financien',
        'financiën (fin)': 'Financien',
        'financiã«n': 'Financien',
        'financiã«n (fin)': 'Financien',
        'grote steden- en integratiebeleid': 'Sociale Zaken en Werkgelegenheid',
        'grote steden- en integratiebeleid (gsi)': 'Sociale Zaken en Werkgelegenheid',
        'integratie, jeugdbescherming': 'Volksgezondheid, Welzijn en Sport',
        'jeugd en gezin (jg)': 'Volksgezondheid, Welzijn en Sport',
        'justitie': 'Veiligheid en Justitie',
        'justitie (jus)': 'Veiligheid en Justitie',
        'kabinet voor nederlands-antilliaanse en arubaanse zaken (naaz)': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'kabinet voor nederlands-antilliaanse en arubaanse zaken': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'landbouw, natuurbeheer en visserij': 'Landbouw, Natuur en Voedselkwaliteit',
        'landbouw, natuurbeheer en visserij (lnv)': 'Landbouw, Natuur en Voedselkwaliteit',
        'minister-president (mp)': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'mp': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'nederlands antilliaanse en arubaanse zaken': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'onderwijs, cultuur en wetenschap (ocw)': 'Onderwijs, Cultuur en Wetenschappen',
        'onderwijs, cultuur en wetenschappen (ocw)': 'Onderwijs, Cultuur en Wetenschappen',
        # BUZA is responsible for ontwikkelingssamenwerking
        'ontwikkelingssamenwerking': 'Buitenlandse Zaken',
        'sociale zaken en werkgelegenheid (szw)': 'Sociale Zaken en Werkgelegenheid',
        'staten-generaal (sg)': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'staten-generaal': 'Binnenlandse Zaken en Koninkrijksrelaties',
        'verkeer en waterstaat (vw)': 'Verkeer en Waterstaat',
        '\'erkeer en waterstaat': 'Verkeer en Waterstaat',
        'volkshuisvesting, ruimtelijke ordening en milieubeheer (vrom)': 'Volkshuisvesting, Ruimtelijke Ordening en Milieubeheer',
        'volksgezondheid, welzijn en sport (vws)': 'Volksgezondheid, Welzijn en Sport',
        'vreemdelingenzaken en integratie (vi)': 'Veiligheid en Justitie',
        'vi': 'Veiligheid en Justitie',
        'vreemdelingenzaken en integratie (vzi)': 'Veiligheid en Justitie',
        'wonen, wijken en integratie (wwi)': 'Sociale Zaken en Werkgelegenheid'
    }

    kvrdf = pd.read_csv(
        data, compression='gzip', sep='\\t', index_col=0, engine='python',
        names=['jaar', 'partij', 'titel', 'vraag', 'antwoord', 'ministerie'])

    # Drop all entries without ministry, since we cannot use them for training
    # Maybe revisit this when looking for a test set.
    kvrdf = kvrdf.dropna()

    # Normalize the ministries, given the rules above
    for i, mini in enumerate(kvrdf['ministerie']):
        # Some normal form
        normin = mini.lower().lstrip()
        # Check if its the same as our ministries
        if normin not in [x.lower() for x in ministeries]:
            # Check if a rule applies
            if normin in rules_dict.keys():
                kvrdf['ministerie'][kvrdf.index[i]] = rules_dict[normin]
            else:
                # Look for some substring that will match versus the known
                # forms of ministries In that case, assign it to the first
                # ministry you encounter
                keys = list(rules_dict.keys())
                for j, key in enumerate(keys):
                    if key in normin:
                        kvrdf['ministerie'][kvrdf.index[i]] = rules_dict[keys[j]]
                        break
                vals = list(rules_dict.values())
                for k, val in enumerate(vals):
                    if val in mini:
                        kvrdf['ministerie'][kvrdf.index[i]] = vals[k]
                        break
        # Remove leading whitespace if the rest of the string is matching
        else:
            kvrdf['ministerie'][kvrdf.index[i]] = mini.lstrip()

    return kvrdf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('data', help='data folder for KVR')
    args = parser.parse_args()
    normalize_min(args.data)

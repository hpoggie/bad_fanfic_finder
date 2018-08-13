import requests
import re
from bs4 import BeautifulSoup as bs


def wikipediaTypos():
    """
    Grab list of common typos from Wikipedia.
    Typos are an excellent indicator of a low quality fanfic.
    """
    site = '''
    https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
    '''

    r = requests.get(site)
    # Last line is blank for some reason
    lines = bs(r.text, "lxml").pre.text.split('\n')[:-1]
    return [x.split('->')[0] for x in lines]

ratingAll = "?&srt=1&r=10"

keywords = [
        # typos (TODO: add more)
        'dont',
        # m-rated stuff tends to be more cringeworthy
        'Rated: M',
        # concepts that frequently lead to disaster
        'OC',
        'OP',
        'bashing',
        'OOC',
        'experimental',
        'angst',
        ] + wikipediaTypos()

compiledRegexes = [re.compile(keyword, re.IGNORECASE) for keyword in keywords]


def extractLinks(site):
    """
    extract links to all crossovers from the site for a single work
    e.g. 'https://www.fanfiction.net/crossovers/Legend-of-Zelda/123/'
    """
    r = requests.get(site)
    return [div.a['href'] for div in
            bs(r.text, 'lxml').find(id='list_output').td('div')]


def matches(text):
    """
    Return the list of keyword matches in text
    """
    matches = []

    for rgx in compiledRegexes:
        found = rgx.findall(text)
        matches.append((rgx.pattern, len(found)))

    return matches


def matchesAsString(text):
    ms = matches(text)
    total = sum(t[1] for t in ms)
    return ('\n'.join(str(t) for t in ms if t[1] > 0) +
            "\nTotal : " + str(total))


def extractFics(site, keywords):
    """
    extract all fics for a given crossover site
    e.g.
    https://www.fanfiction.net/Legend-of-Zelda-and-Harry-Potter-Crossovers/123/224/
    """

    try:
        r = requests.get(site)
    except IOError:
        print("IOError for site " + site)
        return

    return [(
        x.get_text(),
        x.parent(href=re.compile('/u/*'))[0].get_text(),
        x.parent.div.get_text(),
        matchesAsString(x.parent.get_text())
        ) for x in
            bs(r.text, "lxml")(attrs={'class': 'stitle'})]


if __name__ == '__main__':
    # replace with the URL for a work of your choice.
    # currently only searches for crossovers
    baseSite = 'https://www.fanfiction.net/crossovers/Legend-of-Zelda/123/'

    fics = []

    for site in extractLinks(baseSite):
        print("getting fics from " + site)
        url = 'https://www.fanfiction.net' + site + ratingAll
        fics.extend(extractFics(url, keywords))

    sortedFics = sorted(fics, key=lambda fic: fic[3])

    print("writing %d fics to file" % len(sortedFics))

    with open("output.txt", "w") as f:
        for fic in sortedFics:
            f.write(fic[0] + "\n")
            f.write(fic[1] + "\n")
            f.write(fic[2] + "\n")
            f.write(fic[3] + "\n")
            f.write("\n")

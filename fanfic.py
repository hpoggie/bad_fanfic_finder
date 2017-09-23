import urllib
from re import search
import os
from BeautifulSoup import BeautifulSoup as bs

ratingAll = "?&srt=1&r=10"

keywords = [
        # typos (TODO: add more)
        '[Dd]ont',
        '[tT]eh',
        # m-rated stuff tends to be more cringeworthy
        'Rated: M',
        # concepts that frequently lead to disaster
        'OC',
        'OP',
        '[Bb]ashing',
        'OOC',
        '[eE]xperimental',
        '[aA]ngst'
        ]


def extractLinks(site):
    """
    extract links to all crossovers from the site for a single work
    e.g. 'https://www.fanfiction.net/crossovers/Legend-of-Zelda/123/'
    """
    links = []
    urllib.urlretrieve(site, filename='index.html')

    f = open('index.html', 'r')
    for line in f.readlines()[461:]:
        if search('a href', line):
            try:
                links.append(line.split('"')[1])
            except IndexError:
                pass

    os.remove('index.html')
    return links


def extractFics(site, keywords):
    """
    extract all fics for a given crossover site
    e.g. https://www.fanfiction.net/Legend-of-Zelda-and-Harry-Potter-Crossovers/123/224/
    """
    # TODO: strip HTML
    authors = []
    descs = []
    priorities = []

    try:
        urllib.urlretrieve(site, filename='index.html')
    except IOError:
        print "IOError for site " + site
        return

    f = open('index.html', 'r')
    for line in f.readlines():
        if search(' by ', line):
            authors.append(bs(line).prettify('utf-8'))

        if search('Rated: ', line):
            matches = 0
            for word in keywords:
                if search(word, line):
                    matches += 1

            descs.append(line)
            priorities.append(matches)

    os.remove('index.html')

    return zip(authors, descs, priorities)


# replace with the URL for a work of your choice.
# currently only searches for crossovers
baseSite = 'https://www.fanfiction.net/crossovers/Legend-of-Zelda/123/'

fics = []

for site in extractLinks(baseSite):
    print "getting fics from " + site
    url = 'https://www.fanfiction.net' + site + ratingAll
    fics.extend(extractFics(url, keywords))

sortedFics = sorted(fics, key=lambda fic: fic[2])

print "writing %d fics to file" % len(sortedFics)
f = open("output.txt", "w")

for fic in sortedFics:
    f.write(fic[0] + "\n")
    f.write(fic[1] + "\n")
    f.write(str(fic[2]) + "\n")
    f.write("\n")

f.close()

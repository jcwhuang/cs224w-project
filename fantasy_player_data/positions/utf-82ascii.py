import codecs

with codecs.open('players.json', encoding='utf-8') as f:
    for line in f:
        print line.encode('ascii', 'xmlcharrefreplace'),

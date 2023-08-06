from __future__ import with_statement

import re

featured = re.compile('\{\{('
                      'Featured[ |_]?list|'
                      'Featured[ |_]?portal|'
                      'Featured[ |_]?article|' 
                      'FL|'
                      'FA-Class|'
                      'GA-Class|'
                      'A-Class|'
                      'FL-Class'
                      ')[\}\|]+',
                      re.IGNORECASE+re.UNICODE)

import wiki

wiki._init_process('/home/itkach/wikidumps/enwiki-20090827-pages-articles.cdb', 'en', 'html')
with open('enwiki_featured.txt', 'w') as f:
    for a in wiki.wikidb.articles():
        text = wiki.wikidb.reader[a]
        if featured.search(text):
            f.write(a.encode('utf8'))
            f.write('\n')
            f.flush()

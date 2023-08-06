##
## addhrefs.py
## by Peter Bengtsson, 2004-2005, mail@peterbe.com
##
## License: ZPL (http://www.zope.org/Resources/ZPL)
##
__doc__='''A little function that puts HTML links into text.'''
__version__='0.9.7'


__changes__ = """
0.9.7         Fixed better support for domain names without www. or http:// prefix

0.9.6         Match closing links that use single quotes
              (thanks Adam)

0.9.5         Prep for a new source distribution.

0.9.4         Made improveURL a publically available function.

0.9.3         Fixed a bug when text contains "m." but wasnt followed but a a-z.

0.9.2         Added supports for URLs starting with m., mobile. and www2.
              Added 1 new unit test

0.9.1         Fixed broken link parsing containing {curly brackets}
              Added 15 new unit tests

0.9           Better support for strings already containing <a href.
              New unittest called testAddhrefs.py

0.8           Improvements to emaillinkfunction and urllinkfunction
              
0.7           addhrefs() checks that emaillinkfunction and urllinkfunction if passed
              are callable.
    
0.6           three new parameters:
                 return_everything=0 - returns (text, urlinfo, emailinfo)
                                       where urlinfo and emailinfo are lists
                 emaillinkfunction=None - callback function for making an email
                                          into a HTML link the way you want it
                 urllinkfunction=None - callback function for making an URL into
                                        a HTML link the way you want it
                                        
0.5           "foo https bar" created one link

0.4           Python2.1 compatible with custom True,False

0.3           Only one replace which solved the problem with
              "www.p.com bla bla http://www.p.com"
              
0.2           Lots of fine tuning. Created unit tests.

0.1           Project started. First working draft
"""

__credits__="""
David Otton,
"flump cakes"
"""

                     
import re, sys


TOP_LEVELS = \
'aero|asia|biz|cat|com|coop|edu|gov|info|int|jobs|mil|mobi|museum|name|net|'\
'org|pro|tel|travel|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|'\
'ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|'\
'ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cx|cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|er|es|'\
'et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|'\
'gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|'\
'kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|'\
'me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|'\
'ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|'\
'ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|su|sv|sy|sz|'\
'tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va'

_end_dropouts = list(')>.;:,"')
_start_dropouts = list('(<')
def _massageURL(url):
    while url[-1] in _end_dropouts:
        url = url[:-1]
    if url[0] in _start_dropouts:
        url = url[1:]
  
    return url

def improveURL(url):
    if '://' not in url and '@' not in url:
        return 'http://'+url
    return url

    # ok_middle_name_starts looks something like this:
    #  ('ftp','http','www.')
    # If our url here starts with any of those that end in a .
    # then add http:// to it
    for each in ok_middle_name_starts:
        if each.endswith('.') and url.startswith(each):
            return 'http://'+url
    if '://' not in url:
        return 'http://'+url
    return url


def _makeLink(url):
    return '<a href="%s">%s</a>'%(improveURL(url), url)

def _makeMailLink(url):
    return '<a href="mailto:%s">%s</a>'%(improveURL(url), url)

def _rejectEmail(email, start):
    if email.startswith("mailto:"):
        email = email[7:]
    if email.find(':') > -1:
        return True
    return False

_bad_in_url = list('!()<>')
_dont_start_url = list('@')
def _rejectURL(url, start):
    """ return true if the URL can't be a URL """
    if url.lower()=='https':
        return True
    for each in _bad_in_url:
        if url.find(each) > -1:
            return True
    whereat = url.find('@')
    if whereat > -1:
        for each in "http:// ftp:// https://".split():
            url = url.replace(each, '')
        if not -1 < url.find(':') < whereat:
            return True
    if start in _dont_start_url:
        return True
    return False


def _make_regexp(regexp):
    _whitespace = "[\s\({}<>\)]"
    #_not_whitespace  = "[^\s\({}<>\)]"
    _not_whitespace  = "[^\s{}<>]"
    ## don't allow url to end in ( or < but fine with ) or >
#    _not_whitespace  = "[^\s<>\)]" 
    regexp = regexp.replace("\s", _whitespace)
    regexp = regexp.replace("\S", _not_whitespace)
    regexp = re.compile(regexp)
    return regexp

#ok_middle_name_starts = ('ftp','http','www.','mobile.','m.','www2.')
ok_middle_name_starts = ('ftp','http','www.')
ok = {'start': ('^','\(','{','>','<','@','\s',''),
      'middle':('ftp\S+', 'http\S+', 'www\.\w\S+'),
          #('ftp\S+', 'http\S+', 'www\.\w\S+', 'mobile\.\w\S+', 'm\.\w\S+',),
      'end':('\)','}','>','\s','$'),
      }
      
_or = lambda some_list: "|".join(some_list)
_url_regex = _make_regexp('((%s)(%s)(%s))'%(_or(ok['start']), _or(ok['middle']), _or(ok['end'])))
_domain_regex = re.compile(r'(\w[-\w\.]+\.(%s)/?)\b' % (TOP_LEVELS,))
    
_mailto_regex = _make_regexp('((%s)(\S+@\S+\.\S+)(%s))' % (_or(ok['start']), _or(ok['end'])))

                                          
def addhrefs(text, return_everything=0, 
             emaillinkfunction=_makeMailLink,
             urllinkfunction=_makeLink):
    
    if not callable(emaillinkfunction):
        if emaillinkfunction is not None:
            _msg = "%r is not callable email link function"
            print >>sys.stderr, _msg%emaillinkfunction
        emaillinkfunction = _makeMailLink
    
    if not callable(urllinkfunction):
        if urllinkfunction is not None:
            _msg = "%r is not callable URL link function"
            print >>sys.stderr, _msg%urllinkfunction
        urllinkfunction = _makeLink
    
    info_emails = []
    info_urls = []
    
    
    urls = _url_regex.findall(text)
    for each in urls:
        whole, start, url, end = each
        if whole.endswith('">') or whole.endswith("'>"):
            # reject it because it looks like it's taken out of a tag
            continue
        if whole.endswith('<'):
            # the next thing is a tag, if that tag is a </a>
            # the chicken out!
            pos = text.find(whole)
            if text[pos+len(whole)-1:pos+4+len(whole)] == '</a>':
                continue
            
        url = _massageURL(url)
        
        if _rejectURL(url, start):
            continue
        link = urllinkfunction(url)
        if return_everything:
            info_urls.append((url, link))
        better = whole.replace(url, link)
        text = text.replace(whole, better, 1)
    
    replacements = {}
    for match in _domain_regex.finditer(text):
        whole = match.group()
        
        if text[match.start()-2:match.start()] == '//':
            # the domain name we have found is preceeded by two slashes
            # like this http://(m.domain.com) for example. 
            # If this is the case don't bother with it
            continue
        
        elif text[match.start()-1:match.start()] == '@':
            # the found domain was part of an email address
            continue
        
        elif '..' in match.group().split('?')[0]:
            # The regular expression for domain is [\w\.]+ so if we find 
            # something like '..foo.com' it can't be a real domain name
            continue
        
        # Now we've found a domain but where does it end? 
        # There might be a query string after it like this
        # 'm.cnn.com?a=b'
        end = pos = match.end()
        try:
            while text[pos] not in ('<',')','}',']','\t','\n',' '):
                pos += 1
        except IndexError:
            # reached the end
            pass
            
        # we have now reached the end of the domain name plus any
        # possible query string
        if text[pos:pos+4] == '</a>':
            # if the text was originally this:
            # 'bla www.moneyvillage.com bla'
            # it would first be converted to 
            # 'bla <a href="http://www.moneyvillage.com">www.moneyvillage.com</a> bla'
            # and then we don't want to touch it
            continue
        
        if '@' in text[end:pos]:
            # if something domainish existed that later turns out to be 
            # an email address the we have to skip it.
            # For example, we focus on 'm.google.com@gmail.com' then it will
            # spot 'm.google.com' but when going till the end of the string
            # what we have is what looks like an email address
            continue
            
        url = whole + text[end:pos]
        
        link = urllinkfunction(url)
        if return_everything:
            info_urls.append((url, link))

        replacements[url] = link

    # this crazy sort makes sure we do the shortest text pieces first
    for bad, good in sorted([(b,g) for (b,g) in replacements.items()],
                             lambda x,y: cmp(len(x[0]), len(y[0]))):
        text = text.replace(bad, good, 1)
        

    mails = _mailto_regex.findall(text)
    for each in mails:
        whole, start, url, end = each
        url = _massageURL(url)
        if _rejectEmail(url, start):
            continue
        if url.find(':') > -1:
            link = urllinkfunction(url)
            if return_everything:
                info_urls.append((url, link))
            better = whole.replace(url, link)
        else:
            link = emaillinkfunction(url)
            info_emails.append((url, link))
            better = whole.replace(url, link)
        text = text.replace(whole, better)        

    if return_everything:
        return text, info_urls, info_emails
    else:
        return text



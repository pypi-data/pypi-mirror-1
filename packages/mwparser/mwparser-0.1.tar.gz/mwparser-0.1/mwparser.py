# Learning unit testing from http://www.onlamp.com/pub/a/python/2004/12/02/tdd_pyunit.html

# Nested lists!  Especially nested <ul>s, but nested <ul> in <ol> and vice versa is great too
import re
import unittest

def find_lists(start_marker, tag, para):
    ''' Input: A bunch of junk
    Output: None if no modification done,
    otherwise return (formatted_line, unformatted_remainder) '''
    unformatted_remainder = ''
    ret = ''
    assert('<' not in tag and '>' not in tag, "sample tag is 'ol'")
    assert(len(start_marker) == 1, "This code assumes start_marker's length is 1")
    # look for a list
    if para.strip() and para[0] == start_marker:
        # then it's a list entry
        ul = ''
        maybe_lis = para.split('\n')
        while maybe_lis:
            maybe_li = maybe_lis[0]
            if maybe_li and maybe_li[0] == start_marker:
                # FIXME: What's the right behavior for nesting
                # lists?  <ul><li><ul><li>?  Do I need to be aware
                # of nesting between paras?
                li = maybe_li[1:].strip()
                ul += "<li>" + li + "</li>"
                maybe_lis = maybe_lis[1:]
            else:
                unformatted_remainder += '\n'.join(maybe_lis)
                maybe_lis = []
        ret += '<%s>' % tag + ul + '</%s>' % tag
        return (ret, unformatted_remainder)

def handle_section(s):
    ''' Input: some string
    Output: None if no modification done,
    otherwise return (formatted_line, unformatted_remainder) '''
    useful = False
    if '\n' not in s:
        s += '\n' # Evil :-)
    firstline, rest = s.split('\n', 1)
    equals, chomped = chomp_equals(firstline)
    if 1 <= equals <= 5:
        useful = True
        firstline = '<h%d>%s</h%d>' % (equals, chomped, equals)
    if useful:
        return (firstline, rest)

def chomp_equals(s):
    ''' Input: == zomg ==,
    Output: (2, "zomg")'''
    chomped = s
    equals = 0
    while chomped and (chomped[0] == chomped[-1] == '='):
        chomped = chomped[1:-1]
        equals += 1
    return (equals, chomped.strip())

class WikiMarkup:
    def __init__(self, s = ''):
        s = s.replace('<', '\0&lt;\0') # Padded with \0 to prevent
        s = s.replace('>', '\0&gt;\0') # their accidental splitting.
        # FIXME: Evil.  I should be creating a DOM or something.
        if type(s) == unicode:
            self.s = s
        else:
            self.s = unicode(s, 'utf-8')
    def render(self):
        urlregex = r"http://([\w./+\-=&#~?]*)"
        ret = ""
        paragraphs = re.split(r'\n', self.s) # That's right, eat that whitespace
        while paragraphs:
            para = paragraphs.pop(0)
            # check for '\n\n' condition, too
            grow_more = True
            while paragraphs and grow_more:
                # check for \n\n condition
                if para.strip() == '' and paragraphs[0].strip() == '':
                    grow_more = False
                    break
                # Good, so now we check if the next paragraph is of the same type as this one
                # if so, slurp it in
                for fn in handle_section, lambda s: find_lists('*', 'ul', s), \
                    lambda s: find_lists('#', 'ol', s):
                    if fn(para):
                        if fn(paragraphs[0]):
                            para += '\n' + paragraphs.pop(0)
                            break
                    
                else:
                    grow_more = False
            para = re.sub(r"''(.*?)''", r"<em>\1</em>", para)
            # square bracket links
            # First look for ]
            newpara = '' # Grow into here

            # First look for ]]
            subsplitted = para.split(']]')
            for subelt in subsplitted:
                internal = re.sub(r"\[\[(.*)", r'<a href="\1">\1</a>', subelt)
                if internal != subelt:
                    newpara += internal
                else:
                    splitted = subelt.split(']')
                    # Run regex sub on elements
                    namedlinkre = r'\[' + urlregex + ' ' + r'(.+)'
                    for elt in splitted:
                        named = re.sub(namedlinkre, r'<a href="http://\1">\2</a>', elt)
                        if named != elt:
                            newpara += named
                        else: # if no change
                            linked = re.sub(urlregex, r'<a href="http://\1">http://\1</a>', elt)
                            newpara += linked
                            if not (elt is splitted[-1]): # FIXME: "is" check is wrong for ''
                                newpara += ']'
            para = newpara
            # look for section-ness
            hope = handle_section(para)
            if hope:
                formatted, remainder = hope
                ret += formatted
                if hope:
                    para = '' # clear para so nothing later touches it
                    paragraphs.insert(0, remainder)
            # look for ULs
            hope = find_lists('*', 'ul', para)
            if hope:
                formatted, remainder = hope
                ret += formatted
                if hope:
                    para = ''
                    paragraphs.insert(0, remainder)

            # look for OLs
            hope = find_lists('#', 'ol', para)
            if hope:
                formatted, remainder = hope
                ret += formatted
                if hope:
                    para = ''
                    paragraphs.insert(0, remainder)

            # look for a PRE
            if para.strip() and para[0] == ' ':
                pre_so_far = []
                maybe_pres = para.split('\n')
                while maybe_pres:
                    maybe_pre = maybe_pres[0]
                    if maybe_pre and maybe_pre[0] == ' ':
                        pre = maybe_pre[1:]
                        pre_so_far.append(pre)
                        maybe_pres = maybe_pres[1:]
                    else:
                        paragraphs.insert(0, '\n'.join(maybe_pres))
                        maybe_pres = []
                ret += '<pre>' + '\n'.join(pre_so_far) + '</pre>'
                para = ''
            # otherwise
            if para:
                ret += '<p>' + para + '</p>'

        return ret.encode('utf-8')

# Here's our unit tests
class HunkOfTests(unittest.TestCase):
    def testNothing(self):
        self.checkMarkup("", "")

    def testPre(self):
        self.checkMarkup(' this\n and\n this\nshould be preformatted',
                         '<pre>this\nand\nthis</pre><p>should be preformatted</p>')

    def testUL(self):
        self.checkMarkup("* one\n* two\n*three\n\nfour",
                        "<ul><li>one</li><li>two</li><li>three</li></ul><p>four</p>")
        
    def testBoring(self):
        self.checkMarkup("Hey there!",
                         "<p>Hey there!</p>")

    def testBasicWikiLinks(self):
        self.checkMarkup("[[Live nude lesbians]]",
                         '<p><a href="Live nude lesbians">Live nude lesbians</a></p>')

    def testEmbeddedLinks(self):
        self.checkMarkup("http://www.google.com brotha",
                         '<p><a href="http://www.google.com">http://www.google.com</a> brotha</p>')

    def testEm(self):
        self.checkMarkup("''whoa!'' zomg",
                         "<p><em>whoa!</em> zomg</p>")

    def testParagraph(self):
        self.checkMarkup("Trapped across\n\nenemy newlines",
                         "<p>Trapped across</p><p>enemy newlines</p>")

    def testOrderedList(self):
        self.checkMarkup("# one\n#two\nthree",
                         "<ol><li>one</li><li>two</li></ol><p>three</p>")

    def testBullet(self):
        self.checkMarkup("* An albino\n\nA mosquito",
                         '<ul><li>An albino</li></ul><p>A mosquito</p>')

    def testBulletWithOneNewline(self):
        self.checkMarkup("* An albino\nA mosquito",
                         '<ul><li>An albino</li></ul><p>A mosquito</p>')

    def testUnicode2utf8(self):
        # guarantee: If you pass in Unicode, you'll get utf-8 out
        self.checkMarkup(u'\x85',
                         '<p>\xc2\x85</p>')

    def testutf8safety(self):
        # guarantee: If you pass in utf-8, you'll get utf-8 back
        self.checkMarkup('\xc2\x85',
                         '<p>\xc2\x85</p>')

    def testDifficultLink(self):
        self.checkMarkup("<http://fake-domain.org/~luser+bbq/showpost.php?p=525574&postcount=7#sect>",
                         '<p>\0&lt;\0<a href="http://fake-domain.org/~luser+bbq/showpost.php?p=525574&postcount=7#sect">http://fake-domain.org/~luser+bbq/showpost.php?p=525574&postcount=7#sect</a>\0&gt;\0</p>')

    def testLabeledLink(self):
        self.checkMarkup('[http://www.google.com/ Cthuu]gle',
                         '<p><a href="http://www.google.com/">Cthuu</a>gle</p>')

    # FIXME: To pass this cleanly, we need some smarter language than strings
    # for doing HTML/XML templating.
    def testEscaping(self):
        self.checkMarkup("6 < 7 < 8",
                         "<p>6 \0&lt;\0 7 \0&lt;\0 8</p>")

    def checkMarkup(self, markup, wanted):
        p = WikiMarkup(markup)
        got = p.render()
        self.assertEqual(got, wanted)

    def testPre(self):
        self.checkMarkup(' zomg prefor<matted>',
                         '<pre>zomg prefor\0&lt;\0matted\0&gt;\0</pre>')

    def testSection(self):
        self.checkMarkup("== zomg ==",
                         "<h2>zomg</h2>")

    def testParagraphUlSeparation(self):
        self.checkMarkup('zqomg\n* qbbq',
                         '<p>zqomg</p><ul><li>qbbq</li></ul>')

    def testHeaderUlSeparation(self):
        self.checkMarkup('==zomg==\n* bbq\n=omg=',
                         '<h2>zomg</h2><ul><li>bbq</li></ul><h1>omg</h1>')

    def testLotsOfLinesBetweenUlAndH2(self):
        self.checkMarkup('* zomg\n\n\n==bbq==',
                         '<ul><li>zomg</li></ul><h2>bbq</h2>')

    def testComplicatedLink(self):
        self.checkMarkup('Sparta <http://www.mnot.net/sw/sparta/>',
                         '<p>Sparta \x00&lt;\x00<a href="http://www.mnot.net/sw/sparta/">http://www.mnot.net/sw/sparta/</a>\x00&gt;\x00</p>')

def main():
    unittest.main()

if __name__ == '__main__':
    main()

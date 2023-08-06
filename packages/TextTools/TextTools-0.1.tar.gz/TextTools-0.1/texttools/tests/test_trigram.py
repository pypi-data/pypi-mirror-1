import unitest

class TestTriGram(unittest.TestCase):

    def test_lang(self):
        en = Trigram('http://gutenberg.net/dirs/etext97/lsusn11.txt')
    #NB fr and some others have English license text.
        #   no has english excerpts.
        fr = Trigram('http://gutenberg.net/dirs/etext03/candi10.txt')
        fi = Trigram('http://gutenberg.net/dirs/1/0/4/9/10492/10492-8.txt')
        no = Trigram('http://gutenberg.net/dirs/1/2/8/4/12844/12844-8.txt')
        se = Trigram('http://gutenberg.net/dirs/1/0/1/1/10117/10117-8.txt')
        no2 = Trigram('http://gutenberg.net/dirs/1/3/0/4/13041/13041-8.txt')
        en2 = Trigram('http://gutenberg.net/dirs/etext05/cfgsh10.txt')
        fr2 = Trigram('http://gutenberg.net/dirs/1/3/7/0/13704/13704-8.txt')
        print "calculating difference:"
        print "en - fr is %s" % (en - fr)
        print "fr - en is %s" % (fr - en)
        print "en - en2 is %s" % (en - en2)
        print "en - fr2 is %s" % (en - fr2)
        print "fr - en2 is %s" % (fr - en2)
        print "fr - fr2 is %s" % (fr - fr2)
        print "fr2 - en2 is %s" % (fr2 - en2)
        print "fi - fr  is %s" % (fi - fr)
        print "fi - en  is %s" % (fi - en)
        print "fi - se  is %s" % (fi - se)
        print "no - se  is %s" % (no - se)
        print "en - no  is %s" % (en - no)
        print "no - no2  is %s" % (no - no2)
        print "se - no2  is %s" % (se - no2)
        print "en - no2  is %s" % (en - no2)
        print "fr - no2  is %s" % (fr - no2)

        print "\nmaking up English"
        print en.make_words(30)
        print "\nmaking up French"
        print fr.make_words(30)




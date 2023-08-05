""" cocoonhelpers.py """



import urllib
import re

normal=re.compile('^\s*(?:http:\/\/)?(.*?)(?:\/?)$')




class OpenIdName(object):
    
    def __init__(self,open_id_name):
        self.name=open_id_name
        
    def normalize(self):
        """ retire la composante http:// et le dernier /
            
        """
        m=normal.match(self.name)
        if m:
            return m.group(1)
        else:
            return self.name

    def no_slash(self):
        """ normalize + transforme les / en _-_       """
        return self.normalize().replace('/','_-_')

    def wiki_word(self):
        """ tranforme en wikiword """
        word=self.normalize().replace('/','.')
        words=word.split('.')
        if len(words)==1:
            return words[0]
        wikiword=''
        #return words
        for word in words:
            word=word.lower()
            capitalized=word[0].upper()+word[1:]
            wikiword=wikiword+capitalized
        return wikiword

if __name__ == "__main__":


    for url in [ "  http://cocoon.myopenid.com/",
                 "cocoon.myopenid.com",
                 "openid.orange.com/cocoon/",
                 "cocoon",
                "CocoonMyopenIdCom",
                "OpenidOrange_-_cocoon"
                
                ]:
    
        print OpenIdName(url).wiki_word()


        
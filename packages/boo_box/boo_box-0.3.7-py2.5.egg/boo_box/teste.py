import boo_box
import simplejson

#boo = boo_box.Box('submarinoid','248960').getXML('livros javascript')
boo = boo_box.Box('submarinoid','248960').getJSON('livros javascript').replace('jsonBooboxApi(','')
#boo = 'jsonBooboxApi({"shop":"unifilmeid","uid":null,"groupid":"0","defaulttags":"searchterms","item":null})'
json = simplejson.loads(boo[:-1])
for item in json['item']:
    print(item)


from flask import Flask
from flask import request
from flask import render_template
from flask import *
import nltk
from nltk.corpus import stopwords
from Bio import Entrez, Medline
from collections import Counter

app = Flask(__name__)
@app.route('/')

def webIntro(): 
    return render_template( './index.html' )
	
def findArticles(zoekwoord):
	handle = Entrez.esearch(db="pubmed", term=zoekwoord, mindate='2000', usehistory='y', retmax='100000')
	record = Entrez.read(handle)
	ID = record["IdList"]
	count = record["Count"]
	print (ID, count)
	return (ID, count)

def getAbstracts(ID, count):
	abstracts = []
	keys = []
	auteur = []
	datum = []
	titel = []
	handle = Entrez.efetch(db="pubmed", id=ID, rettype ='Medline', retmode='text' )
	record = Medline.parse(handle)
	for ab in record:
		auteur.append(ab.get('AU'))
		abstracts.append(ab.get('AB'))
		datum.append(ab.get('DP'))
		titel.append(ab.get('TI'))
		if ab.get('OT')== None:
			keys.append("-")
		else:
			keys.append(ab.get('OT'))
	return (keys, abstracts, auteur, datum, titel)

def mining(ab):
	tokens = nltk.word_tokenize(str(ab))
	set_tokens = sorted(set(tokens))
	stem = []
	porter = nltk.stem.porter.PorterStemmer()
	for token in set_tokens:
		if len(token) > 3:
			stem.append(porter.stem(token.lower()))
	stops = set(stopwords.words("english")) 
	filtered_words = [word for word in stem if word not in stops]
	return filtered_words

def frequentie(filtered_words):
	c = Counter()
	for word in filtered_words:
		c[word] +=1
	print(c.most_common(25))

def tabel(ID, auteur, keys, datum, titel):

	tablet = """"""
	aantal = 0
	for item in ID:
		url = ("http://www.ncbi.nlm.nih.gov/pubmed/%s" % str(item))
		regel="<tbody><tr><td><font color=""black""><a href="+url+" target=""_blank""></font>"+str(item)+"</a></td><td>"+str(titel[aantal])+"</td><td>"+", ".join(auteur[aantal])+"</td><td>"+str(datum[aantal])+"</td><td><div class=""comment more"">"+", ".join(keys[aantal])+"</div></td></tbody>"
		tablet+=regel
		aantal+=1
	return tablet

@app.route('/tabel', methods=["GET"])
def tabelWeergeven():
	zoekwoord = request.args.get("zoekwoord")
	Entrez.email = "your.email@example.com"   
	webIntro()
	ID, count = findArticles(zoekwoord)
	keys, abstracts, auteur, datum, titel = getAbstracts(ID, count)
	for ab in abstracts:
		filtered_words = mining(ab)
	frequentie(filtered_words)
	return render_template('table.html', zoekwoord = zoekwoord, tabel= tabel(ID, auteur, keys, datum, titel))

def visualisatieWeergeven():
	tabelWeergeven()
	return render_template('visualisatie.html')

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)

tabelWeergeven()

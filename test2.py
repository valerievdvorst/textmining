from flask import Flask
from flask import request
import nltk
from nltk.corpus import stopwords
from Bio import Entrez, Medline
from collections import Counter

app = Flask(__name__)
@app.route('/')

def webIntro():
	html1 = """<html> 
	<link rel="shortcut icon" href="data:image/x-icon;," type="image/x-icon"> 
	<title>Tabel</title> 
		<head>
			<form action = "/tabel"> 
			<H1> Voer hier het zoekwoord in: </H1> 
			<center>
			 <form action="/tabel" method="get"><input type="zoekwoord" name="zoekwoord" id="zoekwoord" placeholder="zoekwoord:"><br>
			<input type=submit value=submit> </center>

			<STYLE TYPE="text/css">
				body { background-color:#FFE4C4}
				H1 { font-family: sans-serif; font-size: 50px; text-align: center;}

				
				tr:hover{background-color:#ff6347}
				
				th {
			    background-color: #dc143c;
			    color: white;
			}
			</STYLE>"""

	return html1
	
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

""""""
def tabel(ID, auteur, keys, datum, titel):
	html = """
	<script type="text/javascript">

		var socket = io.connect("http://127.0.0.1:5000"); 	

		function searchRows(table1) {
		var tbl = document.getElementById(table1);
		var headRow = tbl.rows[0];
		var arrayOfHTxt = new Array();
		var arrayOfHtxtCellIndex = new Array();

		for (var v = 0; v < headRow.cells.length; v++) {
		if (headRow.cells[v].getElementsByTagName('input')[0]) {
		var Htxtbox = headRow.cells[v].getElementsByTagName('input')[0];
		if (Htxtbox.value.replace(/^\s+|\s+$/g, '') != '') {
		arrayOfHTxt.push(Htxtbox.value.replace(/^\s+|\s+$/g, ''));
		arrayOfHtxtCellIndex.push(v);
		}
		}
		}

		for (var i = 1; i < tbl.rows.length; i++) {

			tbl.rows[i].style.display = 'table-row'; 

			for (var v = 0; v < arrayOfHTxt.length; v++) {

				var CurCell = tbl.rows[i].cells[arrayOfHtxtCellIndex[v]];
				var CurCont = CurCell.innerHTML.replace(/<[^>]+>/g, "");
				var reg = new RegExp(arrayOfHTxt[v] + ".*", "i");

				if (CurCont.match(reg) == null) {

					tbl.rows[i].style.display = 'none';

		}

		}

		}
		}
		</script>  </head>
		<body >

		</script>
		</body>

		</html>
"""
	tabel= """	<STYLE TYPE="text/css">
	body { background-color:#FFE4C4}
	H1 { font-family: sans-serif; font-size: 50px; text-align: center;}

	
	tr:hover{background-color:#ff6347}
	
	th {
    background-color: #dc143c;
    color: white;
}
	
<script>
			$(document).ready(function() {
				var showChar = 100;
				var moretext = "meer";
				var lesstext = "minder";
				var ellipsesText = "...";
				$('.more').each(function() {
					var content = $(this).html();

					if(content.length > showChar) {

						var c = content.substr(0, showChar);
						var h = content.substr(showChar-1, content.length - showChar);

						var html = c + '<span class="moreellipses">' + ellipsesText + '&nbsp;</span><span class="morecontent"><span>' + h + '</span>&nbsp;&nbsp;<a href="" class="morelink">' + moretext + '</a></span>';
						$(this).html(html);
					}

				});

				$(".morelink").click(function(){
					if($(this).hasClass("less")) {
						$(this).removeClass("less");
						$(this).html(moretext);
					} else {
						$(this).addClass("less");
						$(this).html(lesstext);
					}
					$(this).parent().prev().toggle();
					$(this).prev().toggle();
					return false;
				});
			});
			</script>
	
	</style>

	<table border='1' id='table1' class="tbl" cellspacing="0" cellpadding="0">
	<thead>
	<tr>
	<th scope="col" >PubmedID
	<input id="txtPrjName" onkeyup="searchRows('table1')" type="text" placeholder="Pubmed ID"/> </th>
	<th scope="col"> Titel
	<input id="txtPrjName" onkeyup="searchRows('table1')" type="text" placeholder="Zoeken op titel"/>
	</th>
	<th scope="col"> Auteur
	<input id="txtPrjName" onkeyup="searchRows('table1')" type="text" placeholder="Zoeken op auteur"/>
	</th>
	<th scope="col">Datum
	<input id="txtPrjName" onkeyup="searchRows('table1')" type="text" placeholder="Zoeken op datum"/>
	</th>
	<th scope="col" >Keywords
	-<input id="txtPrjName" onkeyup="searchRows('table1')" type="text" placeholder="Zoeken op keywords"/>
	</th>
	</tr>
	</thead>"""

	aantal = 0
	for item in ID:
		url = ("http://www.ncbi.nlm.nih.gov/pubmed/%s" % str(item))
		regel="<tbody><tr><td><a href="+url+">"+str(item)+"</a></td><td>"+str(titel[aantal])+"</td><td>"+", ".join(auteur[aantal])+"</td><td>"+str(datum[aantal])+"</td><td><div class=""comment more"">"+", ".join(keys[aantal])+"</div></td></tbody>"
		tabel+=regel
		aantal+=1

	tabel+="</table>"
	html+=tabel
	return html 

@app.route('/tabel', methods=["GET"])
def main():
	zoekwoord = request.args.get("zoekwoord")
	Entrez.email = "your.email@example.com"   
	webIntro()
	#zoekwoord = input("Voer hier het zoekwoord in: ")
	ID, count = findArticles(zoekwoord)
	keys, abstracts, auteur, datum, titel = getAbstracts(ID, count)
	for ab in abstracts:
		filtered_words = mining(ab)
	frequentie(filtered_words)
	return tabel(ID, auteur, keys, datum, titel)


if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)

main()

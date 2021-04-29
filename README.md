# kb_aliases_cleaner

Účelem nástroje kb_aliases_cleaner je vyčistit znalostní bázi od mnohočetných jednoslovných aliasů.
Více informací lze nalézt na interní wiki stránce: [Ner bug fixing](https://knot.fit.vutbr.cz/wiki/index.php/Ner_bug_fixing#Odstran.C4.9Bn.C3.AD_jednoslovn.C3.BDch_alias.C5.AF_.28xkrizd03.290=)

Spuštění
--------
	./start.sh [options]
	možnosti spuštění:
		-h			Vypisuje možnosti programu
		-k			Stáhne novou znalostní bázi ze zdroje
		-t THRESHOLD		Změní hodnotu prahu pro vyřazení aliasů (implicitně 2)
		--destory		Desktruktivní spuštění skriptu
		--debug			Spustí program v debug módu
		--input-file FILE	Cesta ke vstupní znalostní bázi (implicitně ./KB.tsv)
		--output-file FILE	Cesta k výstupní znalostní bázi (implicitně ./KB.tsv)

Debug mod
---------
Vytvoří navíc diagnostické soubory obsahující údaje o zjištěných aliasech, jejich počtech, zdrojích apod.

# kb_aliases_cleaner

Účelem nástroje kb_aliases_cleaner je vyčistit znalostní bázi od mnohočetných jednoslovných aliasů.

Spuštění
--------
	./start.sh [options]
	možnosti spuštění:
		-h					Vypisuje možnosti programu
		-k					Stáhne novou znalostní bázi ze zdroje
		-d					Spustí program v debug módu
		-t THRESHOLD		Změní hodnotu prahu pro vyřazení aliasů (implicitně 3)
		--input-file FILE	Cesta ke vstupní znalostní bázi (implicitně ./KB.tsv)
		--output-file FILE	Cesta k výstupní znalostní bázi (implicitně ./KB.tsv)

Debug mod
---------
Vytvoří navíc diagnostické soubory obsahující údaje o zjištěných aliasech, jejich počtech, zdrojích apod.

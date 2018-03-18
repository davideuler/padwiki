#XMLBZ2 = enwiki-20091103-pages-articles.xml.bz2
#XMLBZ2 = enwikibooks-20100222-pages-articles.xml.bz2
#XMLBZ2 = enwikiquote-20080417-pages-articles.xml.bz2
#XMLBZ2 = enwiktionary-20080315-pages-articles.xml.bz2
#XMLBZ2 = ent0803.bz2
#XMLBZ2 = zh-0804.bz2
XMLBZ2 = zh1001.bz2

.PHONY:	inform wikipedia split mediawiki

all:	inform

inform:
	@echo Make sure you have Python, Perl, PHP5 and Xapian and Django installed
	@echo after that, put ${XMLBZ2} in the wiki-splits directory and \'make wikipedia\'
	@echo you may build index step by step, make split, make indexinput, make index

wikipedia: split indexinput index

split:
	@mkdir -p wiki-splits
	@find wiki-splits -type f -iname rec\*  -exec rm -f '{}' ';'
	@cd wiki-splits && bzip2recover ${XMLBZ2} 
	@echo Perfect, spliting done

index:
	@rm -rf db.lucene
	@echo task begin at `date` for lucene index
	@cat indexinput.txt | java -Xms256m -Xmx1024m -jar WikiIndexer.jar
	@echo task end at `date` for lucene index
	@echo index made successfully!
	@echo To run your local wikipedia, just
	@echo
	@echo cd mywiki
	@echo python manage.py runserver
	@echo
	@echo ... and point your browser to http://localhost:8000/

indexinput:
	@rm -rf db/
	@echo task begin at `date` for index input generating
	#@cd wiki-splits && rm -rf db && for i in rec*.bz2 ; do echo \#$$i ; bzcat $$i | grep '<title' | perl -ne 'm/<title>([^<]+)<\/title>/ && print $$1."\n";' ; done | ../quickstartindex
	#commented, and modified by David Lv, 2010/02/27, don't need to grep before using perl to extract title from line :
	#@cd wiki-splits && rm -rf db && for i in rec*.bz2 ; do echo \#$$i ; bzcat $$i | perl -ne 'm/<title>([^<]+)<\/title>/ && print $$1."\n";'  ; done | ../quickstartindex
	@cd wiki-splits && for i in rec*.bz2 ; do echo \#$$i ; bzcat $$i | perl -ne 'm/<title>([^<]+)<\/title>/ && print $$1."\n";'  ; done  > ../indexinput.txt
	@echo end at `date` for index input generating
	@echo indexinput made successfully!


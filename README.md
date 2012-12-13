## Wikia NLP Library ##
These are scripts that use data available on Wikia for natural language processing.
The results of these scripts can be reused for a variety of purposes 
(e.g. improved search relevance, customer support, new features)

Written for the Wikia December 2012 Hackathon

## Requirements ##
* [NLTK](http://nltk.googlecode.com)
* [Pattern](https://github.com/clips/pattern)
* [Summarize](https://github.com/thavelick/summarize)

## Scripts ##

* '''get-sentiment.py''' -- A script that accesses text from Solr for a given wiki and namespace
and determines the average sentiment (positive/negative) and objectivity (subjective/objective).
* '''get-named-entities.py''' -- A script that accesses all named entities for a document
* '''summarize-doc.py''' -- Summarizes the text of one or more documents

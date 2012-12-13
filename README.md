## Chompsky - Wikia NLP Library ##
![Imgur](http://i.imgur.com/uBV0r.jpg)

These are scripts that use data available on Wikia for natural language processing.
The results of these scripts can be reused for a variety of purposes 
(e.g. improved search relevance, customer support, new features)

This is named after a goofy drawing I made one time of Noam Chomsky.
And also because it chomps through text. Take your pick.
This project in no way endorses Chomsky's views on linguistics. In fact, it flouts it.

Written for the Wikia December 2012 Hackathon

## Requirements ##
* [NLTK](https://github.com/nltk/nltk)
* [NLTK Contrib](https://github.com/nltk/nltk)
* [Pattern](https://github.com/clips/pattern)
* [Summarize](https://github.com/thavelick/summarize)

## Scripts ##

* **get-sentiment.py** -- A script that accesses text from Solr for a given wiki and namespace
and determines the average sentiment (positive/negative) and objectivity (subjective/objective).
* **get-named-entities.py** -- A script that accesses all named entities for a document
* **summarize-doc.py** -- Summarizes the text of one or more documents

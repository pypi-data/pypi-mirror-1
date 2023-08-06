BigramSplitter
------------------------------

Specification:
Text character normalization process uses Python unicodedata.
Convert full-width numeric and alphabet character into half-width equivalent.
Convert half-width Katakana into full-width equivalent.
Therefore all of above character variations can be recognized as same ones.

Language Specifications:

- Chinese

 - No space between words.
 - There is only Kanji(Chinese) character
 - Process	with Bigram(2-gram) model

- Japanese

 - No space between words
 - Combination 0f Kanji(Chinese), Katakana, and Hiragana character

- Korean

 - There are spaces between words, but it contains a particle
 - Combination of Korean alphabet and Kanji(Chinese) character
 - Discriminate Korean alphabet and Kanji(Chinese) character and processed with Bigram(2-gram) model

- Thai

 - No space between words
 - It's very difficult to handle this language in a computer
 - A vowel and a consonant are registered in Unicode separately so that it is difficult to recognize as one word.
 - However, there is a possibility of dealing with Thai characters to use Bigram(2-gram) model.

- Other languages (Including English)

 - There is a space between words

 - It is indexed each word

Notes:

- Source Code

  Since no documents are available on how to develop 'word splitter', we refer to other splitter source code. But I still have a number of questions. If you have any more information, please feel free let us know.

- Hotfix to Plone 3.0 source code

  Because Plone 3.x catalog setting, catalog.xml, doesn't have existing index overwrite mechanism, we developed hotfix and added XML attribute. We believe Plone 3 XML define mechanism is simple and clear, so that we take this approach. We appreciate any comment.


Installation
-----------------
Use zc.buildout
===============
- Add ``Products.BigramSplitter`` to the list of eggs to install, e.g.::

    [buildout]
    ...
    eggs =
        ...
        Products.BigramSplitter
       
- Tell the plone.recipe.zope2instance recipe to install a ZCML slug::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        Products.BigramSplitter
      
- Re-run buildout, e.g. with::

    $ ./bin/buildout

- Restart Zope
- Plone setting -- Add on products  -- Quick install


Old Style
=========
- Untar downloaded file, then copy to 'Products' directory of your Plone instance.
- Restart Zope
- Plone setting -- Add on products  -- Quick install


Required
--------
- Plone3.0.x or higher

License
--------
- See docs/LICENSE.txt

Author
------
- CMScom http://www.cmscom.jp/

 - Manabu Terada  e-mail : terada@cmscom.jp
 - Mikio Hokari
 - Naoki Nakanishi
 - Naotaka Hotta
 - Takashi Nagai

To Do
------
- Add re-install mechanism
- Supports more languages

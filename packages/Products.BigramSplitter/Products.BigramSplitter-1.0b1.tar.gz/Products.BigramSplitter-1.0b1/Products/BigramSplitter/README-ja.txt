BigramSplitter
------------------------------

Description:

Ploneに置ける、東アジア言語を中心に、全世界の言語が検索対象になることを目的としているプロダクト

仕様:
- 文字のノーマライズ処理

    - Pythonのunicodedata にてノーマライズ処理を行っている

        - 全角英数字を半角英数字に変換
        - 半角カタカナを全角カタカナに変換
        - よって、これらは同一視される

- 各言語の対応

    - 中国語

        - 単語間にスペースが存在しない。
        - 漢字のみである。
        - Bigram(2-gram)処理をしている。

    - 日本語

        - 単語間にスペースが存在しない。
        - 漢字、ひらがな、カタカナがある。

    - 韓国語

        - 単語間にスペースは有るが、助詞を含んでいる。
        - ハングル、漢字がある。
        - ハングルと漢字を分け、それぞれで、Bigram(2-gram)処理をしている。

    - タイ語

        - 単語間にスペースがない。
        - 表記がむずかしく、コンピュータ処理も難しいようだ。
        - Unicodeには、母音と子音がばらばらに登録されている。よって、1文字をとらえるのが難しい。
        - しかし、Bigram(2-gram)処理をし、順序がつくのでこれで検索が出来るのではないかと思っている。

    - その他(英語を含む)

        - 単語間にスペースがある。
        - スペースで文字を区切ってインデックス化している。

- 気になっている点

    - ソースコード

      Word Splitter の作り方がきちんと説明されている文書がなく、各種Splitterのコードを参考にした。なぜそうなのかという点で疑問が残っている箇所もある。情報お持ちの方はぜひご連絡下さい。

    - Ploneのコード改造

      Plone3.x の「カタログ」を設定する、catalog.xml の仕様で、既にあるインデックス名を上書きする仕組みが無かった。その為、出来るようにHotfixを当て、XMLの属性を追加している。これについては、Plone3.x のXML設定が明快でわかりやすいと考えているために、その様な拡張をしている。これは議論の分かれるところだと認識している。


Installation
------------
zc.buildoutを使う場合
======================
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


旧スタイルの場合
============
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

  - Manabu Terada
  - Mikio Hokari
  - Naoki Nakanishi  
  - Naotaka Hotta
  - Takashi Nagai


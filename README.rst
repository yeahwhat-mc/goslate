Goslate: Free Google Translate API
##################################################

.. contents:: :local:

``goslate`` provides you *free* python API to google translation service by querying google translation website.

It is:

- **Free**: get translation through public google web site without fee
- **Fast**: batch, cache and concurrently fetch
- **Simple**: single file module, just ``Goslate().translate('Hi!', 'zh')``


Usage
======

.. sourcecode:: python

 >>> import goslate
 >>> gs = goslate.Goslate()
 >>> print gs.translate('hello world', 'de')
 hallo welt

 
For romanlized writing (romanlization), batch translation, language detection, proxy support etc., please check `API reference <http://pythonhosted.org/goslate/#module-goslate>`_
 
 
Install
========

goslate support both Python2 and Python3. You could install it via:


.. sourcecode:: bash
  
  $ pip install goslate

 
or just download `latest goslate.py <https://bitbucket.org/zhuoqiang/goslate/raw/tip/goslate.py>`_ directly and use

``futures`` `pacakge <https://pypi.python.org/pypi/futures>`_ is optional but recommended to install for best performance in large text translation task.


CLI
===========

``goslate.py`` is also a command line tool
    
- Translate ``stdin`` input into Chinese in GBK encoding

  .. sourcecode:: bash
  
     $ echo "hello world" | goslate.py -t zh-CN -o gbk

- Translate 2 text files into Chinese, output to UTF-8 file

  .. sourcecode:: bash
  
     $ goslate.py -t zh-CN -o utf-8 source/1.txt "source 2.txt" > output.txt

     
use ``--help`` for detail usage
     
.. sourcecode:: bash
  
   $ goslate.py -h
     
     
How to Contribute
==================

- Report `issues & suggestions <https://bitbucket.org/zhuoqiang/goslate/issues>`_
- Fork `repository <https://bitbucket.org/zhuoqiang/goslate>`_
- `Donation <http://pythonhosted.org/goslate/#donate>`_

What's New
============

1.4.0
----------

* [fix bug] update to adapt latest google translation service changes


1.3.2
----------

* [fix bug] fix compatible issue with latest google translation service json format changes

* [fix bug] unit test failure



1.3.0
---------

* [new feature] Translation in roman writing system (romanlization), thanks for Javier del Alamo's contribution.
  
* [new feature] Customizable service URL. you could provide multiple google translation service URLs for better concurrency performance

* [new option] roman writing translation option for CLI
  
* [fix bug] Google translation may change normal space to no-break space

* [fix bug] Google web API changed for getting supported language list

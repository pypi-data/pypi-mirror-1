# -*- coding: utf-8 -*-

"""Release information"""


version = "1.2"
author = "Fred Lin"
email = "gasolin+zhpy@gmail.com"
copyright = "Copyright 2007 Fred Lin and contributors"
license = "MIT <http://www.opensource.org/licenses/mit-license.php>"
url = "http://code.google.com/p/zhpy/"
download_url="http://code.google.com/p/zhpy/"
description="Write python language in chinese"
long_description = """
.. contents::
  :depth: 2

Introduction
--------------

"If it walks like a duck and quacks like a duck, I would call it a duck."

Zhpy acts like python and play like python, you (chinese users)

could use it as python.

Zhpy is the full feature python language with fully tested chinese

keywords, variables, and parameters support. Independent on python

version, bundle with command line tool, chinese shell script capability,

interpreter, pluggable keyword system,

bi-directional zhpy <-> python code translation, and great document.

Zhpy on python is good for Taiwan and China beginners to learn python in

our native language (Traditional and Simplified chinese).

The core of zhpy is a lightweight python module and a chinese
source convertor based on python, which provides interpreter and
command line tool to translate zhpy code to python.

zhpy integrated a setuptools-based plugin system and in-place ini reference
feature for keyword reuse.

The zhpy code written in traditional and simplified chinese could be
translated and converted to natual python code.
Thus it could be execute as nature python code and be used in
normal python programs.

Normal python programs could be translated to traditional(.twpy) or
simplified(.cnpy) chinese zhpy source via 'zhpy' command line tool.

You could use 'zhpy' command instead of "python" in command line to execute
source code wrote in either Chinese or English.

Zhpy also provide a method 'zh_exec' that allow you to embed
chinese script in python; Zhpy could be used as the chinese
shell script as well.

Check examples here.

  * http://code.google.com/p/zhpy/wiki/ZhpyExample

Install
----------

You could use easy_install command to install zhpy::

    $ easy_install zhpy

or check instructions for detail.

  * http://code.google.com/p/zhpy/wiki/DownloadInstall

Usage
-------

You could use zhpy interpreter to test zhpy::

    $ zhpy
    >>> print 'hello in chinese'
    hello in chinese

Browse project homepage to get examples in chinese.

  * http://code.google.com/p/zhpy/

check the BasicUsage for detail.

  * http://code.google.com/p/zhpy/wiki/BasicUsage

Programming Guide
-------------------

An C.C licensed zhpy book "A Byte of Zhpy" is available on site.
You could freely view it online.

  * http://code.google.com/p/zhpy/wiki/ByteOfZhpy

The book is based on "A Byte of python".

  * http://swaroopch.info/text/Byte_of_Python:Main_Page

There's the API document available in zhpy download list, too.

  * http://code.google.com/p/zhpy/downloads/list

Change Log
-------------

You could view the ChangeLog to see what's new in these version.

  * http://zhpy.googlecode.com/svn/trunk/CHANGELOG.txt

"""

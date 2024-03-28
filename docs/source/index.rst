.. dataclient documentation master file, created by
   sphinx-quickstart on Fri Dec 27 16:19:45 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image::  _static/distribution_128px.ico


PyDaas
======

**高级的、易用的 气象大数据云平台 在线数据读取包**

> 大数据云平台常包含有各类常规和非常规观测资料、数值模式资料、服务产品等,
  数据格式多种多样，平台针对各类数据有不同的接口支持，使用时需要根据数据代码和该数据可用接口来获取数据，
  这要求我们在使用时打开网页平台进行一系列操作才能获取数据，在一定程度上增加了获取数据的复杂度。

PyDaas库通过对大数据云平台的Python SDK进行进一步封装来简化接口的调用和数据的获取，其设计理念和使用逻辑与
`PyMDFS <https://github.com/zjobsdev/PyMDFS>`_ 库保持一致，

1. 高度简化用户调用接口
2. 使用主流的pandas和xarray数据结构

.. toctree::
   :maxdepth: 3
   :caption: caption

   install
   quick_start
   script
   datasource
   api




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

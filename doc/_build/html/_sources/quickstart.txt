快速开始
========

安装和使用pasta非常简单。在安装前请确保Python版本在3.4之上，并已安装pip3。

要安装pasta，请打开Terminal，输入

``pip install pasta``

注意：如果本地环境中同时包含Python 2和Python 3，一般情况下需要指定pip版本。请以如下命令代替：

``pip3 install pasta``

**pasta不与Python 2兼容**，请特别注意。

要运行pasta，请转换路径到含有数据需求配置文档（*.datacfg文件）的目录下，运行：

``pasta it myconfig.datacfg``

只需片刻，即可在同样的目录下得到一个json文件，内含所有数据需求配置文档的内容，并包含数据结果。


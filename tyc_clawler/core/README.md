源代码地址：https://github.com/TeamWiseFlow/wiseflow
如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0

<!--------- 分割线 --------->

由于是配套代码，所以core和pb两个文件夹都要，但是没有进行很细的研究

wiseflow这个的pocketbase用的是我的账号密码，api key也是我的硅基流动的
至于想爬取什么数据，可以在运行run.ps1之后打开pocketbase的网页，在网页上进行操作管理即可

在终端上输入      cd tyc_clawler     进入tyc_clawler文件夹
在终端上输入      cd core            进入core文件夹
在终端上输入      pip install -r requirements.txt    下载依赖

打开run.ps1文件，运行run.ps1文件，即可开始爬取数据

在终端上CTRL + C 可退出程序

其他文件夹可看里面的readme文件，进行研究

<!--------- 分割线 --------->
不足： 爬取数据质量堪忧，不知道是提供的url地址问题还是提示词有问题，还是本来效果就是这样，或者是用其他代码（其他代码可见wiseflow原代码，我的是不全的）
      我没有写保存数据的代码，只在general_process.log有爬取的日志记录

<!--------- 分割线 --------->
暂时先这样，有什么以后再补充




# Broc是什么
broc是一款面向c/c++语言的构建工具，提供了编译、分支依赖、依赖模块下载等功能。不同于make, cmake等以库文件链接的编译方式，broc将依赖库源代码与程序源代码一并同时进行编译，这种方式可以避免程序源代码与依赖库编译选项或平台不一致导致的软件兼容性问题；broc支持编译结束后自动运行单元测试用例；借助Jenkins broc还能完成软件的[持续集成](https://en.wikipedia.org/wiki/Continuous_integration)

# Broc有那些优势

* **源码编译**          
broc支持将程序以及依赖库从源码状态进行编译，解决了c/c++程序因编译选项、操作系统平台或库文件版本不同而造成的兼容性问题；

* **代码自动下载**      
broc支持自动checkout[依赖模块][4]源代码到本地然后进行编译，用户无需编写控制脚本来实现此功能；

* **分支依赖**          
broc支持指定依赖库的主干、分支和TAG，broc能自动识别并解决库文件传递性依赖问题；

* **语法简单**      
Makefile复杂的语法让人望而却步，而broc语法简洁，易上手；

* **增量编译靠谱**      
make通过文件的修改时间来判断文件是否需要进行再编译，当文件版本回滚后或编译参数变更后，make不会对文件再次进行编译；broc除了使用文件的修改时间，还基于文件内容的哈希值以及编译参数作为增量编译的判断标准，增量编译的准确性会更高；

* **支持protobuf**      
broc内置对protobuf的支持，将proto文件编译成静态库.a文件一步完成

# 使用手册
https://github.com/baidu/broc/wiki/broc-tutorial

# 构建规范
https://github.com/baidu/broc/wiki/broc-manual

#反馈与技术支持
请联系broc@baidu.com

#欢迎加入
如果你热爱开源，对我们感兴趣，我们来聊聊吧 broc@baidu.com

# Contact

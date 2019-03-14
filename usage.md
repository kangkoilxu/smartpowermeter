# Smart power meter usage

## Introducation

智能电表是一个简单的diy项目，它利用功率测量模块获取数据，利用flask搭建html服务器。 通过网页的展示测量到的电压电流功率等数据。

## Parts

### 硬件

- 电量计量模块
- 树莓派

### 软件

- 串口通信
- 数据库读写
- html服务器
- 主页html/css/js

## 原理

1. 电量计量模块可以实时测量电压电流功率数据
2. 树莓派通过串口向电量计量模块发送查询命令，该模块返回相应的数据。
3. 树莓派拿到数据进行解析，然后存储到数据库。
4. 树莓派运行flask，实现一个html服务器。
5. 用户从浏览器访问服务器地址，flask渲染main.html模板并返回给浏览器。
6. 浏览器拿到数据后渲染出网页。
7. 浏览器执行包含在网页中的js，js向服务器请求数据get。
8. 服务器收到请求后，从数据库取出数据，包装然后送回浏览器response。
9. 浏览器拿到这个数据后，解析然后送个四个chart，chart.js负责将数据渲染成图表

## 用法

1. git clone 本项目
2. 安装必要的python库
3. 安装sqlite3
4. 使用python2
5. 运行

  ```
  python runsmartpowermeter.py
  ```

6. 使用浏览器打开localhost网址

# Waterdrop (Data Migrate tool) 
### 本工具主要用途是用smt工具生成建表和flink job的脚本，然后启动对应的同步任务

**[准备工作]**：
1. 安装python3.6+ 
2. 安装virtualenvwrapper
```shell
# 安装package
$ pip3 install virtualenvwrapper

# 设置环境，加入 ~/.bash_profile中
$ source /usr/local/bin/virtualenvwrapper.sh
$ export WORKON_HOME=~/.virtualenvs
$ export VIRTUALENVWRAPPER_PYTHON=/bin/python3

# 环境存放目录
$ mkdir -p $WORKON_HOME

#启动激活环境
$ mkvirtualenv waterdrop

$ workon waterdrop # 第二次启动，激活环境
```
3. 校验flink和mysql
```shell
$ echo $FLINK_HOME
$ flink --version
$ mysql --version
```





**[步骤如下]**：
1. 先从gitlab 或 github中下载代码到本地目录
2. 设置环境变量 
```shell
$ export WATERDROP_HOME = ~/waterdrop/
$ cd $WATERDROP_HOME

#安装package
$ pip3 install -r requirements.txt
```
2. 注册package
```shell
$ pip3 install --editable .

#测试
$ waterdrop --version
```
3. 启动任务
```shell
# 查看帮助
$ waterdrop --help

# 总共分成3步执行
# 1. 根据模板生成配置文件和脚本文件
# 2. 在starrocks中建表
# 3. 启动flink job
```

- Tips:
  1. 清理flink job
  ```shell
  $ flink list|grep 'cdc-task'|awk -F ':' '{print $4}'|xargs -i flink cancel {}
  ```
  2. 查询源数据库中需要同步的表
  ```sql
    SELECT
        concat( '  - ', table_schema, '.', table_name ) 
    FROM
        information_schema.TABLES 
    WHERE
        table_schema = 'mgr' 
        AND table_name LIKE 'sys%'
  ```
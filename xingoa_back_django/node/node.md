
1. 新建项目
2. 修改配置文件：
    * 时区
    * 数据库：sqlite -》 mysql

3. 跨域问题
    pip install django-cors-headers

4. 添加auth模块
    python manage.py 
    安装新的app：在settings.py中

    修改user模型
    模型迁移
    python manage.py makemigrations
    python manage.py migrate

    创建超级管理员
    python manage.py createsuperuser

5. 设计部门表

6. 自定义初始化命令
* 在oaauth应用下创建management包-》commands包
* 在commands文件夹下创建initdepartments.py文件 编写初始化命令代码
* python manage.py initdepartments
* python manage.py inituser

7. 登录： views urls 添加

运行：
python manage.py 

8. 添加中间件
    修改密码

9. 定义考勤模型
    python manage.py startapp absent
    定义模型
    python manage.py makemigrations
    python manage.py migrate


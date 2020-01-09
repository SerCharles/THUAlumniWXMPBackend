---
typora-root-url: ./
---

# 后端文档

软73 沈冠霖 2017013569

**项目整体的github链接：https://github.com/Starrah/THUAlumniWXMP**

**管理员系统的github链接：https://github.com/mayeths/xalumni**

## 1.部署方法

### 1.1 后端部署

先将后端的代码库clone到服务器，在服务器上安装`docker 19.03.5`，进入`backend`文件夹，即`manage.py`所在目录。

之后输入以下命令：

```
docker image build -t backend:1.0.0 .     
docker container run --rm -p 8080:8080 --name backend -d -it backend:1.0.0 
docker attach backend
/bin/bashpython manage.py runserver 0.0.0.0:8080
```

### 1.2 定时更新脚本部署

进入后端backend文件夹，即，即`manage.py`所在目录，然后输入

```
nohup python3 UpdateDatabaseAuto.py
```

### 1.3 管理员系统部署

先将管理员系统的代码库clone到服务器，在服务器上安装`docker 19.03.5`，进入主文件夹，即`Dockerfile`）所在目录。

之后输入以下命令

```
docker image build -t xalumni:1.0.0 .
docker container run --rm -p 8081:8081 --name admin -d -it xalumni:1.0.0 /bin/bash
docker attach admin
npm install
npm run build
npm install -g serve
serve -s build -p 8081
```

## 2.数据库设计

我们使用Mysql类型数据库，具体是django自带的sqlite。

我们数据库设计的UML类图如下：

![Database](/Database.jpeg)

其中，User是用户类，存储用户的session，认证信息，姓名，积分，头像链接等；

Activity是活动类，存储活动的各类时间限制，人数限制，状态，地点，名称，标签，头像，类型等；

JoinInformation是用户加入活动类，存储加入，签到等时间，当前报名状态和权限等，如果用户待审核，还要存储报名原因；

ReportInformation是用户举报活动类，存储举报时间，举报原因等；

Education是教育信息类，存储教育类型，入学年份，院系等；

AdvancedRule是高级报名类，存储入学年份限制，院系限制，教育类型限制等；

Picture是图片类，ActivityType是活动类型类，Department是院系类；EducationType是教育类型类；这些类都相对单一

Admin是管理员类，存储管理员的帐号，密码等；

详情请参考后端的`DataBase/models.py`文件

## 3.系统设计

系统纵向采用分层设计，横向采用模块分块设计，设计图如下：

![Model](/Model.png)

### 3.1 请求层

请求层的模块和后端的每一个功能模块一一对应，请求层每一个函数和后端每一个接口一一对应，其功能如下：

接收前端的请求 -> 进行预处理和合法性判定 -> 进行用户登录，封禁等判断 -> 调用数据库层相应函数得到结果 -> 生成和返回response

### 3.2 数据库层

数据库层的模块和请求层模块基本一一对应，数据库层函数基本和请求层函数一一对应，其功能如下：

将请求的json字典进一步解析成一个一个数据 -> 读取数据库 -> 调用逻辑层相应函数等进行逻辑判断或处理 -> 写入数据库 -> 生成和返回结果给请求层

### 3.3 逻辑层

逻辑层的模块则更加细化，而且其函数也更加丰富多样，其函数的增删也更加频繁。部分函数被请求层直接调用，大多数函数被一个或多个数据库层的模块中的函数调用。

### 3.4 分析

这种设计有以下优点：

首先，这种设计适合频繁变更的需求，数据库设计和接口规则。请求层和数据库层的函数和接口一一对应，而且流程十分明确，在接口和数据库发生变动的时候容易修改。而复杂的逻辑判断都交给逻辑层处理，当功能发生扩展和变动的时候，只需要修改，增加逻辑层的函数即可。

其次，这种设计易于进行测试。在实现和测试一个接口的时候，可以先对其逻辑部分进行单元测试，再对数据库层进行单元测试，再对请求层进行测试。

以及，这种设计让程序高内聚，低耦合---请求层和数据库层横向的模块之间，甚至函数之间很少有耦合。

最终，这种设计也体现了重用原则---逻辑层的函数被底层函数反复调用，让代码更清晰整洁，易于修改。

但是这种设计也遇到了一些问题：

首先，逻辑层函数的变更，拆分较多，容易产生混乱：在接口，数据库需求频繁变更的情况下，很多底层函数原先对逻辑层需求一样，但是在变更后他们对逻辑层的需求会发生变化。在这种情况下，就必须拆分和修改逻辑层函数，这也容易造成混乱。比如，在增加封禁和解封用户需求前，用户查看活动信息和修改活动信息对用户权限的判断一样，而在增加这个需求后，他们对用户权限的判断发生了变化，这就必然导致函数的拆分。

其次，因为数据库层，接口层的流程高度统一，这两层的主要功能重用的不是特别好。比如数据库层有一些比较通用的数据库读，写内容，就没有被很好的重用。

## 4.代码重难点分析

### 4.1 用常量代替数字状态码

我将代码里大量的数字状态码和错误码（比如错误码，活动状态码等）在Constants.py中定义成常量，这样，程序中使用这个状态码和错误码时，引用的是常量名。一方面，这样大大增加了代码的可读性，另一方面，在常量发生变更的时候，只需要修改Constants.py即可。

### 4.2 处理接口的可选参数

很多接口中（尤其是修改活动接口这种）的参数是可能存在可能不存在的，这种情况较难处理。我的处理方法是引入默认参数。比如，对于时间/年份的上界/下界，我引入无穷大/-1；对于修改活动的不存在参数，我读取数据库现有参数作为默认参数；虽然这种做法牺牲了一些效率，但是，在接口频繁变更，逻辑复杂的情况下，这种做法统一了程序流程，大大提高了程序的易修改性，易维护性和可读性。

### 4.3 高级报名

高级报名要解决两个问题:一是判定规则是否自相矛盾（比如2017年入学的软院本科生在一条规则下被接受，另一条被拒绝），二是判定一个学生（可能有多条教育信息，在不同规则下有冲突）是否符合规则。

为此，首先，我们先封装了判定两条单一规则是否冲突的函数，和判定一个人是否符合某规则的函数，利用上述”处理可选参数“的方法进行处理。其次，对于规则冲突，我们将三类规则逐个互相比较，找到冲突就报错。最终，对于学生是否符合规则的判定，我们对规则匹配设置了优先级：待审核>通过>拒绝，然后进行优先匹配。

### 4.4 搜索和推荐

我们的搜索和推荐基于语义分析。为此，我们使用whoosh进行推荐，用jieba进行中文分词，参考了[这个网页](https://www.jianshu.com/p/127c8c0b908a)。

首先，对于每个活动，我们维护了其关键词表---在活动增加，修改，删除时，对活动的名称和标签进行分词，记录在whoosh类的**单体模式对象**中。

其次，对于搜索，我们采用了较为灵活的方法，大大改进了用户体验。因为用户的搜索词可能包括多个维度（比如 火锅聚餐，包括火锅和聚餐两重内容），也可能并不能分词（比如用户只输入单个汉字），因此我们用以下策略进行应对：

我们优先对搜索词进行且关系分词，来处理用户搜索词包含多个维度的情况；如果搜索结果不足，就进行或关系分词；如果分词方法搜索不到任何东西，我们就进行暴力匹配，因为这种情况下，用户的输入通常是单一汉字，因此暴力匹配对效率的影响不大，却能大大改善用户体验。

最终，对于推荐，我们实现了基于活动推荐和基于用户行为推荐两种。我们对推荐结果进行了更为精心的处理，来改进用户体验。一方面，因为用户希望从推荐中得知“自己还能参加哪些活动”，因此，我们在结果中移除了用户已经参加，或者报名必定被拒绝的活动。另一方面，我们的推荐结果有一定随机性，而非确定的。

## 5.测试

### 5.1 测试环境，配置，方法，工具

#### 5.1.1 本地单元测试

使用yapi的手动功能测试和自动化单元测试，安全性，可靠性测试在本地进行，配置如下：

```
ubuntu 16.04
python 3.6.9
django 2.2.4
requests 2.22.0
```

需要先将服务器部署到本地，方法是在manage.py同级目录下输入

```
python manage.py runserver 8082
```

运行自动化单元测试文件需要在同级目录下输入

```
python Unittest.py`
```

#### 5.1.2 服务器功能测试，性能测试

前后端协同的功能测试和性能测试在服务器进行，配置如下：

```
ubuntu 18.04.1
docker 19.03.5
```

性能测试使用`jmeter5.2.1`。

### 5.2 功能测试

#### 5.2.1 测试方法

后端模块和功能众多，不同类型的模块和功能应该采用不同的功能测试方法。

首先，后端的几乎每个接口都有验证格式正确性和用户合法性等公用操作，而且情况并不复杂，因此用yapi手动单元测试即可。

其次，相当多的接口和功能是返回一个/多个活动的信息，这些功能虽然较为复杂，但是手动测试十分容易，因此选用yapi手动单元测试。

再次，许多接口，比如签到等，情形较为单一，而且在前端容易测试，就在yapi手动单元测试之后，借助前端的功能测试进行测试。

最终，一些接口，比如发起，报名，修改活动，条件和情形复杂，接口多变，因此使用自动化单元测试和手动测试结合的方式进行测试。

#### 5.2.2 测试用例

##### 5.2.2.1 用户权限和身份验证

对于用户合法性验证，我们选用三类用户session即可：不存在的session，存在但是被封禁的用户session，正常的用户session进行测试。

还有很多的操作需要验证用户在活动中的权限，我们还对用户权限进行分类：未参加活动的用户，一般用户，活动管理员，活动创建者。

##### 5.2.2.2 分页

对于显示信息类的请求，我们只是专门测试了分页功能

| 起始id限制             | 返回数目限制 | 预期结果                           |
| ---------------------- | ------------ | ---------------------------------- |
| 无                     | 无           | 返回全部合法的                     |
| 有，远大于最大id       | 无           | 返回全部合法的                     |
| 有，最大id+1           | 无           | 返回全部合法的                     |
| 有，最大id             | 无           | 返回除最大id外全部合法的           |
| 有，最小id和最大id之间 | 无           | 返回小于id限制的全部               |
| 有，小于等于最小id     | 无           | 返回空                             |
| 最小id+1               | 无           | 返回最小id的                       |
| 无                     | 远多于总数   | 全部                               |
| 无                     | 总数         | 全部                               |
| 无                     | 小于总数     | 返回id从大至小前k个（k为数目限制） |
| 无                     | 1            | 返回id最大的                       |
| 无                     | 0            | 报错                               |
| 有，最小id和最大id之间 | 大于等于总数 | 返回k个（k为数目限制）             |
| 有，最小id和最大id之间 | 小于总数     | 返回所有能返回的                   |

其余的功能，我们用yapi测试后手动与数据库比对来进行测试。

##### 5.2.2.3 发起活动

对于活动发起，我们进行了手动和自动化测试相结合的单元测试

| 测试的变量                           | 等价类划分                                           | 测试方法         |
| ------------------------------------ | ---------------------------------------------------- | ---------------- |
| 活动开始，结束，报名开始，结束的时间 | 开始时间大于结束时间                                 | 自动化测试       |
|                                      | 报名开始时间大于报名结束时间                         | 自动化测试       |
|                                      | 报名开始时间大于活动开始时间                         | 自动化测试       |
|                                      | 报名结束时间大于活动结束时间                         | 自动化测试       |
|                                      | 当前时间大于结束时间                                 | 自动化测试       |
|                                      | 报名开始时间小于，等于，大于当前时间（测试活动状态） | 手动测试         |
|                                      | 签到开始时间小于，等于，大于当前时间（测试活动状态） | 手动测试         |
| 活动最大，最小人数                   | 活动最大人数小于3                                    | 自动化测试       |
|                                      | 活动最大人数小于最小人数                             | 自动化测试       |
| 活动类型                             | 非法活动类型                                         | 自动化测试       |
|                                      | 个人活动                                             | 自动化测试       |
|                                      | 班级活动                                             | 自动化测试       |
|                                      | 官方活动                                             | 自动化测试       |
| 高级报名                             | 教育类型冲突                                         | 手动和自动化测试 |
|                                      | 时间冲突                                             | 手动和自动化测试 |
|                                      | 院系冲突                                             | 手动和自动化测试 |
|                                      | 正常                                                 | 手动和自动化测试 |

##### 5.2.2.4 报名活动

对于活动报名，我们进行了手动和自动化测试相结合的单元测试

| 测试的变量   | 等价类划分                     | 测试方法   |
| ------------ | ------------------------------ | ---------- |
| 活动报名状态 | 未开始                         | 自动化测试 |
|              | 正在报名                       | 自动化测试 |
|              | 报名暂停或结束                 | 自动化测试 |
| 活动状态     | 活动状态正常                   | 自动化测试 |
|              | 活动待审核                     | 自动化测试 |
|              | 活动状态异常或结束             | 手动测试   |
| 活动最大人数 | 当前人数小于最大人数           | 自动化测试 |
|              | 当前人数=最大人数-1            | 自动化测试 |
|              | 当前人数大于等于最大人数       | 自动化测试 |
| 高级报名     | 直接报名成功                   | 自动化测试 |
|              | 待审核                         | 自动化测试 |
|              | 直接拒绝                       | 自动化测试 |
|              | 未被匹配，状态变为活动默认状态 | 自动化测试 |

##### 5.2.2.5 修改活动

对于活动修改，我们进行了手动和自动化测试相结合的单元测试

| 测试的变量                           | 等价类划分                              | 测试方法         |
| ------------------------------------ | --------------------------------------- | ---------------- |
| 活动开始，结束，报名开始，结束的时间 | 开始时间大于结束时间                    | 自动化测试       |
|                                      | 报名开始时间大于报名结束时间            | 自动化测试       |
|                                      | 报名开始时间大于活动开始时间            | 自动化测试       |
|                                      | 报名结束时间大于活动结束时间            | 自动化测试       |
|                                      | 当前时间大于结束时间                    | 自动化测试       |
| 活动最大，最小人数                   | 活动最大人数小于3                       | 自动化测试       |
|                                      | 活动最大人数小于最小人数                | 自动化测试       |
| 活动类型                             | 非法活动类型                            | 自动化测试       |
|                                      | 个人活动，班级活动相互修改              | 自动化测试       |
|                                      | 个人/班级活动修改成官方活动             | 自动化测试       |
|                                      | 官方活动相互修改                        | 自动化测试       |
|                                      | 官方活动修改成个人/班级活动（待审核）   | 自动化测试       |
|                                      | 官方活动修改成个人/班级活动（正常状态） | 自动化测试       |
| 高级报名                             | 教育类型冲突                            | 手动和自动化测试 |
|                                      | 时间冲突                                | 手动和自动化测试 |
|                                      | 院系冲突                                | 手动和自动化测试 |
|                                      | 正常                                    | 手动和自动化测试 |

##### 5.2.2.6 活动签到

活动签到方面，我们根据状态类型和签到类型进行手动单元测试

| 测试的变量 | 等价类划分               | 预期结果 |
| ---------- | ------------------------ | -------- |
| 签到状态   | 未开始                   | 失败     |
|            | 正在签到                 | 成功     |
|            | 签到暂停或者结束         | 失败     |
| 二维码签到 | 匹配                     | 成功     |
|            | 不匹配                   | 失败     |
| 距离签到   | 小于阈值                 | 成功     |
|            | 阈值-1                   | 成功     |
|            | 阈值                     | 成功     |
|            | 阈值+1                   | 失败     |
|            | 大于阈值                 | 失败     |
| 用户状态   | 用户已经加入活动，未签到 | 成功     |
|            | 用户已经签到             | 失败     |
|            | 用户未加入活动           | 失败     |
|            | 用户被封禁               | 失败     |

##### 5.2.2.7 其余接口

对于二维码，头像的上传，返回，我们使用postman进行测试。

对于管理员系统的登录，注销，修改用户，活动状态，举报活动等，情况单一，用yapi进行手动测试。

对于登录和用户认证，因为前后端高度耦合，我们在用yapi进行简单的单元测试之后，通过前后端集合的功能测试完成了测试。

对于搜索和推荐，因为这些是利用外部库实现的，还有随机性，因此我们使用yapi进行手动功能测试。

##### 5.2.2.8 可靠性测试

在实际情况中，可能会有许多非法的请求访问我的服务器，为了防止这种请求让服务器崩溃，我们必须要测试非法输入的影响。我的方法是对每个接口用yapi手动发送格式不正确的乱码，看程序是否还能正常运行。对于所有的接口，发送乱码程序都不会崩溃，都会返回错误信息。

#### 5.2.3 测试结果

我们通过了上面全部的单元测试。在开发的中后期，我们利用这种测试驱动开发的思想发现并修改了不少bug，提高了开发效率。同时，我们在开发的后期，利用单元测试，将活动添加，报名，修改这三个功能复杂，需求频繁修改的接口的bug全部修复。

### 5.3 安全性

安全性主要的威胁是sql注入，我的方法是使用自动化的方法模拟sql注入攻击，再查看数据库看看是否有问题。

我们参考了[这个网页](https://blog.csdn.net/yyyyycici/article/details/90318050)设计了几组攻击，然后发现全部能返回错误信息，而且查看数据库，发现没有被修改，这可以说明程序没有sql注入风险。

注：以下每组攻击都是正常请求+非正常攻击性sql语句

正常请求是http://127.0.0.1:8082/userData?session=bbb

| 组号 | 后缀                                                         |
| ---- | ------------------------------------------------------------ |
| 1    | -0\|                                                         |
| 2    | and 1=3                                                      |
| 3    | order by 4                                                   |
| 4    | order by 5                                                   |
| 5    | and 1=2 union select 1,2,3,4                                 |
| 6    | and 1=2 union select 1,database(),3,4                        |
| 7    | and 1=2 union select 1,table_name,3,4 from information_schema.tables where table_schema='DataBase_user' |
| 8    | and 1=2 union select 1,table_name,3,4 from information_schema.tables where table_schema='models' |

### 5.4 性能测试

#### 5.4.1 测试设计

首先，测试接口我们选择获取全部活动接口和搜索接口，因为这两个接口是用户一进入小程序就会调用的，也是最频繁访问的，因此这两个接口容易达到高并发。而其他的操作，比如发起，参与，签到活动等，因为实际用户不是很多，难以达到高并发。因此，我们测试获取全部活动接口和搜索接口。

其次，我们使用jmeter进行负载和压力测试，并发量选用200,500,800,1000,达到最大并发时间是10s。

#### 5.4.2 测试结果和分析

首先，我们测试了获取全部活动接口，最大获取活动数目是15，结果如下：

| 并发量 | 平均返回时间 | 50%返回时间 | 90%返回时间 | 错误率 |
| ------ | ------------ | ----------- | ----------- | ------ |
| 200    | 5.78s        | 4.43s       | 9.86s       | 0.19%  |
| 500    | 17.22s       | 8.62s       | 48.78s      | 9.75%  |
| 800    | 27.40s       | 17.06s      | 60.12s      | 31.02% |
| 1000   | 30.32s       | 22.12s      | 60.12s      | 30.38% |

可以看出，在并发量200的时候，平均和中位数返回时间不到6s，90%返回时间不到10s，错误率接近0,程序运行良好；

**在并发量500的时候，程序接近其极限了**，错误率接近10%，只有估计三分之二的请求能在10秒内返回；

**在并发量800和1000的时候，程序超过极限**，错误率高达30%，大多数请求都不能在10s内返回，程序无法使用。

之后，我们猜测原因可能是两方面的：程序效率低下，运算占了大头；服务器性能差，带宽不足。因此，我们测试了最大获取活动数目为1的情况：在上一个测试（最大获取活动数目15）时，一个response包有6kb左右，而这次测试一个包不到500bytes。结果如下：

| 并发量 | 平均返回时间 | 50%返回时间 | 90%返回时间 | 错误率 |
| ------ | ------------ | ----------- | ----------- | ------ |
| 200    | 2.27s        | 1.50s       | 4.47s       | 0.00%  |
| 500    | 5.85s        | 2.03s       | 11.41s      | 2.97%  |
| 800    | 8.35s        | 4.16s       | 19.37s      | 4.52%  |
| 1000   | 10.42s       | 1.57s       | 60.01s      | 12.51% |

返回15个活动和返回1个活动的计算用时几乎一致，而response包大小差距巨大。而返回一个活动的平均，中位数返回时间，错误率只有返回15个活动的三分之一，在并发量500,800的时候运行良好，到了并发量1000才达到极限。因此可以初步说明，**限制这个接口效率的主要是服务器带宽**。

最终，我们测试了搜索活动接口，最多返回15个活动，结果如下：

| 并发量 | 平均返回时间 | 50%返回时间 | 90%返回时间 | 错误率 |
| ------ | ------------ | ----------- | ----------- | ------ |
| 200    | 7.20s        | 4.72s       | 14.06s      | 0.92%  |
| 500    | 17.24s       | 4.93s       | 60.12s      | 19.27% |
| 800    | 27.40s       | 17.06s      | 60.12s      | 31.02% |
| 1000   | 32.50s       | 26.49s      | 60.12s      | 35.75% |

搜索活动接口的情况和返回15个的返回全部活动接口类似，都是在并发200时运行良好，并发500时接近极限，大于500时程序几乎无法使用。

综上所述，这个程序在200及以下并发能够良好运行，在500并发左右达到极限。
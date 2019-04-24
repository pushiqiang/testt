# Cassandra
## 分布式系统的CAP 定理

CAP 定理:“一致性、可用性和分区容错性”

分布式系统的三个指标：

* Consistency

* Availability

* Partition tolerance

#### Consistency（一致性）
分布式系统，写操作之后的读操作，必须返回该值

#### Availability（可用性）
Availability 中文叫做"可用性"，意思是只要收到用户的请求，服务器就必须给出回应。

#### Partition tolerance（分区容错性）
大多数分布式系统都分布在多个子网络。每个子网络就叫做一个区（partition）。分区容错的意思是，区间通信可能失败。

依据 CAP 定理，对于任何分布式系统，都必须为它选择两种最重要的保证

Cassandra 是专注于可用性和分区容错性的解决方案的最佳选择。
CAP与传统关系数据库管理系统的 ACID（原子性、一致性、隔离性、持久性）属性相反

## 环境

建议机器上至少拥有 4 GB RAM，其中至少 2 GB 可用于该 Cassandra 实例。8GB RAM 机器更好。
如果决定在 Docker 上运行 Cassandra 实例，每个容器至少必须有 1 GB RAM 可用来运行每个 Cassandra 节点。

## Cassandra

Cassandra是一个Java实现的分布式非关系型数据库。

#### 分布式

典型的 Cassandra 网络拓扑结构包含一个节点集群（也称为 Cassandra 环），每个节点在不同物理服务器上的不同网络地址中运行。
每个节点都可以协调客户端的请求，而不需要主节点，因此没有单点故障（在python连接客户端配置连接可以指定多个节点配置）

#### 非关系型
CQL: Cassandra查询语言
结构动态扩展，非格式化数据

#### 基本架构
节点的每个写入活动都由写入节点的提交日志捕获(Commit log， 永久存在),之后，数据将被捕获并存储在内存表(Mem-table)中。 
每当内存表已满时，数据将被写入SStable数据文件。 
所有写入在整个集群中自动分区和复制。 Cassandra定期整合SSTables，丢弃不必要的数据。

Cassandra提供了数据可以自动过期（ttl）的功能。

### 基本数据结构和建模

#### 基本概念

Cluster：Cassandra 的节点实例，它可以包含多个Keyspace。
Keyspace:：用于存放 ColumnFamily 的容器，相当于关系数据库中的 Schema 或 database。

ColumnFamily:：用于存放 Column 的容器，类似关系数据库中的 table 的概念 。

SuperColumn:：它是一个特列殊的 Column, 它的 Value 值可以包函多个Column。

Column:：Cassandra 的最基本单位。由name , value , timestamp组成。

![enter image description here](https://images2015.cnblogs.com/blog/812359/201511/812359-20151119221242546-1765431174.png)

#### 主键
在 Cassandra 中，所有数据都通过一个主键（或行键）按分区进行组织

Cassandra 中的主键可以包含两种特殊键：分区键和（可选的）集群键。
分区键的用途是将数据均匀分布在集群中
集群键（也称为“集群列”）的职责是集群化某个分区的数据并组织它们

当您在 Cassandra 中创建一个表时，您使用了一条与以下命令类似的 CQL 命令：

```
CREATE TABLE movie_catalog (category text, year int, title text, 
PRIMARY KEY (category));
```

第一列被隐式地视为 movie_catalog 表的分区键。没有集群键。但是，假设您在主键中添加了 year 列，如下所示：

```
CREATE TABLE movie_catalog (category text, year int, title text, 
PRIMARY KEY (category,year));
```

现在，category 继续作为分区键，而 year 列是集群键。两列都是主键的一部分。

所有 Cassandra 表都必须有一个主键来确定数据位于集群中的哪个节点。该键至少要包含一个分区键(用于定位节点)


### Cassandra写数据

数据要写到 Cassandra 中有两个步骤：

* 找到应该保存这个数据的节点
* 往这个节点写数据。

客户端写一条数据必须指定 Keyspace、ColumnFamily、Key、Column Name 和 Value，还可以指定 Timestamp，以及数据的安全等级。

更新操作也是写入操作，所有写入数据都会保存（历史数据可查）

### Cassandra读数据

Cassandra 的写的性能要好于读的性能，Cassandra 的设计原则就是充分让写的速度更快、更方便而牺牲了读的性能。

使用Cassandra的时候，数据在写入的时候就已经排好顺序了。在某一个Key内的所有Column都是按照它的Name来排序的

索引、排序和分页；处于性能的考虑，cassandra对这些支持都比较简单

###### Allow Filtering

cassandra的数据结构类似python字典对象，查询需要通过键一级一级深入
但是也可以使用Allow Filtering参数，放开限制，但是有性能损失

Cassandra建模面向读效率建模

### Example
python客户端
```
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.cqlengine import columns, usertype, connection
from cassandra.cqlengine.models import Model

CASSANDRA_USER = 'cassandra'
CASSANDRA_PASSWORD = 'cassandra'
CASSANDRA_NODES = ['cassandra']

auth = PlainTextAuthProvider(username=CASSANDRA_USER,
                             password=CASSANDRA_PASSWORD)
cluster = Cluster(CASSANDRA_NODES, auth_provider=auth)
db_session = cluster.connect()
connection.set_session(db_session)


class TestModel(Model):
    room_id = columns.UUID(partition_key=True)
    game_id = columns.UUID(primary_key=True)

    users = columns.Map(key_type=columns.UUID,
                        value_type=UserDefinedType(UserInfo))
    records = columns.List(value_type=UserDefinedType(BuyInRecord))

    created_at = columns.DateTime(default=datetime.utcnow)
 
TestModel.create(room_id='xxxx', game_id='xxxx')
TestModel.get(room_id='xxxx', game_id='xxxx')
```

### Cassandra应用场景

快速增长的数据业务

### 总结
查询问题

写入失败问题

分页问题

作为缓存系统使用

不需要象数据库一样预先设计schema，增加或者删除字段非常方便



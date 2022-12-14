===============
学习 Linux
===============

++++++++++++
POSIX APIs
++++++++++++

-----------
fork
-----------

创建一个新的进程，调用者称为父进程，新创建的进程称为子进程。两个进程运行在不同的地址空间，内存读写、文件映射等操作不会互相干扰。除了以下几点外，子进程会在创建时复制父进程的状态：

- 分配新的 PID，不会于现有的 PGID 冲突
- 父进程 PID 与调用者的 PID 一致
- 不会继承父进程的内存锁（mlock）
- 进程资源占用情况（getrusage），CPU 时间会清零（times）
- 等待处理的信号集合会清空 （sigpending）
- 不会继承 semaphore adjustments （不太理解）
- 不会继承 process-assosiated record locks
- 不会继承计时器（setitimer、alarm、timer_create）
- 不会继承异步 IO 的上下文和未完成的请求

一些其他需要注意的点：

- 子进程会复制整个地址空间，父进程内锁的状态等信息也会被复制
- 

------------
fcntl
------------

`这篇博客 <https://saltigavv.net/articles/file-locks/>`_ 详细地介绍了 Linux 中的文件锁。

- BSD locks：
    - 通过 ``flock`` 创建文件锁
    - 整个文件上锁
    - 和 ``File`` 对象关联
    - 不支持原子的读写锁类型转换
    - 复制的文件描述符（指向同一个 ``File`` ）不提供同步机制
- POSIX record locks:
    - 通过 ``fcntl`` 创建文件锁
    - 上锁范围精确到字节
    - 和 ``[inode, pid]`` 对关联
    - 支持原子的读写锁类型转换

------------
execve
------------


------------
getrusage
------------

获取当前进程、当前进程的全部子进程或当前线程的资源占用情况。具体信息直接参考 ``usage`` 结构体。

---------------
mlock 系列
---------------

对某个范围内连续的页进行上锁，确保该页不会被系统换出。主要应用场景为实时算法和高安全性数据处理。

实时算法需要统计任务调度等性能瓶颈带来的开销，而换页则是具有很高不确定性的机制。
实时算法测试可以将全部页面算法，同时使用一些 dummy 写操作来避免页的强制缺失。注意 fork 调用会准备 COW 机制，也就是说这之后的写操作会触发缺页异常，因此应该在对时间精度要求较高的场景下避免使用 fork。

安全性需求则是防止用户的隐私信息在处理过程中被换入外存，从而增大泄漏的风险。但是一些电脑会在挂起时将内存拷贝到外存，这一机制无法通过 mlock 来避免。

++++++++++++
io_uring
++++++++++++
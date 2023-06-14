# 阅读笔记

## IPC

### Understanding the Overheads of Hardware and Language-Based IPC Mechanisms

这篇文章侧重于性能分析，关于 Rust 的探讨基于 RedLeaf，从参考文献中可以了解相关论文。

硬件隔离机制：VMFUNC、MPK（x86）、MTE（arm）

硬件隔离机制的性能仍受到保存和恢复寄存器、换栈等影响，应用 Rust 隔离可以减少这些开销。

Rust 比 C++ 慢（4-8%），Rust 需要更多运行时检查（更多的分支预测失败），高度抽象和结构体封装（可能）对 Cache 不友好。

### Android Binder

Android Binder 是 Android 中实现的（Client-Server） IPC 方式，软件层面减少进程间跨地址空间通信的拷贝次数。主要组成部分：

- Client 进程
- Server 进程
- Binder 驱动：mmap 向 Server 进程共享数据；线程池线程管理
- ServiceManager：管理 Service 注册与查询

1. 注册服务：Server 进程向 Binder 驱动发起 Service 注册请求；Binder 驱动将注册请求转发给 ServiceManager 进程；ServicManager 进程添加 Server 进程信息。
2. 获取服务：Client 进程向 Binder 驱动发起获取服务的请求（服务名称）；Binder 驱动将获取请求转发给 ServiceManager 进程；ServiceManager 查找到 Server 进程信息；通过 Binder 驱动将信息返回给 Client 进程。
3. 使用服务：Binder 驱动先创建一块内核缓冲区，并将 Server 进程的用户地址映射到该区域，避免 `copy_to_user()` ，Client 进程通过系统调用 `copy_from_user()` 将数据拷贝到内核缓冲区（当前线程被挂起）；Server 进程收到 Binder 通知后，从线程池中取出对应线程对数据进行处理并将执行结果写入共享内存（相当于写入内核缓冲区）中；Binder 驱动通知内核唤醒 Client 进程，Client 进程通过 `copy_to_user()` 从内核缓冲区接收 Server 进程返回对数据。

Binder 驱动位于内核空间，ServiceManager 是用户空间的进程，二者均为 Android 基础架构。

可以将通信过程视为一次跨域调用，Client 向缓冲区传入参数，Server 向缓冲区传入返回值。

一些问题：

1. ServiceManger 相当于路由，为什么不采用 Client 到 Server 直接的共享内存？Client 数量大时可能会占用 Server 很多地址，Binder 相比于共享内存就是更易于使用开发，抽象得好管理起来比较方便。
2. 多个 Client 同时向同一个 Service 发起请求怎么处理？应该有缓冲队列或者线程调度上的处理，反正 Client 发送请求后会挂起。
3. 通信流程涉及到多少次**通知**？Binder 通知 Server 处理传入数据、Binder 通知 Client 处理返回数据。
4. Binder 还是涉及到了一次拷贝的开销，且 Client 地位比较被动，使用服务要被挂起。

### seL4 Notification
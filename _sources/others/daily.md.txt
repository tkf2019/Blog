# 阅读笔记

## XPC

- 硬件层面优化IPC性能的实现，我理解为新的进程管理方法，通过引入更复杂的硬件设计来适应microkernel对IPC的高度依赖，有硬件操作系统的趋势？
- 存在的问题：
  - 解决不了多核跨进程通信问题
  - 设计较为复杂，但安全方面可能比较薄弱，论文中只采用了控制位和预设的物理空间来进行安全检查（可能通过硬件漏洞直接窃听内存中的通信数据
- 实现高性能IPC的两个重要层面：
  - 如何摆脱kernel带来的开销：
    - 陷入和恢复
    - IPC 相关执行逻辑
    - 进程上下文切换
  - 如何实现无拷贝通信
- 设计目标：
  - 无陷入进程切换
  - 无拷贝进程通信
  - 适应现有内核
  - 尽可能简化硬件设计
- 基本组成：
  - x-entry:区分ID，访问权限控制xcall-cap
  - xcall和xret指令：快速的进程切换
  - 地址映射策略relay-seg：使用寄存器保存message在内存中的基址和范围；进程间原子性拥有message控制权，避免TOCTOU攻击
  - migrating thread model: ？
- Zircon通过异步IPC模拟文件系统接口的同步语义带来了高昂的开销
- seL4的IPC处理机制，检查以下条件来判断是否采用slowpath还是fastpath：
  - 通信双方有不同的特权级别
  - 通信双方位于不同的核上
  - message大小是否超出寄存器大小但未超过buffer大小
  - 这些机制可以通过硬件并行化来降低延迟
- seL4的IPC通信机制，根据消息长度采用三种策略：寄存器、IPC buffer、shared memory；并不安全，多线程可以篡改数据？
- XPC engine：

![xpc.png](../_static//xpc.png)

- xcall #reg:
  - 访问bitmap检查xcall-cap
  - 访问x-entry-table并检查valid标志位
  - 将恢复需要的信息推入link stack中
  - 指向callee页表，pc跳转到目标进程entry point，保存caller的信息
- xret：
  - 将link stack的栈顶弹出，检查valid标志位，并根据信息返回caller进程（嵌套？）
- xcall-cap：xcall-cap-reg保存bitmap在内存中的基址
- link stack：可以非阻塞方式写stack
- cached x-entries：利用prefetch，进程可提前将x-entry加载到cache
- swapseg #reg: reg-seg和seg-list中的一项交换内容


![relay-seg-chain.png](../_static/relay-seg-chain.png)


## SkyBridge

- 论文多次提到熔断漏洞，近几年受到广泛关注和研究的安全性问题；
- 微内核最关键的机制是核间通信，在用户层实现很多系统级应用，内核只保留最基本的功能；传统的进程通信依赖于内核进程切换，带来了巨大的开销
- seL4的fastpath IPC
- SkyBridge 提出了一些应用 VMFUNC 的方法：
  - 位于microkernel下方的Rootkernel，使用巨页避免microkernel频繁触发缺页中断；采用Subkernel和Rootkernel两级分管
  - SkyBridge巧妙地将Client的CR3映射为对应Server的CR3，Client通过EPTP list来指向不同Server的EPT
  - 安全机制在kernel处理IPC，SkyBridge检查process的二进制文件避免非法VMFUNC，通过查表来验证IPC请求
- Rootkernel:
  - 从Subkernel启动，通过VMCALL与Subkernel通信
  - 确保大多数VM行为不触发VM exit，VM exits包含三类：
    - 特权指令：不触发VM exits
    - 硬件中断：直接将中断交给microkernel处理
    - EPT异常（miss，invalid）：Subkernel到Rootkernel采用1GB的页，SkyBridge仅为Rootkernel保留100MB的物理空间，减少TLB miss等问题出现的次数和开销
- Subkernel：
  - server注册：将trampoline code page和stack pages映射到server的虚拟地址空间，为server分配ID
  - client注册：绑定到指定ID的server，同样进行映射；EPT处理，将client的CR3映射到server的CR3；将所有和server有关的EPTP添加到client的EPTP list
  - 跨虚拟地址空间执行时陷入内核的问题：Subkernel可以记录进程的信息来判断
- Rewriting Illegal VMFUNC:
  - 替换VMFUNC指令，若只有一条指令，则直接替换，若需要执行多条指令，则替换为跳转指令，跳转到待执行代码再返回
  - （具体策略和x86的指令编码有关，暂时还没有深入学习x86体系结构）

## [CHERI: A Hybrid Capability-System Architecture for Scalable Software Compartmentalization](https://ieeexplore.ieee.org/document/7163016)

- Slides: [CHERI](https://www.cl.cam.ac.uk/research/security/ctsrd/pdfs/20171109-mit-cheri-web.pdf)
- 其他：[UCB PLAS06](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjlwPXovMT7AhWltFYBHfeeBAkQFnoECA0QAQ&url=https%3A%2F%2Fpeople.eecs.berkeley.edu%2F~daw%2Ftalks%2FPLAS06.ps&usg=AOvVaw04t4KMID2-GG-_ALG3vT9C&cshid=1669212494087131)

### 简介

- 目标：通过软硬件协同的方法，解决有关 TCB 安全问题
- 将传统方法分为两类： `exploit mitigation` 和 `software compartmentalization`
  - 前者局限于攻击方式
  - 后者引入性能问题和扩展性问题
  - CPU 未提供细粒度的内存保护
- 完成的工作：
  - 提出一种新的软硬件架构支持细粒度的隔离机制
  - 在 FPGA、FreeBSD、LLVM 中对架构进行验证
  - 提出一种高效的、可扩展的 MMU 模型
  - 对安全性、性能、特别是兼容性进行分析和验证

### 方法

- `Ambient Authority`: 系统访问控制，主体指明对某一客体执行的动作并完成，称该主体使用了**环境权限**。请求是否授予或拒绝权限取决于动作的属性，比如动作的身份或角色。
- `Confused Deputy Problem`: 一个程序通过向另一个程序发起请求，来获取另一个程序的系统权限。（代理混淆问题）例如传统的文件名并不能携带发起请求的程序对这个文件的访问权限，通过代理后，系统并不会处理该程序到文件的权限。
- `Capability-based software compartmentalization`: 
  - `OS-based`: HYDRA、EROS、SeL4、Capsicum
  - `language-based`: E、Joe—E、Caja
- 局限性：
  - 过于依赖硬件提供的机制，侧信道攻击
  - TCB 问题需要考虑很多因素比如编译错误，内存分配，文件描述，垃圾回收等，如何最小化 TCB


## Understanding the Overheads of Hardware and Language-Based IPC Mechanisms

这篇文章侧重于性能分析，关于 Rust 的探讨基于 RedLeaf，从参考文献中可以了解相关论文。

硬件隔离机制：VMFUNC、MPK（x86）、MTE（arm）

硬件隔离机制的性能仍受到保存和恢复寄存器、换栈等影响，应用 Rust 隔离可以减少这些开销。

Rust 比 C++ 慢（4-8%），Rust 需要更多运行时检查（更多的分支预测失败），高度抽象和结构体封装（可能）对 Cache 不友好。

## Android Binder

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

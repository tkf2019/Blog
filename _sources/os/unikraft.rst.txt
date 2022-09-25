-------------
Unikraft
-------------

.. admonition:: What is Unikernel ?

    - fast instantiation (实例化) times (tens of milliseconds or less)
    - tiny memory footprints (内存占用) (a few MBs or even KBs)
    - high network throughput (10-40GB/s)
    - high consolidation (整合性) (being able to run thousands of instances on a single commodity server)
    - a reduced attack surface and the potential for easier (如何体现安全性？)

**Unikraft** 设计思想：保留 **Unikernel** 的特性，解决应用的移植开销问题，在性能和移植性上作出权衡，可以进行灵活的配置。

.. admonition:: What is `Unikraft <https://arxiv.org/abs/2104.12721>`_ ?

    - Standard image with lots of unnecessary code; specialized image needs lots of development efforts.
    - Unikraft: a system that automatically builds a lean, high performance image for the application and the platforms.

**Unikraft** 构建镜像流程：

- Select application
- Select configured libs (main lib, platform lib, arch lib)
- Build
- Run with Unikernel binaries

.. admonition:: Library pools

    1. the architecture library tool, containing libraries specific to a computer architectur.
    2. the platform tool, where target platforms can be Xen, KVM, bare metal and user-space Linux.
    3. the main library pool, containing a rich set of functionality to build the unikernel form.

    Main library: 

    1. Drivers (both virtual such as netback/netfront) and physical such as ixgbe
    2. Filesystems
    3. Memory allocators
    4. Schedulers
    5. Network stacks
    6. Standard libs (libc, openssl)
    7. Runtimes (Python interpreter, debugging and profiling tools)



====================
关于模块化的一些思考
====================

模块化工程应满足 **高内聚低耦合** 原则，低耦合模块不应该了解其他模块的内部工作原理，高内聚意味着模块应该仅包含相关性的代码。

模块间的通信不可避免，通信的方法一般是实现中间层，例如 ``Redleaf`` 中的 ``Shared Heap`` 。

模块间通信可以划分为两种形式，一种是 **数据交互**，另一种是 **模块切换**，类似于 ``Theseus`` 中的 ``Swap Cell``。

模块的接口应该保证是最小的，不应该对外暴露内部实现细节，尽可能地减少外部调用者对于接口的访问范围。


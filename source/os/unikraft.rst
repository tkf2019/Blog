-------------
Unikraft
-------------

    https://unikraft.org/docs/getting-started/

    https://asplos22.unikraft.org/

    https://github.com/unikraft/unikraft

======
概述
======

.. admonition:: What is Unikernel ?

    - fast instantiation (实例化) times (tens of milliseconds or less)
    - tiny memory footprints (内存占用) (a few MBs or even KBs)
    - high network throughput (10-40GB/s)
    - high consolidation (整合性) (being able to run thousands of instances on a single commodity server)
    - a reduced attack surface and the potential for easier (如何体现安全性？)

..

    Defining a small set of APIs for core OS components that makes it easy to replace-out a component when it is not needed, and to pick-and-choose from multiple implementations of the same component when performance dictates.

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

..

   - Perf: 1.7x-2.7x performance improvement compared to Linux guests
   - Image size: images for these apps are around 1MB
   - Memory footprint: require less than 10MB of RAM to run
   - Boot: boot in around 1ms on top of the VMM time 

关于性能测试， **Unikraft** 声称在镜像大小、引导时间、运行性能上都取得了非常好的效果。

=========
源码分析
=========

.. image:: ../_static/unikraft.png
    :align: center
    :scale: 75%

论文中的这张图非常清晰地给出了 **Unikraft** 的设计架构，从设计架构出发，可以对 `源码 <https://github.com/unikraft/unikraft>`_ 进行简要的分析。
（ lib 文件夹把所有的模块都平铺在一块，这也是之后在设计 OS 时需要注意的问题，没有这张图就很难找到头绪）

+++++++++
ukalloc
+++++++++

- a POSIX compliant external API
- an internal allocation API called ukalloc
- one or more backend allocator implementations

.. code-block:: c
    :linenos:

    struct uk_alloc;
    typedef void* (*uk_alloc_malloc_func_t)
		(struct uk_alloc *a, __sz size);
    struct uk_alloc {
        /* memory allocation */
        uk_alloc_malloc_func_t malloc;
        // ...

        /* internal */
        struct uk_alloc *next;
        __u8 priv[];
    };
    /* wrapper functions */
    static inline void *uk_do_malloc(struct uk_alloc *a, __sz size) {
        UK_ASSERT(a);
        return a->malloc(a, size);
    }
    static inline void *uk_malloc(struct uk_alloc *a, __sz size) {
        if (unlikely(!a)) {
            errno = ENOMEM;
            return __NULL;
        }
        return uk_do_malloc(a, size);
    }
    /* Platform common functions */
    static struct uk_alloc *plat_allocator;
    int ukplat_memallocator_set(struct uk_alloc *a) {
        UK_ASSERT(a != NULL);

        if (plat_allocator != NULL)
            return -1;

        plat_allocator = a;

        _ukplat_mem_mappings_init();

        return 0;
    }
    struct uk_alloc *ukplat_memallocator_get(void) {
        return plat_allocator;
    }


    /* Descriptor of a memory region */
    struct ukplat_memregion_desc {
        void *base;
        __sz len;
        int flags;
    #if CONFIG_UKPLAT_MEMRNAME
        const char *name;
    #endif
    };




+++++++++
uksched
+++++++++

.. code-block:: c
    :linenos:


++++++++
ukboot
++++++++
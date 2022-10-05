----------
Redleaf
----------

===============
Communication
===============

核心类型 ``RRef<T>`` (Remote reference)

.. code-block:: rust

    pub struct RRef<T> where T: 'static + RRefable {
        // 仅在 mutable borrow 时变更所有者
        domain_id_pointer: *mut u64,
        // 记录 immutable borrow 的数量
        pub(crate) borrow_count_pointer: *mut u64,
        pub(crate) value_pointer: *mut T
    }

利用 Rust 所有权机制，通过 shared heap 传递数据。在确保隔离的条件下，不引入拷贝带来的开销。Domains 之间通过 ``RRef<T>`` 类型获得数据的所有权（Redleaf 是单一地址空间的）。

shared heap 上分配的 object 只能通过 ``RRef<T>`` 访问 shared heap 上的其他 object，这个规则通过 IDL Compiler 的类型检查来确保（称之为 Exchangable Types）。


 
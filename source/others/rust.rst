------------
学习 Rust
------------

``static``

- 全局变量不会被内联，整个程序中，全局变量只有一个实例，所有的引用会指向相同的地址
- 可变全局变量可能出现多个线程同时访问的情况，因而引发内存不安全的问题，所以对于可变全局变量的访问和修改代码必须在 ``unsafe`` 块中定义
- 存储在全局变量中的值必须实现 ``trait Sync``
- 全局变量需要在编译期确定好内存布局
- 如何定义 ``static`` 变量，用于全局访问，且运行时才对这一变量进行初始化？最直观的做法是使用 ``lazy_static``，查看 ``lazy_static`` 内部源码发现，可以使用 ``spin::Once`` 结构对变量进行封装，在运行时调用 ``call_once`` 函数进行初始化。传入参数需要返回初始化后的结果。

.. code-block:: rust
  :linenos:

    fn call_once<'a, F>(&'a self, builder: F) -> &'a T 
    where
        F: FnOnce() -> T,

--------------

``PathBuf``

- 用来方便地进行系统路径的操作（在 Windows 和 Unix 中表现不同）
- 调用 ``into_os_string().into_string().unwrap().to_str()`` 方法转化为 ``&str``
- 可将根目录视为栈底，支持 ``push`` 和 ``pop`` 操作动态添加路径中的目录
- ``set_file_name``：替换栈顶元素
- ``set_extension``：为栈顶元素增加文件类型

---------------

``Generics``

- ``where`` 更清晰地指定泛型约束，且支持间接指定类型
- ``associated types`` 将类型放入 ``trait`` 内部作为输出类型，增强了代码可读性

---------------

``Closure``

- ``FnOnce`` 闭包只能运行一次，通过 ``self`` 参数获取对象的所有权，调用后即释放
- ``FnMut`` 闭包可运行多次，且可以修改捕获变量的值
- ``Fn`` 闭包可运行多次，不可以修改捕获变量的值
- ``move`` 强制将要捕获的变量的所有权转移到闭包内部的存储区域

---------------

``Module test``

- 在对 ``lib`` 或 ``bin`` 进行测试时，如果外部实现为 ``#![no_std]``，那么可以在单独定义的 ``mod test`` 中通过 ``extern crate std`` 导入 std 库
- ``cargo test`` 通过是默认不打印输出的，如果想看到一些输出结果，可以使用命令``cargo test --package <your package> -- --nocapture``

---------------

``paste``

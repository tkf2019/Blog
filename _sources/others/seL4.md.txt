# seL4

## Tutorial

seL4 构建基于多种工具，包括 repo、ninja 等。Tutorial 测例默认在 x86 架构的 QEMU 上运行。

运行 hello-world 退出后报错 `Caught cap fault`，将 return 0 改为执行 exit 后不再出现报错。

ninja 构建 hello-camkes-0 报错 `make: stack: No such file or directory`，一个解决办法是执行 `curl -sSL https://get.haskellstack.org/ | sh` 安装 haskell-stack，然后报错 Timeout，解决网络问题后可以正常运行。

## Hardware

支持 [Rocket](https://docs.sel4.systems/Hardware/rocketchip.html) 硬件平台。

hardware.yml 给出的硬件描述，以 uintc 为例：

```yml
- compatible:
    - riscv,uintc0
  regions:
    - index: 0
      kernel: UINTC_PPTR
      kernel_size: 0x4000
      user: true
```

其中 kernel 字段表示内核映射后的 device 起始地址。

## Capability and Kernel Object

    A capability is a unique, unforgeable token that gives the possessor permission to access an entity or object in system. 

**Capability (cap)** 是 seL4 的核心机制，通过唯一且不可伪造的 token 来获取对象的访问权限，可以将 cap 视为带有访问控制的指针。

**root task** 在初始化时会获取所有资源的 cap ，例如 `seL4_CapInitThreadTCB`，可以通过 API 读取或修改 TCB 的内容。

**CSpace** 表示一个 thread 持有的全部 cap 。

seL4 提供了七个内核对象，它们一起构成了进程的基本运行环境。

- **CNodes & CSlots**：可以将 CNode 视为 cap 数组，数组元素被称为 CSlot ，CSlot 可以看成是 `Option<Cap>` 类型。`1 << info->CNodeSizeBits` 表示数组大小，`1 << seL4_SlotBits` 表示 CSlot 大小。每个 thread 的 TCB 中有一个 CNode cap ，即 CSpace root 。Invocation 会隐式地通过 CSpace root 访问 CNode ，并通过其中的 CSlot 访问资源。可以通过以下字段寻址 CSlot：
  
  - _service/root：对应的 CNode cap
  - index：CSlot 在 CNode 中的下标
  - depth：默认为 `seL4_WordBits` （寻址 `index << seL4_WordBits`）
  
以 root task 为例， 访问 TCB 的过程大致为 `seL4_CapInitThreadCNode -> CNode -> seL4_CapInitThreadTCB -> TCB` 。`seL4_bootInfo` 描述了初始 CSpace 中的 cap 和空闲 CSlot 。

支持 [Rocket](https://docs.sel4.systems/Hardware/rocketchip.html) 硬件平台。


## Syscalls

相关定义位于 libsel4/include/api/syscall.xml 。

- Call
- ReplyRecv
- Send
- NBSend
- Recv
- Reply
- Yield
- NBRecv

## seL4 改动 (ZRQ 2023.6)

改动类似 Linux，包括系统调用实现和外设支持。

- include/arch/riscv/arch/uintr.h: 定义 uintr 相关结构体，声明系统调用函数接口，声明相关状态保存与恢复函数。
- include/drivers/irq/riscv_uintc.h: 定义 uintc 相关结构体，声明 uintc 读写函数。
- libsel4/include/api/syscall.xml: 定义 syscall_register_receiver 和 syscall_register_sender
- src/api/syscall.c: handleSyscall 入口，跳转到新定义的 syscall
- src/arch/c_traps.c: trap 返回前（restore_user_context 函数）插入 uintr_return 函数恢复相关寄存器
- src/arch/riscv/config.cmake: 添加 uintr.c 的编译选项
- src/arch/riscv/traps.S: 陷入汇编代码，寄存器保存，中断异常跳转
- src/arch/riscv/uintr.c: Linux 内注册结构体需要利用全局变量
  - syscall_register_receiver: 注册用户态中断接收方（每个 TCB 只能注册一次），分配 uintc 槽位，返回 uintc 下标
  - syscall_register_sender: 注册用户态中断发送方（多次注册也只初始化一次状态表），根据 uintc 下标和对应标识号分配状态表项
- tools/dts/spike.dts: 加入 uintc 设备书节点
- tools/hardware.yml: 加入 uintc 描述信息
- tools/tmp.h: 由 c_header.py 自动生成

由于目前的结构都是全局静态分配的，所以还没有实现资源的释放。

一些可能会用到的函数：

- NODE_STATE(ksCurThread) 获取当前 TCB 指针
- setRegister(tcb, a0, uintc_idx): 将 uintc_idx 作为系统调用结果返回
- restore_user_context: 出现在 slowpath, fastpath 和 init_kernel 之后
- kpptr_to_paddr 将虚拟地址翻译为物理地址

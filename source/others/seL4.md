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

## MCS




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

seL4 riscv 的 syscall 实现位于 libsel4/arch_include/riscv/sel4/arch/syscalls.h ，对上暴露的 API 保持一致，内部实现 `riscv_sys_send` ，`riscv_sys_send_null` 等函数，这些函数基本的执行逻辑为通过 `ecall` 指令陷入内核并通过寄存器传递参数。重点关注 `seL4_Signal` 这个系统调用，目前默认的实现方法为：

```c
LIBSEL4_INLINE_FUNC void seL4_Signal(seL4_CPtr dest)
{
    riscv_sys_send_null(seL4_SysSend, dest, seL4_MessageInfo_new(0, 0, 0, 0).words[0]);
}

static inline void riscv_sys_send_null(seL4_Word sys, seL4_Word src, seL4_Word info_arg)
{
    register seL4_Word destptr asm("a0") = src;
    register seL4_Word info asm("a1") = info_arg;

    /* Perform the system call. */
    register seL4_Word scno asm("a7") = sys;
    asm volatile(
        "ecall"
        : "+r"(destptr), "+r"(info)
        : "r"(scno)
    );
}
```

相当于和 `seL4_Send` 共用了内核接口，换句话说，可以将 `seL4_Signal` 视为消息长度为空的 `seL4_Send` 。

系统调用号例如 `seL4_SysYield` 等是在编译后确定的。

注意到开关 MCS 参数前后，系统调用的实现方式是不一样的。




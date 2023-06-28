# seL4

本文档的分析主要基于 RISC-V 架构。

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

## Capability

    A capability is a unique, unforgeable token that gives the possessor permission to access an entity or object in system. 

**Capability (cap)** 是 seL4 的核心机制，通过唯一且不可伪造的 token 来获取对象的访问权限，可以将 cap 视为带有访问控制的指针。

**root task** 在初始化时会获取所有资源的 cap ，例如 `seL4_CapInitThreadTCB`，可以通过 API 读取或修改 TCB 的内容。

**CSpace** 表示一个 thread 持有的全部 cap 。

**CNodes & CSlots**：可以将 CNode 视为 cap 数组，数组元素被称为 CSlot ，CSlot 可以看成是 `Option<Cap>` 类型。`1 << info->CNodeSizeBits` 表示数组大小，`1 << seL4_SlotBits` 表示 CSlot 大小。每个 thread 的 TCB 中有一个 CNode cap ，即 CSpace root 。Invocation 会隐式地通过 CSpace root 访问 CNode ，并通过其中的 CSlot 访问资源。可以通过以下字段寻址 CSlot：
  
  - _service/root：对应的 CNode cap
  - index：CSlot 在 CNode 中的下标
  - depth：默认为 `seL4_WordBits` （寻址 `index << seL4_WordBits`）
  
以 root task 为例， 访问 TCB 的过程大致为 `seL4_CapInitThreadCNode -> CNode -> seL4_CapInitThreadTCB -> TCB` 。`seL4_bootInfo` 描述了初始 CSpace 中的 cap 和空闲 CSlot 。

## TCB

从 `struct tcb` 出发，分析其成员的含义：

- `arch_tcb_t tcbArch`：arch 相关的状态，主要包含上下文的内容。逐级展开可以的得到 `word_t registers[n_contextRegisters]`，相关定义位于 `enum _register`，除了 31 个通用寄存器外（不包括 zero），还包含 `sstatus` 和 `scause` 等，可以在其中加入其他需要保存和恢复的用户态寄存器。
- `thread_state_t tcbState`：线程状态，主要包括：
  - `ThreadState_Inactive`：
  - `ThreadState_Running`：
  - `ThreadState_Restart`：
  - `ThreadState_BlockedOnReceive`：
  - `ThreadState_BlockedOnSend`：
  - `ThreadState_BlockedOnReply`：
  - `ThreadState_BlockedOnNotification`：
- `notification_t *tcbBoundNotification`：指向该线程对应的 Notification ，若该指针非空，该线程可以接收 Signalsh ceshce
- `seL4_Fault_t tcbFault`：
- `lookup_fault_t tcbLookupFailure`：
- `dom_t tcbDomain`：
- `prio_t tcbMCP`：
- `prio_t tcbPriority`：线程优先级
- `sched_context_t *tcbSchedContext`：该线程对应的调度上下文，若该指针为空，线程不可被加入调度队列
- `sched_context_t *tcbYieldTo`：线程切换至的调度上下文
- `word_t tcbIPCBuffer`：用户空间的 IPC 缓冲区的虚拟地址
- `word_t tcbAffinity`：正在运行该线程的核号
- `struct tcb *tcbSchedNext, *tcbSchedPrev`：调度队列的链表指针
- `struct tcb *tcbEPNext, *tcbEPPrev`：Notification 队列的链表指针

实际的 TCB 还包括头部的 `cte_t` ，`tcb_t` 默认占据 TCB 的后半部分空间。

```c
// A diagram of a TCB kernel object that is created from untyped:
//  _______________________________________
// |     |             |                   |
// |     |             |                   |
// |cte_t|   unused    |       tcb_t       |
// |     |(debug_tcb_t)|                   |
// |_____|_____________|___________________|
// 0     a             b                   c
// a = tcbCNodeEntries * sizeof(cte_t)
// b = BIT(TCB_SIZE_BITS)
// c = BIT(seL4_TCBBits)
```

## MCS



## IPC

```
block endpoint {
    field epQueue_head 64
    field_high epQueue_tail 37
    field state 2
}
```

## Notification

```
block notification {
#ifdef CONFIG_KERNEL_MCS
    field_high ntfnSchedContext 39
#endif
    field_high ntfnBoundTCB 39
    field ntfnMsgIdentifier 64
    field_high ntfnQueue_head 39
    field_high ntfnQueue_tail 39
    field state 2
}
```

三种状态：

- Idle
- Waiting
- Active

内核函数：

- `void sendSignal(notification_t *ntfnPtr, word_t badge)`：
- `void cancelSignal(tcb_t *threadPtr, notification_t *ntfnPtr)`：

## Boot

从 `head.S` 入手分析 kernel 的启动流程：

```asm
  /* Call bootstrapping implemented in C with parameters:
   *    a0/x10: user image physical start address
   *    a1/x11: user image physical end address
   *    a2/x12: physical/virtual offset
   *    a3/x13: user image virtual entry address
   *    a4/x14: DTB physical address (0 if there is none)
   *    a5/x15: DTB size (0 if there is none)
   *    a6/x16: hart ID (SMP only, unused on non-SMP)
   *    a7/x17: core ID (SMP only, unused on non-SMP)
   */
_start:
  fence.i
.option push
.option norelax
1:auipc gp, %pcrel_hi(__global_pointer$)
  addi  gp, gp, %pcrel_lo(1b)
.option pop

/* 多核下为每个核分配栈空间 */
  la sp, (kernel_stack_alloc + BIT(CONFIG_KERNEL_STACK_BITS))
  csrw sscratch, x0 /* zero sscratch for the init task */
#if CONFIG_MAX_NUM_NODES > 1
  mv t0, a7
  slli t0, t0, CONFIG_KERNEL_STACK_BITS
  add  sp, sp, t0
  csrw sscratch, sp
#endif
  /* 内核初始化 */
  jal init_kernel
  /* 恢复用户态上下文（返回到 rootserver） */
  la ra, restore_user_context
  jr ra

```

相关函数：

- `BOOT_CODE tcb_t *create_initial_thread(cap_t root_cnode_cap, cap_t it_pd_cap, vptr_t ui_v_entry, vptr_t bi_frame_vptr, vptr_t ipcbuf_vptr, cap_t ipcbuf_cap)`：创建并初始化 init 线程。

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




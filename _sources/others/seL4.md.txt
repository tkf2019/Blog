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

常用内核函数：

- `void tcbEPDequeue(tcb_t *tcb, tcb_queue_t queue)`：将当前 TCB 从队列（EP 或 Ntfn 的等待队列）中移除
- `cpu_id_t getCurrentCPUIndex(void)`：从 `sscratch` 寄存器中读出当前核号
- `void tcbSchedEnqueue(tcb_t *tcb)`：将 TCB 置于调度队列的头部
- `void tcbSchedAppend(tcb_t *tcb)`：将 TCB 置于调度队列的头部
- `void remoteQueueUpdate(tcb_t *tcb)`：发送 `ipiReschedulePending` 更新目标核的调度目标
- `void setRegister(tcb_t *thread, register_t reg, word_t w)`：设置寄存器`thread->tcbArch.tcbContext.registers[reg] = w`

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
    field_high ntfnBoundTCB 39      // 指向绑定的 TCB
    field ntfnMsgIdentifier 64      // msg 标识符
    field_high ntfnQueue_head 39    // 等待队列头部
    field_high ntfnQueue_tail 39    // 等待队列尾部
    field state 2                   // 当前状态
}

block notification_cap {
    field capNtfnBadge 64      // badge 标识符
    field capType 5            // cap 类型
    field capNtfnCanReceive 1  // 可以接收
    field capNtfnCanSend 1     // 可以发送
    field_high capNtfnPtr 39   // 指向 notification 内核结构
}
```

`state` 字段指定 Notification 的三种状态：

- **NtfnState_Waiting**：TCB 在队列中等待接收信号
- **NtfnState_Active**：TCB 接收到信号
- **NtfnState_Idle**：以上两种状态之外的状态

### 内核相关函数

- `void bindNotification(tcb_t *tcb, notification_t *ntfnPtr)`：将 notification 绑定到指定的 TCB ，将 ntfnPtr 赋值给 tcbBoundNotification ，将 tcb 赋值给 ntfnBoundTCB 
- `void unbindNotification(tcb_t *tcb)`：取消绑定
- `void sendSignal(notification_t *ntfnPtr, word_t badge)`：不同的状态处理方法不同：
  - NtfnState_Idle：如果绑定到 TCB ，则根据 Thread 当前状态进行判断，若处于 ThreadState_BlockedOnReceive ，切换到该 TCB 开始运行，并设置 badge 标识符
  - NtfnState_Waiting：从等待队列中取出一个唤醒并开始执行，如果队列变为空则转为 NtfnState_Idle 状态
  - NtfnState_Active：已经有正在等待响应的 badge 了，直接与当前 badge 进行或操作
- `void receiveSignal(tcb_t *thread, cap_t cap, bool_t isBlocking)`：根据 cap 获取 Notification 对象指针，不同状态的处理方法不同：
  - NtfnState_Idle 和 NtfnState_Waiting：若采用阻塞方法（isBlocking 为 1），则设置 TCB 状态为 ThreadState_BlockedOnNotification ，并设置 TCB 的 blockingObject 为当前 ntfnPtr ，将 TCB 放到 Ntfn 等待队列尾部等待唤醒，转为 NtfnState_Waiting 状态
  - NtfnState_Active：将 TCB 的 badgeRegister 设置为 ntfnMsgIdentifier ，转为 NtfnState_Idle 状态

### 用户相关函数

- `void seL4_Wait(seL4_CPtr src, seL4_Word *sender)`：即 seL4_Recv
- `void seL4_Poll(seL4_CPtr src, seL4_Word *sender)`：即 seL4_NBRecv
- `void seL4_Signal(seL4_CPtr dest)`：即 seL4_Send

## IRQ

相关 Cap 如下：

- **IRQControl**：由 root 进行管理，不可被复制
- **IRQHandler**：通过调用 IRQControl 获取对应中断的访问权限，可以被复制；通过 `seL4_IRQControl_Get(seL4_IRQControl _service, seL4_Word irq, seL4_CNode root, seL4_Word index, seL4_Uint8 depth)` 获取

`seL4_IRQHandler_SetNotification` 将 IRQHandler 绑定至 Notification 接收中断，如果想让 Notification 接收多个中断，可以让 badge 绑定至不同的 IRQHandler 。中断可以通过 `seL4_Poll` 或 `seL4_Wait` 来感知。通过 Notification 接收中断并进行处理后，可以通过 `seL4_IRQHandler_Ack` 来响应中断（准备接收下一个中断）或 `seL4_IRQHandler_Clear` 来取消绑定。 

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
  /* 恢复用户态上下文（返回到 root） */
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

## [seL4test](https://github.com/seL4/sel4test/blob/master/docs/design.md)

root 是 sel4test-driver ，启动时获取 `seL4_Bootinfo_t` ，为测例的运行提供环境。bootstrap 运行环境主要是为了测试创建进程和与其通信的功能是否正常。root 通过 linker section 来在运行时选择测例，可以通过字符串匹配在编译期对测例进行选择。测例是依次运行的，root 可以选择是否在测例运行失败后中止测试。

sel4test-driver 运行流程：

```
main ->
  main_continued ->
    sel4test_run_tests ->
      test_types[tt]->run_test(tests[i])
```

sel4test_run_tests 根据 `__start__test_type` 到 `__stop__test_type` 加载 `struct test_type` 信息，对 test 进行过滤后依次运行每个 test （不同 test_type 可以有多个 test）。

=================
User Interrupt
=================

--------------
Intel UINTR
--------------

++++++++++++++
Intro.
++++++++++++++

User interrupts are delivered to software operating in 64-bit mode with CPL=3 without any change to segmentation state. Different user interrupts are distinguished by a 6-bit user-interrupt vector. Based on x86, the UINTR state is configured by new supervisor-managed state, including new MSRs.

**UPID** : user posted-interrupt descriptor. User interrupts for an OS-managed thread can be posted in the UPID associated with that thread after receipt of an ordinary interrupt called a **user-interrupt notification**. 

- Outstanding notification (0): For one or more user interrupts in PIR (as ``|pir_bits``).
- Suppress notification (1): If set, agents should not send notifications when posting user interrupts in this descriptor.
- Notification vector (23:16): Used by SENDUIPI.
- Notification destination (63:32): Target physical APIC ID.
- Posted-interrupt requests (PIR) (127:64): One bit for each user-interrupt vector. See UIRR.

Setting ``CR4[25] (as CR4.UINTR)`` enables user-interrupt delivery, user-interrupt notification identification and the user-interrupt instructions (UIRET, SENDUIPI). 

**User-interrupt State** :

- **UIRR** : If UIRR[i] = 1, a user interrupt with vector i is requesting service.
- **UIF** : If UIF = 0, user-interrupt delivery is blocked; if UIF = 1, user interrupts may be delivered. User-interrupt delivery clears UIF, and the new UIRET instruction sets it.
- **UIHANDLER** : The linear address of the user-interrupt handler.
- **UISTACKADJUST** : This value controls adjustment to the stack pointer prior to user-interrupt delivery.
- **UINV** : The vector of those ordinary interrupts that are treated as user-interrupt notifications.
- **UPIDADDR** : The linear address of the UPID that the logical processor consults upon receiving an ordinary interrupt with vector UINV.
- **UITTADDR** : The linear address of user-interrupt target table, which the logical processor consults when software invokes the SENDUIPI instruction.
- **UITTSZ** : The highest index of a valid entry in the UITT.

**User-interrupt MSRs** :

- IA32_UINTR_RR -> UIRR
- IA32_UINTR_HANDLER -> UIHANDLER
- IA32_UINTR_STACKADJUST -> UISTACKADJUST
- IA32_UINTR_MISC -> {24'b0, UINV[7:0], UITTSZ[31:0]}
- IA32_UINTR_PD -> UPIDADDR
- IA32_UINTR_TT -> UITTADDR 

**User-interrupt notification identification** : How to identify an ordinary interrupt as user-interrupt notification? The local **APIC** is acknowledged; move to the next step if the processor get an interrupt vector V = UINV. The processor writes zero to the EOI register in the local APIC; this dismiss the interrupt with vector V = UINV from the local APIC.

.. admonition:: APIC

    Advanced Programmable Interrupt Controller. Intended to solve interrupt routing efficiency issues in computer systems.
    In a APIC-based system, each CPU is made of a core and a local APIC. In addition, there is an I/O APIC that is part of the chipset and provides multi-processor interrupt management.
    Each interrupt pin is individually programmable as either edge or level triggered. The interrupt vector and interrupt steering information can be specified per interrupt.

**User-interrupt notification processing** :

- The logical processor clears the outstanding-notification bit in the UPID. This is done atomically so as to leave the remainder of the descriptor unmodified.
- The logical processor reads PIR into a temporary register and writes all zeros to PIR. This is done atomically so as to ensure that each bit cleared is set in the temporary register.
- If any bit is set in the temporary register, the logical processor sets in UIRR each bit corresponding to a bit set in the temporary register and recognize a pending user interrupt.

++++++++++++++++
Impl. in Linux
++++++++++++++++

UPID and UITT are managed by kernel. 

Instructions: 

- SENDUIPI <index>: send a user IPI to a target task based on the UITT index.
- CLUI: Mask user interrupts by clearing UIF.
- STUI: Unmask user interrupts by setting UIF.
- TESTUI: Test current value of UIF.
- UIRET: return from a user interrupt handler.

UITT entry:

- (0): V, a valid bit
- (7:1): reserved
- (15:8): UV, the user-interrupt vector (15:14 is wired to zero)
- (63:16): reserved
- (127:64): UPIDADDR (64-byte aligned, so 69:64 is wired to zero)

See implementations in `uintr_linux <https://github.com/intel/uintr-linux-kernel>`_ .

.. code-block:: c
    :linenos:

    /* Vector for User interrupt notifications */
    #define UINTR_NOTIFICATION_VECTOR       0xec
    #define UINTR_KERNEL_VECTOR		        0xeb

    int do_uintr_register_handler(u64 handler)
    {
        struct uintr_receiver *ui_recv;
        struct uintr_upid *upid;
        struct task_struct *t = current;
        struct fpu *fpu = &t->thread.fpu;
        u64 misc_msr;
        int cpu;

        if (is_uintr_receiver(t))
            return -EBUSY;

        /* Alloc new uintr receiver with UPID */
        ui_recv = kzalloc(sizeof(*ui_recv), GFP_KERNEL);
        ui_recv->upid_ctx = alloc_upid();

        /*
    	 * UPID and ui_recv will be referenced during context switch. Need to
    	 * disable preemption while modifying the MSRs, UPID and ui_recv thread
    	 * struct.
    	 */
    	fpregs_lock();
        
        /* Find the receiver and set the notification vector and destination */
        cpu = smp_processor_id();
        upid = ui_recv->upid_ctx->upid;
        upid->nc.nv = UINTR_NOTIFICATION_VECTOR;
        upid->nc.ndst = cpu_to_ndst(cpu);

        t->thread.ui_recv = ui_recv;

        if (fpregs_state_valid(fpu, cpu)) {
            wrmsrl(MSR_IA32_UINTR_HANDLER, handler);
            wrmsrl(MSR_IA32_UINTR_PD, (u64)ui_recv->upid_ctx->upid);

            /* Set value as size of ABI redzone */
            wrmsrl(MSR_IA32_UINTR_STACKADJUST, 128);

            /* Modify only the relevant bits of the MISC MSR */
            rdmsrl(MSR_IA32_UINTR_MISC, misc_msr);
            misc_msr |= (u64)UINTR_NOTIFICATION_VECTOR << 32;
            wrmsrl(MSR_IA32_UINTR_MISC, misc_msr);
        } else {
            struct xregs_state *xsave;
            struct uintr_state *p;

            xsave = &fpu->state.xsave;
            xsave->header.xfeatures |= XFEATURE_MASK_UINTR;
            p = get_xsave_addr(&fpu->state.xsave, XFEATURE_UINTR);
            if (p) {
                p->handler = handler;
                p->upid_addr = (u64)ui_recv->upid_ctx->upid;
                p->stack_adjust = 128;
                p->uinv = UINTR_NOTIFICATION_VECTOR;
            }
        }

        fpregs_unlock();

        return 0;
    }

    int do_uintr_register_vector(struct uintr_receiver_info *r_info)
    {
        struct uintr_receiver *ui_recv;
        struct task_struct *t = current;
        /*
        * A vector should only be registered by a task that
        * has an interrupt handler registered.
        */
        if (!is_uintr_receiver(t)) return -EINVAL;
        if (r_info->uvec >= UINTR_MAX_UVEC_NR) return -ENOSPC;
        ui_recv = t->thread.ui_recv;
        if (ui_recv->uvec_mask & BIT_ULL(r_info->uvec)) return -EBUSY;
        ui_recv->uvec_mask |= BIT_ULL(r_info->uvec);
        r_info->upid_ctx = get_upid_ref(ui_recv->upid_ctx);
        return 0;
    }

``int do_uintr_register_handler(u64 handler)`` allocates new user-interrupt context and UPID for current task.
It disables preemption (the ability of the operating system to preempt or stop a currently scheduled task in favour of a higher priority task) during modifying task states.
Then it sets the destination as target APIC id. It writes MSRs finally (or xsave states) to activate hardware process.

.. code-block:: c
    :linenos:

    int do_uintr_register_sender(struct uintr_receiver_info *r_info,
			     struct uintr_sender_info *s_info)
    {
        struct uintr_uitt_entry *uitte = NULL;
        struct uintr_sender *ui_send;
        struct task_struct *t = current;
        unsigned long flags;
        int entry;
        int ret;

        /*
        * Only a static check. Receiver could exit anytime after this check.
        * This check only prevents connections using uintr_fd after the
        * receiver has already exited/unregistered.
        */
        if (!uintr_is_receiver_active(r_info))
            return -ESHUTDOWN;

        if (is_uintr_sender(t)) {
            entry = find_first_zero_bit((unsigned long *)t->thread.ui_send->uitt_mask,
                            UINTR_MAX_UITT_NR);
            if (entry >= UINTR_MAX_UITT_NR)
                return -ENOSPC;
        } else {
            BUILD_BUG_ON(UINTR_MAX_UITT_NR < 1);
            entry = 0;
            ret = init_uitt();
            if (ret)
                return ret;
        }

        ui_send = t->thread.ui_send;

        set_bit(entry, (unsigned long *)ui_send->uitt_mask);

        spin_lock_irqsave(&ui_send->uitt_ctx->uitt_lock, flags);
        uitte = &ui_send->uitt_ctx->uitt[entry];
        pr_debug("send: sender=%d receiver=%d UITTE entry %d address %px\n",
            current->pid, r_info->upid_ctx->task->pid, entry, uitte);

        uitte->user_vec = r_info->uvec;
        uitte->target_upid_addr = (u64)r_info->upid_ctx->upid;
        uitte->valid = 1;
        spin_unlock_irqrestore(&ui_send->uitt_ctx->uitt_lock, flags);

        s_info->r_upid_ctx = get_upid_ref(r_info->upid_ctx);
        s_info->uitt_ctx = get_uitt_ref(ui_send->uitt_ctx);
        s_info->task = get_task_struct(current);
        s_info->uitt_index = entry;

        return 0;
    }


.. code-block:: c
    :linenos:

    int uintr_receiver_wait(void)
    {
        struct uintr_upid_ctx *upid_ctx;
        unsigned long flags;

        if (!is_uintr_receiver(current))
            return -EOPNOTSUPP;

        upid_ctx = current->thread.ui_recv->upid_ctx;
        upid_ctx->upid->nc.nv = UINTR_KERNEL_VECTOR;
        upid_ctx->waiting = true;
        spin_lock_irqsave(&uintr_wait_lock, flags);
        list_add(&upid_ctx->node, &uintr_wait_list);
        spin_unlock_irqrestore(&uintr_wait_lock, flags);

        set_current_state(TASK_INTERRUPTIBLE);
        schedule();

        return -EINTR;
    }

    /*
     * Runs in interrupt context.
     * Scan through all UPIDs to check if any interrupt is on going.
     */
    void uintr_wake_up_process(void)
    {
    	struct uintr_upid_ctx *upid_ctx, *tmp;
    	unsigned long flags;

    	spin_lock_irqsave(&uintr_wait_lock, flags);
    	list_for_each_entry_safe(upid_ctx, tmp, &uintr_wait_list, node) {
    		if (test_bit(UPID_ON, (unsigned long *)&upid_ctx->upid->nc.status)) {
    			set_bit(UPID_SN, (unsigned long *)&upid_ctx->upid->nc.status);
    			upid_ctx->upid->nc.nv = UINTR_NOTIFICATION_VECTOR;
    			upid_ctx->waiting = false;
    			wake_up_process(upid_ctx->task);
    			list_del(&upid_ctx->node);
    		}
    	}
    	spin_unlock_irqrestore(&uintr_wait_lock, flags);
    }

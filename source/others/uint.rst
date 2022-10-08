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
    More information can be seen `here <>`_.

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

----------
io_uring
----------
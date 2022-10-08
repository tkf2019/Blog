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

1.  User-interrupt Recognition
(1) 
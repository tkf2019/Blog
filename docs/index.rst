.. raw:: html

   <div class="profile-page">
     <aside class="profile-sidebar">
      <img class="profile-photo" src="me.jpg" alt="Kaifu Tian profile photo" />
       <h1>Kaifu Tian</h1>
       <p class="profile-title">Ph.D. Student / Systems Researcher</p>
       <p class="profile-affiliation">Department of Computer Science and Technology, Tsinghua University</p>
        <ul class="contact-list">
          <li><i class="contact-icon icon-solid icon-envelope" aria-hidden="true"></i><a href="mailto:kaifu6821@qq.com">kaifu6821@qq.com</a></li>
          <li><i class="contact-icon icon-solid icon-phone" aria-hidden="true"></i>+86 15944806118</li>
          <li><i class="contact-icon icon-solid icon-location" aria-hidden="true"></i>Beijing, China</li>
          <li><i class="contact-icon icon-brands icon-github" aria-hidden="true"></i><a href="https://github.com/tkf2019" target="_blank" rel="noopener noreferrer">github.com/tkf2019</a></li>
        </ul>
     </aside>

     <main class="profile-main">

Bio
=======

I am a third-year Ph.D. student in the Operating Systems Laboratory at Tsinghua University, advised by Prof. Yu Chen. My research focuses on operating systems, including scheduling, networking, and storage. I study hardware-software co-design and kernel-bypass techniques to improve system performance.

Education
=========

- **Tsinghua University**, Ph.D. in Computer Science and Technology, 2023.8 - present

  Recipient of the 2025 Comprehensive Scholarship. Expected graduation: June 2028.

- **Tsinghua University**, B.Eng. in Computer Science and Technology, 2019.8 - 2023.7

  Recipient of the 2019 Freshman Scholarship, 2020 Academic Excellence Scholarship, and 2022 Comprehensive Scholarship.

Research
========

- Yuekai Jia*, **Kaifu Tian***, Yuyang You, Yu Chen, Kang Chen.
  **Skyloft: A General High-Efficient Scheduling Framework in User Space**.
  *SOSP 2024*.

  .. raw:: html

      <div class="paper-actions">
        <a class="paper-btn" href="_static/sosp24-skyloft.pdf" target="_blank" rel="noopener noreferrer">Paper</a>
        <a class="paper-btn" href="papers/paper-skyloft.html">Overview</a>
      </div>

  - Skyloft leverages user interrupts to support kernel-bypassing preemption, and is the first general user-space scheduling framework for multi-application workloads with microsecond-scale preemptive scheduling.
  - Skyloft introduces a scheduler development paradigm that builds diverse schedulers with a small set of common operations; policies that previously required heavy customization can now be implemented in only a few hundred lines.
  - Under both synthetic and real workloads on mainstream applications, Skyloft delivers performance that is competitive with, and often better than, existing solutions.

Internship
==========

- **Beijing Institute of Open Source Chip**, Intern, 2025.6 - 2025.8
  System Cache stream prefetcher design and implementation.

Competition Awards
==================

- **6th Loongson Cup**, Team First Prize, 2022

  - Implemented an out-of-order superscalar CPU in SystemVerilog, supporting two-level register renaming, dual-fetch triple-issue, and early wake-up for cached loads.
  - Debugged CPU implementation with the Difftest framework.
  - Achieved a final frequency of 120 MHz, capable of running Linux and Busybox.


.. raw:: html

   </main>
   </div>

.. toctree::
   :maxdepth: 2
   :hidden:

   logs/index
   papers/index

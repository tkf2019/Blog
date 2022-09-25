-----------
Theseus
-----------

.. admonition:: Links

    https://www.usenix.org/conference/osdi20/presentation/narayanan-vikram

    https://github.com/mars-research/redleaf

    https://www.usenix.org/conference/osdi20/presentation/boos

    https://github.com/theseus-os/Theseus

Safety over all alse (convenience, performance)

Single address space (SAS), Single privilege level (SPL)

Structure of cells:

- persistence of cell bounds reduces complexity: 
- striking a balance with cell granularity: extract would-be modules into distinct crates (organized into folders)

Boot by ```nono_core```:

1. Cells statically linked into a kernel image, comprising only components needed to bootstrap a bare-minimum environment (vm, loading/linking object files).
2. The `nano_core` fully replaces itself at the final bootstrap stage by dinamically loading its constituent cells one by one.
3. The `nano_core` image is unloaded after bootstrap.

Intralingual design:

- Uses Rust's built-in reference types ``&T`` and ``Arc<T>``
- Employs lossless interfaces (presering all language-level context)
- Implements all cleanup semantics in drop handlers
- Employs stack unwinding

Memory management:

- The mapping from virtual pages to physical frames must be one-to-one, which prevents aliasing, an extralingual approach that renders sharing transparent to the compiler and thus uncheckable for safety.
- Memory must be accessible beyond the mapped region's bounds.
- A memory region must be unmapped exactly once, only after there remain no outstanding references to it. (Tie the lifetime of the re-typed borrowed reference `&'m T` to the lifetime of its backing memory region)
- A memory region must only be mutable or executable if mapped as such.

Task management:

- Spawning a new task must not violate memory safety.
- All task states must be released in all possible execution paths.
- All memory transitively reachable from a task's entry function must outlive that task.


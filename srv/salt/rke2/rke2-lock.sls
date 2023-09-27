/etc/rke2.lock:
  file.managed:
    - contents: |
        This file is to prevent rke2.uninstall execution.
        If you need to uninstall rke2 then you have to remove this file first.

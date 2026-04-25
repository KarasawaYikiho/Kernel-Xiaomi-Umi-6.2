#!/sbin/sh
# Minimal local AnyKernel candidate template for umi.

properties() {
  echo "kernel.string=Kernel-Xiaomi-Umi candidate"
  echo "do.devicecheck=1"
  echo "do.modules=0"
  echo "do.cleanup=1"
  echo "device.name1=umi"
  echo "device.name2="
  echo "device.name3="
  echo "supported.versions="
  echo "supported.patchlevels="
}

block=boot
is_slot_device=0
ramdisk_compression=auto

ui_print() { :; }

dump_boot() { :; }
write_boot() { :; }
reset_ak() { :; }

properties

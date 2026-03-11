# Official ROM Package Analysis (UMI OS1.0.5.0.TJBCNXM)

- Source File: `D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip`
- Zip Size Bytes: `4413290022`
- Zip SHA256: `1e6f5eba43219dfeead7395387c0e2eba9ff49c310917b9cf22092963f7adba1`
- Entry Count: `48`
- Top-Level Entries: `META-INF, boot.img, dynamic_partitions_op_list, firmware-update, mi_ext.new.dat.br, mi_ext.patch.dat, mi_ext.transfer.list, odm.new.dat.br, odm.patch.dat, odm.transfer.list, product.new.dat.br, product.patch.dat, product.transfer.list, system.new.dat.br, system.patch.dat, system.transfer.list, system_ext.new.dat.br, system_ext.patch.dat, system_ext.transfer.list, vendor.new.dat.br, vendor.patch.dat, vendor.transfer.list`

## Package Metadata
```text
ota-property-files=metadata:69:328,metadata.pb:465:206
ota-required-cache=0
ota-type=BLOCK
post-build=Xiaomi/umi/umi:13/TKQ1.221114.001/V816.0.5.0.TJBCNXM:user/release-keys
post-build-incremental=V816.0.5.0.TJBCNXM
post-sdk-level=33
post-security-patch-level=2024-03-01
post-timestamp=1717592892
pre-device=umi
```

## Dynamic Partitions Operation List
```text
# Remove all existing dynamic partitions and groups before applying full OTA
remove_all_groups
# Add group qti_dynamic_partitions with maximum size 9126805504
add_group qti_dynamic_partitions 9126805504
# Add partition system to group qti_dynamic_partitions
add system qti_dynamic_partitions
# Add partition vendor to group qti_dynamic_partitions
add vendor qti_dynamic_partitions
# Add partition product to group qti_dynamic_partitions
add product qti_dynamic_partitions
# Add partition odm to group qti_dynamic_partitions
add odm qti_dynamic_partitions
# Add partition system_ext to group qti_dynamic_partitions
add system_ext qti_dynamic_partitions
# Add partition mi_ext to group qti_dynamic_partitions
add mi_ext qti_dynamic_partitions
# Grow partition system from 0 to 1203900416
resize system 1203900416
# Grow partition vendor from 0 to 1740369920
resize vendor 1740369920
# Grow partition product from 0 to 4297064448
resize product 4297064448
# Grow partition odm from 0 to 134217728
resize odm 134217728
# Grow partition system_ext from 0 to 664535040
resize system_ext 664535040
# Grow partition mi_ext from 0 to 2646016
resize mi_ext 2646016
```

## Updater Script (Key Excerpt)
```text
(!less_than_int(1717593555, getprop("ro.build.date.utc"))) || abort("E3003: Can't install this package (Wed Jun  5 13:19:15 UTC 2024) over newer build (" + getprop("ro.build.date") + ").");
getprop("ro.product.device") == "umi" || abort("E3004: This package is for \"umi\" devices; this is a \"" + getprop("ro.product.device") + "\".");
ui_print("Target: Xiaomi/umi/umi:13/RKQ1.211001.001/V816.0.5.0.TJBCNXM:user/release-keys");

# ---- radio update tasks ----

ui_print("Patching firmware images...");
package_extract_file("firmware-update/abl.elf", "/dev/block/bootdevice/by-name/abl");
package_extract_file("firmware-update/aop.mbn", "/dev/block/bootdevice/by-name/aop");
package_extract_file("firmware-update/BTFM.bin", "/dev/block/bootdevice/by-name/bluetooth");
package_extract_file("firmware-update/cmnlib64.mbn", "/dev/block/bootdevice/by-name/cmnlib64");
package_extract_file("firmware-update/cmnlib.mbn", "/dev/block/bootdevice/by-name/cmnlib");
package_extract_file("firmware-update/devcfg.mbn", "/dev/block/bootdevice/by-name/devcfg");
package_extract_file("firmware-update/dspso.bin", "/dev/block/bootdevice/by-name/dsp");
package_extract_file("firmware-update/featenabler.mbn", "/dev/block/bootdevice/by-name/featenabler");
package_extract_file("firmware-update/hyp.mbn", "/dev/block/bootdevice/by-name/hyp");
package_extract_file("firmware-update/km4.mbn", "/dev/block/bootdevice/by-name/keymaster");
package_extract_file("firmware-update/NON-HLOS.bin", "/dev/block/bootdevice/by-name/modem");
package_extract_file("firmware-update/qupv3fw.elf", "/dev/block/bootdevice/by-name/qupfw");
package_extract_file("firmware-update/storsec.mbn", "/dev/block/bootdevice/by-name/storsec");
package_extract_file("firmware-update/tz.mbn", "/dev/block/bootdevice/by-name/tz");
package_extract_file("firmware-update/uefi_sec.mbn", "/dev/block/bootdevice/by-name/uefisecapp");
package_extract_file("firmware-update/xbl_4.elf", "/dev/block/bootdevice/by-name/xbl_4");
package_extract_file("firmware-update/xbl_5.elf", "/dev/block/bootdevice/by-name/xbl_5");
package_extract_file("firmware-update/xbl_config_4.elf", "/dev/block/bootdevice/by-name/xbl_config_4");
package_extract_file("firmware-update/xbl_config_5.elf", "/dev/block/bootdevice/by-name/xbl_config_5");
package_extract_file("firmware-update/abl.elf", "/dev/block/bootdevice/by-name/ablbak");
package_extract_file("firmware-update/aop.mbn", "/dev/block/bootdevice/by-name/aopbak");
package_extract_file("firmware-update/cmnlib64.mbn", "/dev/block/bootdevice/by-name/cmnlib64bak");
package_extract_file("firmware-update/cmnlib.mbn", "/dev/block/bootdevice/by-name/cmnlibbak");
package_extract_file("firmware-update/devcfg.mbn", "/dev/block/bootdevice/by-name/devcfgbak");
package_extract_file("firmware-update/hyp.mbn", "/dev/block/bootdevice/by-name/hypbak");
package_extract_file("firmware-update/qupv3fw.elf", "/dev/block/bootdevice/by-name/qupfwbak");
package_extract_file("firmware-update/storsec.mbn", "/dev/block/bootdevice/by-name/storsecbak");
package_extract_file("firmware-update/tz.mbn", "/dev/block/bootdevice/by-name/tzbak");

# --- Start patching dynamic partitions ---


# Update dynamic partition metadata

assert(update_dynamic_partitions(package_extract_file("dynamic_partitions_op_list")));

# Patch partition system

ui_print("Patching system image unconditionally...");
show_progress(0.400000, 0);
block_image_update(map_partition("system"), package_extract_file("system.transfer.list"), "system.new.dat.br", "system.patch.dat") ||
  abort("E1001: Failed to update system image.");

# Patch partition vendor

ui_print("Patching vendor image unconditionally...");
show_progress(0.100000, 0);
block_image_update(map_partition("vendor"), package_extract_file("vendor.transfer.list"), "vendor.new.dat.br", "vendor.patch.dat") ||
  abort("E2001: Failed to update vendor image.");

# Patch partition product

ui_print("Patching product image unconditionally...");
show_progress(0.100000, 0);
block_image_update(map_partition("product"), package_extract_file("product.transfer.list"), "product.new.dat.br", "product.patch.dat") ||
  abort("E2001: Failed to update product image.");

# Patch partition odm

ui_print("Patching odm image unconditionally...");
show_progress(0.100000, 0);
block_image_update(map_partition("odm"), package_extract_file("odm.transfer.list"), "odm.new.dat.br", "odm.patch.dat") ||
  abort("E2001: Failed to update odm image.");

# Patch partition system_ext

ui_print("Patching system_ext image unconditionally...");
show_progress(0.100000, 0);
block_image_update(map_partition("system_ext"), package_extract_file("system_ext.transfer.list"), "system_ext.new.dat.br", "system_ext.patch.dat") ||
  abort("E2001: Failed to update system_ext image.");

# Patch partition mi_ext

ui_print("Patching mi_ext image unconditionally...");
show_progress(0.100000, 0);
block_image_update(map_partition("mi_ext"), package_extract_file("mi_ext.transfer.list"), "mi_ext.new.dat.br", "mi_ext.patch.dat") ||
  abort("E2001: Failed to update mi_ext image.");

# --- End patching dynamic partitions ---

package_extract_file("boot.img", "/dev/block/bootdevice/by-name/boot");
show_progress(0.100000, 10);

# ---- radio update tasks 2 ----

ui_print("Patching vbmeta dtbo logo binimages...");
package_extract_file("firmware-update/dtbo.img", "/dev/block/bootdevice/by-name/dtbo");
package_extract_file("firmware-update/logo.img", "/dev/block/bootdevice/by-name/logo");
package_extract_file("firmware-update/vbmeta.img", "/dev/block/bootdevice/by-name/vbmeta");
package_extract_file("firmware-update/vbmeta_system.img", "/dev/block/bootdevice/by-name/vbmeta_system");
set_progress(1.000000);
```

## Firmware Payload Snapshot
- firmware-update entries: `23`
- sample: firmware-update/BTFM.bin, firmware-update/NON-HLOS.bin, firmware-update/abl.elf, firmware-update/aop.mbn, firmware-update/cmnlib.mbn, firmware-update/cmnlib64.mbn, firmware-update/devcfg.mbn, firmware-update/dspso.bin, firmware-update/dtbo.img, firmware-update/featenabler.mbn, firmware-update/hyp.mbn, firmware-update/km4.mbn, firmware-update/logo.img, firmware-update/qupv3fw.elf, firmware-update/storsec.mbn, firmware-update/tz.mbn, firmware-update/uefi_sec.mbn, firmware-update/vbmeta.img, firmware-update/vbmeta_system.img, firmware-update/xbl_4.elf, firmware-update/xbl_5.elf, firmware-update/xbl_config_4.elf, firmware-update/xbl_config_5.elf

## Key Image/Data Entries
- `boot.img`: size=`134217728` sha256=`95f61211e885d05047f152977077d2019e361390b635342b91f6fa8cebd56dca`
- `firmware-update/dtbo.img`: size=`33554432` sha256=`5a4a3cf8fdb3e78c16c7f155f1195eed332cf78993562a36d02bac632d09ab70`
- `firmware-update/vbmeta.img`: size=`8192` sha256=`04f103061f80bdc0805c85b66c1679d9c441546fd1dbc54d4278939f6cdace88`
- `firmware-update/vbmeta_system.img`: size=`4096` sha256=`848c54c8e2a057c74952ae877afbd571854765acc84eb2e29351b2636236a52d`
- `system.new.dat.br`: size=`557497438` sha256=`bedf3bb03843f3c29b9ba810537fef3dd51a40a5e49fe4b4f7c3c5ee50267819`
- `vendor.new.dat.br`: size=`851100588` sha256=`39efc58c00d4ed6d6bb2f47e4090ecacadb62c79acb2766394520db57a8b5591`
- `product.new.dat.br`: size=`2559788280` sha256=`2481dd9d67ebbf47d37946fb66593f1f60cfa913c706b1e598827de7d8e5418b`
- `odm.new.dat.br`: size=`1259071` sha256=`e90337bfb715411fd1a2ff7abec8219dd63b52a57982c56458188ffbc6f151f7`
- `system_ext.new.dat.br`: size=`269330784` sha256=`5540488cf28ab92a4d3d7b38188b33801a8e3d3f2231311ab60a3b16059bac71`
- `mi_ext.new.dat.br`: size=`281151` sha256=`d7557205c79dbafd8b8fdd75063c698bdb0f470b297a5df7189b5535c5fffe99`

## boot.img Header Snapshot
- boot magic: `b'ANDROID!'`
- kernel_size (legacy offset): `54837264`
- ramdisk_size (legacy offset): `1330716`
- header_version_guess (legacy offset): `2`

## Integration Recommendations (Moderate)
1. Treat this package as baseline evidence only; do not directly import proprietary blobs into the repository.
2. Keep using extracted metadata + partition ops + hash evidence for reproducibility and regression tracking.
3. Compare boot/dtbo/vbmeta hashes against CI-generated artifacts to validate release-chain consistency.
4. Continue kernel-side integration via open-source references; use official ROM package as validation target, not code donor.

# Gap Report (SO-TS 4.19 Reference -> yefxx 6.11 Source)

## Defconfig

- SO-TS umi-like defconfigs: 6
- yefxx 6.11 umi-like defconfigs: 0
- SO-TS list: alioth_defconfig, apollo_defconfig, cmi_defconfig, lmi_defconfig, thyme_defconfig, umi_defconfig
- yefxx 6.11 list: (none)

## DTS/QCOM focus

- SO-TS qcom umi/sm8250/xiaomi related files: 200
- yefxx 6.11 qcom umi/sm8250/xiaomi related files: 34
- SO-TS sample: alioth-audio-overlay.dtsi, alioth-pinctrl.dtsi, alioth-sm8250-camera-board.dtsi, alioth-sm8250-camera-sensor-mtp.dtsi, alioth-sm8250-overlay.dts, alioth-sm8250.dtsi, apollo-audio-overlay.dtsi, apollo-pinctrl.dtsi, apollo-sm8250-camera-sensor-mtp.dtsi, apollo-sm8250-overlay.dts, apollo-sm8250.dtsi, bengal-rumi-overlay.dts, bengal-rumi.dts, bengal-rumi.dtsi, cas-sm8250-camera-sensor-mtp.dtsi, cas-sm8250-overlay.dts, cas-sm8250.dtsi, cmi-audio-overlay.dtsi, cmi-pinctrl.dtsi, cmi-sm8250-camera-sensor-mtp.dtsi
- yefxx 6.11 sample: msm8953-xiaomi-daisy.dts, msm8953-xiaomi-mido.dts, msm8953-xiaomi-tissot.dts, msm8953-xiaomi-vince.dts, msm8992-msft-lumia-octagon-talkman.dts, msm8992-xiaomi-libra.dts, msm8994-msft-lumia-octagon-cityman.dts, msm8994-msft-lumia-octagon.dtsi, msm8994-sony-xperia-kitakami-sumire.dts, msm8996-xiaomi-common.dtsi, msm8996-xiaomi-gemini.dts, msm8996pro-xiaomi-natrium.dts, msm8996pro-xiaomi-scorpio.dts, msm8998-xiaomi-sagit.dts, sdm660-xiaomi-lavender.dts, sdm845-sony-xperia-tama-apollo.dts, sdm845-xiaomi-beryllium-common.dtsi, sdm845-xiaomi-beryllium-ebbg.dts, sdm845-xiaomi-beryllium-tianma.dts, sdm845-xiaomi-polaris.dts

## Techpack

- SO-TS techpack entries: 14
- yefxx 6.11 techpack entries: 0
- SO-TS techpack dirs: .gitignore, Kbuild, Kconfig, audio, camera-bengal, camera-xiaomi-cas, camera-xiaomi-psyche, camera-xiaomi-tablet, camera-xiaomi, camera, data, display, stub, video
- yefxx 6.11 source has no top-level techpack (expected: mainline-style drivers split).

## Migration implication

- Need to create/port umi defconfig in the yefxx 6.11 source before feature migration.
- DTS migration should start from sm8250-xiaomi-* subset, not full tree copy.
- Techpack features require subsystem-by-subsystem adaptation into the yefxx 6.11 driver layout.

## Official ROM Alignment Note

This project is building the yefxx-based 6.11 kernel source baseline for `umi`, not reproducing Xiaomi's stock 4.19 kernel.

The official ROM should be treated as a reference extraction source and validation baseline for:
- `boot.img` size and packaging expectations
- `dtbo` / `vbmeta` / dynamic partition baseline
- boot-chain consistency checks
- runtime validation on official userspace

Therefore, the current gap against the official ROM should be understood as a compatibility and release-chain gap rather than a requirement to downgrade the target kernel version.

## Current Release-Chain Gap

- `boot.img` delivery is still incomplete in the latest Phase2 artifact
- ROM boot / `dtbo` / `vbmeta` consistency is not yet confirmed
- DTB target coverage remains incomplete
- runtime validation is still pending on device

---

## 分析总结

| 优先级 | 任务 | 依据 |
|--------|------|------|
| P0 | 完成驱动集成清单 | Phase2Decision.py:driver_integration_runtime_blockers |
| P1 | 改进DTB清单映射 | BuildDtbManifest.py 白名单优化 |
| P1 | 增强运行时验证 | BuildRuntimeValidationSummary.py |
| P2 | 增加自动化测试 | 边界条件覆盖 |
| P2 | 文档完善 | 与代码变更同步 |

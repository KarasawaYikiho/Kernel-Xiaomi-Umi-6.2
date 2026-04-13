# Gap Report (SO-TS 4.19 -> 5+ Base)

## Defconfig

- SO-TS umi-like defconfigs: 6
- 5+ base umi-like defconfigs: 0
- SO-TS list: alioth_defconfig, apollo_defconfig, cmi_defconfig, lmi_defconfig, thyme_defconfig, umi_defconfig
- 5+ list: (none)

## DTS/QCOM focus

- SO-TS qcom umi/sm8250/xiaomi related files: 200
- 5+ base qcom umi/sm8250/xiaomi related files: 34
- SO-TS sample: alioth-audio-overlay.dtsi, alioth-pinctrl.dtsi, alioth-sm8250-camera-board.dtsi, alioth-sm8250-camera-sensor-mtp.dtsi, alioth-sm8250-overlay.dts, alioth-sm8250.dtsi, apollo-audio-overlay.dtsi, apollo-pinctrl.dtsi, apollo-sm8250-camera-sensor-mtp.dtsi, apollo-sm8250-overlay.dts, apollo-sm8250.dtsi, bengal-rumi-overlay.dts, bengal-rumi.dts, bengal-rumi.dtsi, cas-sm8250-camera-sensor-mtp.dtsi, cas-sm8250-overlay.dts, cas-sm8250.dtsi, cmi-audio-overlay.dtsi, cmi-pinctrl.dtsi, cmi-sm8250-camera-sensor-mtp.dtsi
- 5+ sample: msm8953-xiaomi-daisy.dts, msm8953-xiaomi-mido.dts, msm8953-xiaomi-tissot.dts, msm8953-xiaomi-vince.dts, msm8992-msft-lumia-octagon-talkman.dts, msm8992-xiaomi-libra.dts, msm8994-msft-lumia-octagon-cityman.dts, msm8994-msft-lumia-octagon.dtsi, msm8994-sony-xperia-kitakami-sumire.dts, msm8996-xiaomi-common.dtsi, msm8996-xiaomi-gemini.dts, msm8996pro-xiaomi-natrium.dts, msm8996pro-xiaomi-scorpio.dts, msm8998-xiaomi-sagit.dts, sdm660-xiaomi-lavender.dts, sdm845-sony-xperia-tama-apollo.dts, sdm845-xiaomi-beryllium-common.dtsi, sdm845-xiaomi-beryllium-ebbg.dts, sdm845-xiaomi-beryllium-tianma.dts, sdm845-xiaomi-polaris.dts

## Techpack

- SO-TS techpack entries: 14
- 5+ base techpack entries: 0
- SO-TS techpack dirs: .gitignore, Kbuild, Kconfig, audio, camera-bengal, camera-xiaomi-cas, camera-xiaomi-psyche, camera-xiaomi-tablet, camera-xiaomi, camera, data, display, stub, video
- 5+ base has no top-level techpack (expected: mainline-style drivers split).

## Migration implication

- Need to create/port umi defconfig in 5+ base before feature migration.
- DTS migration should start from sm8250-xiaomi-* subset, not full tree copy.
- Techpack features require subsystem-by-subsystem adaptation into 5+ driver layout.

# W41 华北县年统计与遥感单产配对试点

## 已核对的数据

- [县级年鉴小麦原值](w41_county_wheat_statistics.csv)含山东泰安 6 个县级单位 2016–2021 年 36 条记录，以及北京房山 2018–2021 年 4 条记录。保留面积、总产、原表亩产、表号和来源。40 条均通过亩产单位交叉检验。年鉴栏名为小麦，冬、春季型和少数县域统计例外需要单独核实。
- [Lu 的公开数据](https://doi.org/10.17632/rbs52ww8v2.1)的实际 CSV 没有收获年列。有标识的 1,385 行均为江苏代码，另有 77 行没有标识。数据文件 SHA-256 为 `506f9bd11cafe16e9107591f23ff88810539aae2a00adb505ae2bfb51806554c`。未根据文件行序推断收获年。
- [Zheng 的华北产量与物候](https://doi.org/10.5281/zenodo.14785961)已下载。25 个县级名称的校准和验证工作表没有逐行年份，1984–2020 年汇总表没有县字段，两类表不能合成县年面板。产量和物候压缩包分别通过官方 MD5 `cbdaf83f7ed4df7e35564e99271ee5dc` 和 `12b04f2543fdf287fd63c12a0088821c` 校验。
- 河南 2021 年县级小麦面积、产量的两张表已经定位，当前仅记录条目，原值待取得；滑县公报同时提供小麦面积和夏粮产量，未用夏粮总产代替小麦总产。[面积表](https://www.tjnjdata.com/navipage-n3023021602000508.html) · [产量表](https://www.tjnjdata.com/navipage-n3023021602000509.html) · [滑县统计局公报](https://www.hnhx.gov.cn/portal/zwgk/tjgb/webinfo/2022/04/phone1650433594082604.htm)

## 可复跑的配对

在 `Data/external/ncp_yield_pairing/download/` 放入下列输入。使用 NumPy 和 Rasterio，从仓库根目录运行。完整栅格可按年份补齐，其他 4 个收获年当前仅录入统计侧。

| 文件 | 版本与校验 |
|---|---|
| `geoBoundaries-CHN-ADM3.geojson` | [geoBoundaries gbOpen CHN ADM3 固定快照](https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09/releaseData/gbOpen/CHN/ADM3/geoBoundaries-CHN-ADM3.geojson)，来源 OpenStreetMap，ODbL 1.0。SHA-256 `3cc71d6cd23e7dbb5646422b40dd92a7a74d8779f340eb9377158c961dec310e`。数据代表年份为 2017。用固定 shapeID 配对，尚未完成逐年行政区划变更核证。 |
| `2017ChinaWheatYield30m.tif` | [发布文件](https://zenodo.org/records/7360753/files/2017ChinaWheatYield30m.tif?download=1)，发布者完整文件 MD5 `712fc74438d8447cd2c1d0b51d6d5306`。 |
| `2021ChinaWheatYield30m.tif` | [发布文件](https://zenodo.org/records/7360753/files/2021ChinaWheatYield30m.tif?download=1)，发布者完整文件 MD5 `98c9ef3723874893177b4c67c7fdfcba`。 |

```bash
python src/s2_model_validation/w41_pair_county_yield.py 2017
python src/s2_model_validation/w41_pair_county_yield.py 2021
```

本轮在整图传输不稳定时，按 TIFF 索引取得覆盖目标县边界窗口的全部数据块，并逐段校验 HTTP 206、字节区间和长度。[窗口清单](../../Outputs/reports/w41_remote_windows.json)记录各段范围和本地 SHA-256。局部文件仅用于这些已核对的窗口。2021 年整图随后完整下载并通过官方 MD5 校验，整图和窗口输出的 SHA-256 一致。2017 年已核验范围为泰安试点窗口。统计单产按小麦总产除以播种面积，遥感单产按县域内正值、有效像元面积加权。用于诊断的面积比为正值遥感像元面积除以年鉴播种面积，允许超过 1，不能直接等同于冬小麦分类准确率。[遥感产品方法](https://doi.org/10.5194/essd-15-4047-2023)

## 试点结果与限制

- [2017 年配对表](../../Outputs/reports/w41_county_yield_pairing_2017.csv)含泰安 6 条，[2021 年配对表](../../Outputs/reports/w41_county_yield_pairing_2021.csv)含泰安 6 条及房山 1 条。输出保留统计与遥感单产、有效像元数、面积比和口径备注。本轮没有用这些记录训练模型。
- 房山 2021 年正值遥感像元 512 个，面积约 35.4 ha，年鉴播种面积 1,930.6 ha，面积约为统计面积的 1.8%。面积覆盖差提示其均值缺少代表性，须查产品掩膜和口径。
- 新泰的面积比为 2017 年 72.6%、2021 年 62.4%。2021 年泰安六个县级单位的面积比为 62.4%–348.0%。2021 年原表脚注经扫描图核对，说明未含高新区、泰山景区、徂汶景区。泰山区尤其需要核查统计范围与县级几何口径。正式纳入条件应固定后再做误差和模型比较，报告筛选如何改变样本地区与年份分布。
- 当前统计数据仅含泰安与房山，遥感实际配对仅涉及 2017、2021 年。冀、豫资料仍待取得，2020 年前后的行政区划变化仍待核对。以上结果仅用于评估配对可行性。

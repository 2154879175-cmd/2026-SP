# W43 冀鲁县级遥感单产配对

2017–2021 年共得到 94 条统计—遥感试配对。河北石家庄 60 条、山东泰安 30 条、北京房山 4 条。每个收获年所有配对县均有有效正值像元。有效像元数与代表性的判断分别留存，后者按 W42 约定另行审核。行政边界与 W41 使用同一版本。

2021 年使用已通过官方 MD5 的完整产品。2017–2020 年读取覆盖全部候选县边界的 TIFF 数据块，逐一核验 HTTP 206、精确范围和内容 SHA-256。窗口文件仅可用于记录的县域。已重新计算 2017、2021 年的 W41 样本，重叠行逐字段一致。[遥感产品及整图校验](https://zenodo.org/records/7360753) · [边界资料](../../Data/external/w41_county_yield_pairing.md)

从仓库根目录对每个收获年运行以下命令。2021 年可省略取窗口步骤，并用完整图路径替换 `--raster` 参数。

```bash
python src/s2_model_validation/w43_fetch_yield_windows.py 2020
python src/s2_model_validation/w41_pair_county_yield.py 2020 --additional-stats Data/external/w42_sjz_winter_wheat.csv --raster Data/external/ncp_yield_pairing/download/w43_2020_counties.sparse.tif --output Outputs/reports/w43_county_yield_pairing_2020.csv
```

配对表以原报作物栏名、县和收获年保存两套单产，并记录统计播种面积、遥感正值像元面积、两者比值及口径备注。面积较小或边界差异较大的县仍在配对表保留。这个表用于覆盖筛查和配对验证，未作为华北总体样本直接解释。

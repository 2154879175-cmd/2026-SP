# W40 华北数据补充

从作者公开记录下载下表文件，均按官方大小和 MD5 通过校验。本地相对位置从仓库根目录算起。

| 本地文件 | 字节数 | 官方 MD5 | 来源 |
|---|---:|---|---|
| `Data/external/china_yield_centurial/download/China_yield_centurial_v1.xlsx` | 5,125,821 | `f709ad47259dec09e1a0ebdca41cec46` | [Figshare v1](https://doi.org/10.6084/m9.figshare.30819320.v1) · [下载](https://ndownloader.figshare.com/files/63199477) |
| `Data/external/wheatmap_ncp/download/Winter wheat planting area.xlsx` | 60,496 | `a5c95817fb36f07b7bd61ea8f5e4fe06` | [WheatMapNCP v2](https://doi.org/10.6084/m9.figshare.28890956.v2) · [下载](https://ndownloader.figshare.com/files/57281096) |
| `Data/external/wheatmap_ncp/download/WheatMapNCP_2020.tif` | 105,956,638 | `f86405fe936b89cab26d609af6f31d27` | [WheatMapNCP v2](https://doi.org/10.6084/m9.figshare.28890956.v2) · [下载](https://ndownloader.figshare.com/files/57293717) |

两个数据发布记录的许可均为 CC BY 4.0。田间工作簿包含试验处理平均谷粒干重 `GrainYield_mean`（kg/ha）。WheatMapNCP 包含冬小麦种植分布和面积；面积工作簿含市级与省级表。2020 年样例为 EPSG:4326、单波段、63,888 × 50,402 像元，试读窗口读到 0 和 1，文件未声明 NoData。正式掩膜处理需结合研究区边界核对覆盖，避免把覆盖区外解释为未种植。其余 2000–2024 年栅格可按配对实验需要补齐。引用请同时保留 [田间数据论文](https://doi.org/10.1038/s41597-026-07545-0) 与 [WheatMapNCP 论文](https://doi.org/10.1038/s41597-026-07216-0)。

用 Python 3.11+ 和 openpyxl 在仓库根目录复跑初筛：

```bash
python src/s2_model_validation/w40_field_trial_screen.py
```

[初筛台账](../../Outputs/reports/w40_field_trial_screen.csv)记录 2016–2021 年内、WheatMapNCP 论文外包框（105–123°E、29–42°N）中有经纬度与正值谷粒产量的记录。外包框用于发现候选记录，精确研究域须以研究区与县界叠加来确定。432 条 Wheat 与 394 条 Maize 分别是试验处理记录，两者尚待核实季型与地理定位精度，独立样本规模需用研究、站点和年份判断。工作簿及原始样例栅格保存在本地，仓库记录下载地址、校验值和聚合台账。

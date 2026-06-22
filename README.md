# 森林野外数据采集小车

**Forest Field Data Rover**

面向森林样地环境数据采集与火险监测场景的轮腿式移动平台概念设计。项目包含 SolidWorks 结构建模、多视图输出，以及面向代表性轮腿下连杆的局部有限元静力分析。

## 局部有限元静力分析

本上传包中的有限元部分为真实的数值有限元求解，不是解析公式代替。求解对象是轮腿机构中的代表性下连杆，而非整车装配体。

| 项目 | 设置 |
| --- | --- |
| 分析对象 | 180 × 25 × 8 mm 代表性下连杆 |
| 单元类型 | CSTRI3 二维平面应力三角形单元 |
| 候选材料输入 | 6061 系铝合金，E = 69 GPa，ν = 0.33 |
| 边界条件 | 车体侧安装端的面内自由度固定 |
| 载荷工况 | 轮侧端面总计 150 N 向下分布力 |
| 网格规模 | 840 个单元，473 个节点，946 个自由度 |
| 最大 von Mises 应力 | 30.87 MPa |
| 最大总位移 | 0.390 mm |

![有限元网格与边界条件](fea_mesh_boundary_conditions.png)
![有限元 von Mises 应力云图](fea_von_mises_stress.png)
![有限元总位移云图](fea_total_deformation.png)

### 结果边界

- 6061 系铝合金是仿真候选材料输入，不代表项目已完成真实制造材料或设备品牌选型。
- 该模型不包含销轴接触、关节间隙、螺栓预紧、轮胎柔顺性、车体柔度和真实地形时程。
- 结果适用于局部连杆在设定载荷下的结构趋势和初步校核，不能替代整车工程定型验证。

## 主要文件

- `index.html` 与 `site.css`：GitHub Pages 静态展示网页。
- `fea_mesh_boundary_conditions.png`、`fea_von_mises_stress.png`、`fea_total_deformation.png`：有限元结果图。
- `fea_results.json` 与 `FEA_README.md`：有限元数据和方法说明。
- `run_link_plane_stress_fea.py`：可复现本地有限元求解与云图生成的脚本。
- `forest_lfmc_fire_rover_final.SLDPRT`：最终展示模型。

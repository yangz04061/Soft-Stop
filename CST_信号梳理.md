# CST 信号梳理

基于 Word 原文 `SGMW_VMC Comfortable Stop_舒适制动功能规范_master.docx` 和现有规格整理。以下优先采用 Word 中出现的真实接口名；如果 Markdown 中有概念名但 Word 已细化为真实接口，下面以 Word 为准。

## 1. 软件架构拆分

VMC 内部建议按 6 个软件职责拆分：

1. 状态机与开关记忆管理：维护 `Off / Standby / Active / Failure`，对接 HMI 和 Host ECU 记忆。
2. 激活退出判定：汇总车速、踏板、档位、稳定性、ADAS、故障、能力限制等条件。
3. 舒适制动控制器：基于减速度、俯仰角、俯仰角速度形成电制动和悬架目标。
4. 握手平顺管理：负责与机械制动、VCU 扭矩接管、站停阶段 speed control 的平滑切换。
5. 执行器目标分发：向 VCU、制动执行器、SUCU 下发目标。
6. 能力与有效性监控：监控有效位、驱动能力、执行器握手和故障降级。

## 2. 关键别名关系

| Markdown / 概念名 | Word 中真实信号名 | 说明 |
| --- | --- | --- |
| VMCSoftStopFlg | VMCSoftStopSts | CST 状态反馈信号 |
| CSTSwRqst | CSTFctSwtSts | HMI 开关请求 |
| AirSuspTarHei_FL/FR/RL/RR | AirSpringHeiReq_FL/FR/RL/RR | 空簧高度请求 |
| TarStfnLvlFrntLe/FrntRi/ReLe/ReRi | TarStfnReqFrntLe/FrntRi/ReLe/ReRi | 空簧刚度等级请求 |
| CdcCurrentReq_xx | CdcCurrentMaxRqst_xx / CdcCurrentMinRqst_xx | CDC 请求被拆成 max / min 两路 |
| TarDrvModeFrntLe/FrntRi/ReLe/ReRi | VMCMtCtrlModeFL_1st / FR_2nd / RL_3rd / RR_4th | 四电机控制模式请求 |

## 3. HMI / 状态记忆接口

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| HMI -> VMC | CSTFctSwtSts | CST 功能开关请求。Word 中定义：`0=NoRequest`，`1=On`，`2=Off`。 |
| VMC -> HMI | VMCSoftStopSts | CST 当前状态反馈，`0=Off`，`1=Standby`，`2=Active`，`3=Failure`。 |
| VMC -> Host ECU | VMCSoftStopSts | 下电前记忆状态写入 Host ECU / NVRAM。 |
| Host ECU -> VMC | memory restore request | 上电后恢复上次记忆状态。Word 描述了动作，但未给出独立真实信号名。 |

## 4. 激活 / 退出判定输入信号

### 4.1 车辆状态与驾驶员输入

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| Vehicle -> VMC | VehSpdAvgDrvn_ABS | 车速，用于工作区间判定和站停控制。 |
| Brake -> VMC | BrakPedalDisp | 制动踏板位置，用于激活门限、松踏板退出。 |
| Brake -> VMC | brake pedal rate (derived) | Word 未给真实报文名，允许由踏板位置求导，用于紧急制动退出。 |
| Vehicle -> VMC | AccActPos_FD | 油门踏板位置。 |
| Vehicle -> VMC | AccActPosV_FD | 油门踏板位置有效位。 |
| Vehicle -> VMC | VehActGrStsESC_FD | 当前档位状态，用于判定车辆是否前进。 |

### 4.2 车辆动态与控制观测量

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| Vehicle -> VMC | ADASLongAcc | 纵向加速度，用于减速度工作区间判定和前馈控制。 |
| Vehicle -> VMC | ADASLongAccV | 纵向加速度有效位。 |
| Vehicle -> VMC | ADASLatAccel | 横向加速度，用于横向工况门限。 |
| Vehicle -> VMC | ADASLatAccelV | 横向加速度有效位。 |
| Vehicle -> VMC | ADASIMUPitch | 俯仰角 / 俯仰相关量。Word 描述文本为“俯仰角速度”，需结合信号定义再确认量纲。 |
| Vehicle -> VMC | ADASPitchRateV | 俯仰角速度有效位。 |
| Vehicle -> VMC | slope / grade | 规范要求存在坡度退出条件，但 Word 提取内容中未给出真实信号名。 |
| Vehicle -> VMC | standstill confirm | 规范要求车辆静止确认，但 Word 提取内容中未给出真实信号名。 |

### 4.3 仲裁与故障输入

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| ESC -> VMC | ABSAtv_FD | ABS 激活状态，激活后 CST 退出。 |
| ESC -> VMC | TCSysAtv_FD | TCS 激活状态，激活后 CST 退出。 |
| ADAS -> VMC | VCUADASactvSts | ADAS 激活状态，Word 建议可拆成行车辅助 / 泊车辅助 / AEB-AES。 |
| Drive -> VMC | DrvActrStsFb | 驱动系统降级 / 不可用。 |
| Vehicle -> VMC | critical valid bits | 车速、轮速、踏板、俯仰等有效位集合。部分已给出真实信号名，部分仍只给概念。 |

## 5. 制动执行器接口

### 5.1 VMC -> 制动执行器

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| VMC -> Brake | DecelBrkTrqAtvRqstFlg | 减速制动扭矩请求使能，Word 定义 `0=NoRequest`，`1=Request`。 |
| VMC -> Brake | VehTargtDecelBrkTorq | 整车目标减速制动力矩。激活时将机械制动请求 ramp down 到 0；退出前恢复驾驶员原始请求。 |

### 5.2 制动执行器 -> VMC

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| Brake -> VMC | DecelBrkActrRqstSts | 制动执行器减速请求状态反馈，用于握手。Word 定义：`0=Not_Controllable`，`1=Ready_for_Control`，`2=Controlled`，`3=Override`，`4=Error`。 |
| Brake -> VMC | DrRqdFrntShftBrkTorq | 驾驶员前轴请求制动力矩，含液压制动 + regen 部分。 |
| Brake -> VMC | DrRqdRearShftBrkTorq | 驾驶员后轴请求制动力矩，含液压制动 + regen 部分。 |

## 6. 驱动系统接口

### 6.1 VCU -> VMC 能力与反馈

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| VCU -> VMC | PrDrvMtrTorqMinLitVal_FD | 2 电机车型前轴 / 4 电机车型左前的电制动最小能力值。 |
| VCU -> VMC | MCU2MtrTorqMinLitVal_FD | 2 电机车型后轴 / 4 电机车型右前的电制动最小能力值。 |
| VCU -> VMC | MCU3MtrTorqMinLitVal_FD | 4 电机车型左后电制动最小能力值。 |
| VCU -> VMC | MCU4MtrTorqMinLitVal_FD | 4 电机车型右后电制动最小能力值。 |
| VCU -> VMC | TMTorqRqst_FD | VCU 实际需求扭矩反馈，2 电机前轴 / 4 电机左前。 |
| VCU -> VMC | MCU2TorqRqst_FD | VCU 实际需求扭矩反馈，2 电机后轴 / 4 电机右前。 |
| VCU -> VMC | MCU3TorqRqst_FD | VCU 实际需求扭矩反馈，4 电机左后。 |
| VCU -> VMC | MCU4TorqRqst_FD | VCU 实际需求扭矩反馈，4 电机右后。 |
| VCU -> VMC | PrDrvShftDrRqstdTorqDff_FD | 双电机前电机驾驶员请求电制动扭矩（BrkReg + Coasting）。 |
| VCU -> VMC | ThScdDrvShftDrRqstdTorqDffHCU_FD | 双电机后电机驾驶员请求电制动扭矩。 |
| VCU -> VMC | FrntLeMotDrRqstdTorq | 四电机左前驾驶员请求电制动扭矩。 |
| VCU -> VMC | FrntRiMotDrRqstdTorq | 四电机右前驾驶员请求电制动扭矩。 |
| VCU -> VMC | ReLeMotDrRqstdTorq | 四电机左后驾驶员请求电制动扭矩。 |
| VCU -> VMC | ReRiMotDrRqstdTorq | 四电机右后驾驶员请求电制动扭矩。 |

### 6.2 VMC -> VCU 双电机接口

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| VMC -> VCU | FrntAxleTarDrvModeRqst | 前轴控制模式请求。 |
| VMC -> VCU | ReAxleTarDrvModeRqst | 后轴控制模式请求。 |
| VMC -> VCU | VMCTarDrvTqFrnt | 前轴目标扭矩（驱动 / 电制动）主减前。 |
| VMC -> VCU | VMCTarDrvTqRe | 后轴目标扭矩（驱动 / 电制动）主减前。 |
| VMC -> VCU | VMCTarSpdFrnt | 前轴目标转速主减前，用于站停 speed control。 |
| VMC -> VCU | VMCTarSpdRe | 后轴目标转速主减前，用于站停 speed control。 |

`FrntAxleTarDrvModeRqst` / `ReAxleTarDrvModeRqst` 状态定义：`0=NoRequest`，`1=Speed Control`，`2=Drive Torque Control`，`3=Regen Torque Control`。

### 6.3 VMC -> VCU 四电机接口

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| VMC -> VCU | VMCMtCtrlModeFL_1st | 第一驱动电机控制模式请求。 |
| VMC -> VCU | VMCMtCtrlModeFR_2nd | 第二驱动电机控制模式请求。 |
| VMC -> VCU | VMCMtCtrlModeRL_3rd | 第三驱动电机控制模式请求。 |
| VMC -> VCU | VMCMtCtrlModeRR_4th | 第四驱动电机控制模式请求。 |
| VMC -> VCU | VMCTarDrvTqFL_1st | 左前目标扭矩（驱动 / 电制动）主减前。 |
| VMC -> VCU | VMCTarDrvTqFR_2nd | 右前目标扭矩（驱动 / 电制动）主减前。 |
| VMC -> VCU | VMCTarDrvTqRL_3rd | 左后目标扭矩（驱动 / 电制动）主减前。 |
| VMC -> VCU | VMCTarDrvTqRR_4th | 右后目标扭矩（驱动 / 电制动）主减前。 |
| VMC -> VCU | VMCTarSpdFL_1st | 左前目标转速主减前。 |
| VMC -> VCU | VMCTarSpdFR_2nd | 右前目标转速主减前。 |
| VMC -> VCU | VMCTarSpdRL_3rd | 左后目标转速主减前。 |
| VMC -> VCU | VMCTarSpdRR_4th | 右后目标转速主减前。 |

四电机控制模式与双电机一致：`0=NoRequest`，`1=Speed Control`，`2=Drive Torque Control`，`3=Regen Torque Control`。

## 7. 悬架系统接口

### 7.1 CDC 接口

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| VMC -> SUCU | CdcActvRqst | CDC 激活请求。 |
| VMC -> SUCU | CdcCurrentMaxRqst_xx | CDC 目标最大电流百分比，请求量。 |
| VMC -> SUCU | CdcCurrentMinRqst_xx | CDC 目标最小电流百分比，请求量。 |
| SUCU -> VMC | CdcActrStsFb | CDC 减震器状态反馈，握手成功时 `0x01=Controlled`。 |
| SUCU -> VMC | SUCUVlvActuCrntFL / FR / RL / RR | 四轮电磁阀实际电流百分比。 |
| SUCU -> VMC | CdcBaseCurrent_FL / FR / RL / RR | 四轮 CDC 基础电流百分比。 |

### 7.2 空气弹簧接口

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| VMC -> SUCU | AirSuspActvRqst | 空簧执行请求。 |
| VMC -> SUCU | AirSpringHeiReq_FL / FR / RL / RR | 四轮空簧高度控制请求。 |
| VMC -> SUCU | TarStfnReqFrntLe / FrntRi / ReLe / ReRi | 四轮空簧刚度等级请求。 |
| SUCU -> VMC | AirSpringActrStsFb | 空气弹簧执行器状态反馈。 |

### 7.3 主动悬架接口

| 方向 | 信号 | 作用 |
| --- | --- | --- |
| VMC -> SUCU | ActvSuspActvRqst | 主动悬架激活请求，Word 定义 `0x2 = Mode Damper Force`。 |
| VMC -> SUCU | ActvSuspTarForce_FL / FR / RL / RR | 四轮目标主动阻尼力。 |
| SUCU -> VMC | ActSuspActrSts | 主动悬架执行器状态；`0x2 = Mode Damper Force` 表示握手成功。 |
| SUCU -> VMC | ActSuspCtrlOrigTargtDampForce_FL / FR / RL / RR | 四轮减震器目标主动力。 |
| SUCU -> VMC | ActSuspActulDampForce_FL / FR / RL / RR | 四轮减振器实际减振力。 |

## 8. 仍需接口进一步澄清的项目

以下需求在 Word 中描述了物理含义，但当前提取内容没有给出唯一真实报文名，做软件设计时应在 CAN / RTE 接口定义里补齐：

1. 坡度信号。
2. 站停确认信号。
3. 制动踏板速率真实接口名。
4. 制动压力 / 主缸压力真实接口名。
5. 轮速有效位 / 俯仰角真实量纲与命名。
6. Host ECU 恢复记忆状态的真实信号名。

## 9. 建议的 drawio 图层表达

建议画 3 层：

1. 外部 ECU / 执行器层：HMI / Host、Brake、VCU、SUCU、ADAS / ESC。
2. VMC CST 软件层：状态机、仲裁、控制器、握手管理、目标分发、监控。
3. 接口层：每条边只写真实信号名，不再用泛化描述。
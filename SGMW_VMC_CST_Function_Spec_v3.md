# SGMW VMC 舒适制动（Comfortable Stop）功能规范

## 1. 功能描述

舒适制动（Comfortable Stop简称CST）功能是一个可选的舒适性功能，该功能致力于解决车辆前进行驶非紧急制动工况车辆刹停前出现的减速度波动，降低车辆制动俯仰，使用制动（只考虑电制动可选）和悬架控制（阻尼、刚度和高度）实现舒适制动的效果。

CST功能仅在汽车非紧急情况减速停车时激活，为驾驶员提供平稳的感觉。

1. 当车速低于一个门限值且制动压力大于某一门限值，CST功能激活（"CST_Status"=Active），此时减速行为通过制动（只使用电制动）控制，VMC CST功能负责保证激活时的平顺性。

2. 为了保证电制动能够平顺刹停车辆，在CST的最后阶段，舒适制动会通过转速接口来保证车辆静止。当车辆确认静止后（standstill状态确认），CST功能需要退出（"CST_Status"=Standby），制动系统介入保证车辆维持在当前位置，制动系统需要保证握手时的平顺性。

3. 当出现驾驶员紧急制动的情况，CST功能需要退出（"CST_Status"=Standby），制动系统介入保证满足驾驶员的制动请求，制动系统需要保证握手时的平顺性。

4. 当驾驶员释放制动踏板时（或者主缸压力小于xxbar），CST功能需要退出（"CST_Status"=Standby）。

5. 当检测到车辆驶到坡道（坡度>=15% TBD），CST功能需要退出（"CST_Status"=Standby），制动系统介入保证满足驾驶员的制动请求，制动系统需要保证握手时的平顺性。

6. 当整车稳定控制功能激活时：
   - 制动：ABS, EBD, TCS, YSC, DTC等稳定控制功能激活
   - VMC：TankTurn, CompasTurn, TBH等纵向功能功能激活
   
   CST功能需要退出（"CST_Status"=Standby），制动系统介入，制动系统需要保证握手时的平顺性。

7. 当智驾系统功能（AEB/APA/ACC）激活时，CST功能需要退出（"CST_Status"=Standby），制动系统介入响应智驾的请求，制动系统需要保证握手时的平顺性。

8. 如果驾驶员手动按压开关，HMI会基于VMC发送的状态（VMCSoftStopFlg：0x0:Off 0x1:Standby 0x2:Active 0x3:Failure）判定驾驶员激活还是关闭CST功能。
   - 当VMCSoftStopFlg=0x0:Off时，驾驶员按压开关，HMI发送CSTSwRqst=0x1:激活
   - 当VMCSoftStopFlg!=0x0:Off时，驾驶员按压开关，HMI发送CSTSwRqst=0x1:关闭

9. 正常下电后，CST开关状态需要保持记忆，VMC需要将下电前的CST状态（VMCSoftStopFlg）通过RTE发给Host ECU。Host ECU(联电)需要将这个开关状态信号通过NVRAM存储。再次上电时，需要发送记忆状态给VMC，VMC会更新记忆的状态（VMCSoftStopFlg）然后发给HMI。HMI需要基于CST反馈的状态，显示当前HMI上CST功能的开关状态。

## 2. 系统架构

### 2.1 功能架构

#### 2.1.1 与子系统自身控制功能边界区分

VMC的CST功能主要通过制动（仅电制动可选）和悬架的控制。

**VCU（电制动可选）**：
- VMC请求电制动扭矩发给VCU，如果VCU收到了来自制动系统的更高优先级功能的请求（例如一些稳定性功能DTC等），Override VMC，VCU优先执行制动高优先级请求，VMC的CST功能也会退出
- CST功能激活的最后时刻，VMC会将电制动请求缓慢降为0，然后把控制模式由扭矩模式转为转速模式，转速模式下会发送目标转速（目标转速=0）给前后电机。从而需要电机保证此时车辆静止
- 当VMC CST功能出于某些原因在车辆正常静止前退出（"CST_Status"=Standby/Off/Failure）,VCU应该保证接手驱动部分的控制，保证平滑过渡到VCU请求的扭矩值
- 当VMC激活时，VMC CST功能会基于VCU的coasting请求，ramp到目标请求，保证平顺性。谁握手谁来保证控制平顺性的原则

**制动执行器（不控制液压制动，但是需要从制动执行器获取相关信号保证激活时平顺握手控制）**：
- VMC CST激活后，制动执行器需要将制动请求（10kph只有液压制动）降为0，VMC CST功能需要基于制动执行器退出时残余制动扭矩，来增加CST的电制动请求值，保证车辆不出现闯动
- 当VMC CST功能出于某些原因退出（"CST_Status"=Standby/Off/Failure）, VMC CST功能需要将制动请求（只有电制动）降为某个目标值（8kph以上=coasting torque，8kph以下=0），制动执行器需要基于VMC退出时的电制动扭矩，调整制动功能的请求值，保证车辆不出现闯动。制动系统需要保证握手时的平顺性。谁握手谁来保证控制平顺性的原则

**主动悬架**：
- VMC控四轮侧主动悬架的阻尼、刚度。配合制动（电制动）控制，减少制动俯仰的影响。CST功能激活期间，VMC拥有控制最高优先级

**CDC**：
- VMC控四轮侧CDC的阻尼、刚度。配合制动（电制动）控制（min/max电流控制），减少制动俯仰的影响。CST功能激活期间，VMC拥有控制最高优先级

**空气弹簧**：
- VMC控制空簧的刚度和高度。配合制动（电制动）控制，减少制动俯仰的影响。CST功能激活期间，VMC拥有控制最高优先级

## 3. 执行器需求

该功能需要控制后转、制动执行器等。需要至少有一个执行器可用。

| 序号 | 系统 | 零部件名称 | 配置需求 | 需求概述 |
|------|------|------------|----------|----------|
| 1 | 转向 | RWS后轮转向执行器 | - | CST不控制后转 |
| 2 | 转向 | SBW线控转向/EPS非线控转向 | - | CST不控制前转 |
| 3 | 悬架 | CDC连续可变阻尼减振器 | 可选 | 阻尼调节（目标电流min/max）优化pitch control，握手后VMC进行独占控制 |
| 4 | 悬架 | 空气弹簧 | 可选 | 空簧刚度调节优化pitch control，握手后VMC进行独占控制 |
| 5 | 悬架 | 主动悬架 | 可选 | 主动施加damping force优化pitch control |
| 6 | 驱动 | 轴间四驱 | 可选 | VMC分别控制前后轴电制动扭矩 |
| 7 | 驱动 | 分布式四驱 | 可选 | VMC分别控制前后左右四电机电制动扭矩 |
| 8 | 制动 | EHBi 集成式电机液压制动 | - | CST不控制液压制动 |
| 9 | 制动 | EMB 机械电子制动 | - | CST不控制液压制动 |

## 4. 功能逻辑策略

### 4.1 功能逻辑策略概览

CST功能逻辑：仅通过制动（仅电制动）实现平稳减速的目标，同时悬架执行器也需要动态调整悬架刚度，进一步优化Pitch Control。

### 4.1.1 功能激活和退出策略

CST功能具有以下状态：Off、Standby、Active、Failure

**条件1：同时满足下面所有条件，CST Standby 切换到 Active**
- CST开关开启 switch on
- 无故障降级信号有效（车速，轮速，踏板信号等有效）
- 整车稳定控制功能未激活（ABS, TCS, YSC等稳定控制功能未激活）
- 坦克/圆规/TBH爆胎稳定功能未激活
- 电机Regen torque不受限（高SOC/低温/电机限扭）
- ADAS功能未激活
- 制动踏板高于阈值
- 制动踏板速率小于阈值（非紧急制动）
- 车速在工作区间（TBD < 车速 < TBD）
- 减速度在工作区间
- 坡度小于阈值
- 车辆处于前进状态
- 侧向加速度小于阈值
- 转向角小于阈值

**条件2：满足下面任意条件，CST Active 切换到 Standby**
- 整车稳定控制功能激活（紧急制动工况，ABS, TCS, YSC等稳定控制功能激活）
- 坦克/圆规/蟹行/TBH爆胎稳定功能激活
- 驾驶员制动踏板位置低于阈值（驾驶员松开制动踏板）
- 电机Regen torque受限（高SOC/低温/电机限扭）
- 速度不在工作区间（高于TBD，低于TBD）
- 驾驶员制动踏板速率过大（紧急制动）
- ADAS功能激活

**条件3：满足下面任意条件，CST Active 切换到 Off**
- 开关关闭
- 开关信号无效

**条件4：满足下面条件，CST Off 切换到 Standby**
- 场景A - CST处于未打开状态：车辆处于ready状态 且 制动、动力&VMC系统无任何故障 且 驾驶员手动按下开关（虚拟）打开CST功能
- 场景B - CST处于记忆状态（上一次打开后未通过开关关闭）：车辆处于ready状态 且 制动、动力&VMC系统无任何故障

**条件5：满足下面任意条件，CST Standby 切换到 Off**
- 开关关闭

**条件6：满足下面任意条件，CST Standby 切换到 Failure**
- 故障降级（包括电制动能力故障）
- 关键信号无效

**条件7：同时满足下面所有条件，CST Failure 切换到 Standby**
- 故障恢复
- 关键信号恢复
- 开关保持开启

**条件8：满足下面任意条件，CST Active 切换到 Failure**
- 故障降级（包括电制动能力故障）
- 关键信号无效

### 4.2 控制逻辑

**核心控制算法**：通过前馈控制（基于减速度，俯仰角及俯仰角导数等）和反馈控制（控制目标为俯仰角）调节前后轴的制动（电制动）扭矩来减小俯仰角，从而达到舒适制动的效果。悬架也会将俯仰作为控制目标，通过调整悬架刚度来进一步优化车辆点头。

**驾驶模式选择**：不区分驾驶模式

**执行器使用策略**：CST控制功能工作时会使用所有以下范围内可用执行器：包括驱动系统执行器（电制动控制regen torque control）

---

### 4.2.1 驱动系统执行器（电制动控制）

**轴间四驱车型**：CST功能请求前后轴的电制动扭矩给VCU。

**前后电机请求的控制模式**：

| 信号 | 0x0 | 0x1 | 0x2 | 0x3 |
|------|-----|-----|-----|-----|
| FrntAxleTarDrvModeRqst | No Request | Speed Control | Drive Torque Control | Regen Torque Control |
| ReAxleTarDrvModeRqst | No Request | Speed Control | Drive Torque Control | Regen Torque Control |

**前后轴电机电制动请求扭矩**：
- VMCTarDrvTqFrnt：当FrntAxleTarDrvModeRqst=0x03（Regen Torque Control）时，VMCTarDrvTqFrnt请求的值只会是前轴主减前的电制动regen请求，VCU无需根据请求扭矩值的符号来做任何判定。VCU需要保证电机处于电制动请求状态（轮速和扭矩方向相反）
- 对于EV轴间四驱车型：前轴主减前的目标电制动扭矩和电机端的目标电制动扭矩是一致的
- 对于PHEV车型，前轴主减前的目标电制动扭矩对应Z3的扭矩，VCU需要考虑Z2/Z1的传动比保证电机端的目标电制动扭矩

- VMCTarDrvTqRe：当ReAxleTarDrvModeRqst=0x03（Regen Control）时，VMCTarDrvTqRe请求的值只会是后轴主减前的电制动regen请求，VCU无需根据请求扭矩值的符号来做任何判定。VCU需要保证电机处于电制动请求状态（轮速和扭矩方向相反）
- 对于所有轴间四驱车型，后轴主减前的目标电制动扭矩和电机端的目标电制动扭矩是一致的

**前后轴电机速度请求**：
- VMCTarSpdFrnt：当FrntAxleTarDrvModeRqst=0x01（Speed Control）时，VMCTarSpdFrnt请求前轴主减前的目标速度
  - 对于EV轴间四驱车型：前轴主减前的目标速度和电机端速度应是一致的
  - 对于PHEV车型，前轴主减前的目标速度对应Z3的速度，VCU需要考虑Z2/Z1的传动比保证电机端的目标速度
- VMCTarSpdRe：当ReAxleTarDrvModeRqst=0x01（Speed Control）时，VMCTarSpdRe请求后轴主减前的目标速度
  - 对于所有轴间四驱车型，后轴主减前的目标速度和电机端的速度是一致的

**分布式四驱**：CST功能请求四个电机侧的主减前的电制动扭矩给VCU。

**四电机的电机请求的控制模式**：
- TarDrvModeFrntLe（左前电机控制模式）
- TarDrvModeFrntRi（右前电机控制模式）
- TarDrvModeReLe（左后电机控制模式）
- TarDrvModeReRi（右后电机控制模式）

控制模式定义：0x0 No Request, 0x1 Speed Control, 0x2 Drive Torque Control, 0x3 Regen Torque Control

**四电机的电制动请求扭矩**：
- VMCTarDrvTqFL_1st/VMCTarDrvTqFR_2nd/VMCTarDrvTqRL_3rd/VMCTarDrvTqRR_4th
- 当TarDrvModeFrntLe/FrntRi/ReLe/ReRi=0x03（Regen Torque Control）时，请求的值只会是四个电机主减前的电制动regen请求，VCU无需根据请求扭矩值的符号来做任何判定。VCU需要保证电机处于电制动请求状态（轮速和扭矩方向相反）
- 对于所有四电机车型：主减前的目标电制动扭矩和电机端的目标电制动扭矩是一致的

**前后轴电机速度请求**：
- VMCTarSpdFL_1st/VMCTarSpdFR_2nd/VMCTarSpdRL_3rd/VMCTarSpdRR_4th
- 当TarDrvModeFrntLe/FrntRi/ReLe/ReRi=0x01（SpeedControl）时，请求的是主减前的目标速度
- 对于所有四电机车型：主减前的目标速度和电机端速度是一致的

**从VCU接收的信号**：以下信号用来表征电机电制动能力的大小
- PrDrvMtrTorqMinLitVal_FD：双电机前轴主减前的电制动能力
- MCU2MtrTorqMinLitVal_FD：四电机左前主减前的电制动能力
- MCU3MtrTorqMinLitVal_FD：四电机右前主减前的电制动能力
- MCU4MtrTorqMinLitVal_FD：四电机左后主减前的电制动能力
- 双电机后轴及四电机右后主减前的电制动能力

---

### 4.2.2 后轮转向

**边界定义**：CST功能不使用后转执行器

---

### 4.2.3 前轮转向

**边界定义**：CST功能不使用前转执行器

---

### 4.2.4 悬架系统（CDC、空簧）

**边界定义**：VMC CST功能的垂向/载荷调整功能控制CDC的目标电流（min/max），以及空气弹簧的目标刚度等级。

**连续可调阻尼减振器（CDC）控制**：
- VMC CST功能激活时，通过0x0C0报文发送CDC控制目标请求给SUCU悬架控制器
- CDC激活请求 CdcActvRqst = 0x1（Request请求）
- CDC电流百分比 CdcCurrentReq_xx
- SUCU反馈：CDC减震器状态CdcActrStsFb = 0x1（Controlled）、SUCU电磁阀实际电流百分比SUCUVlvTrgtCrnt_XX、CDC基础电流百分比CdcBaseCurrent_xx
- VMC CST功能控制频率10ms左右

**空气弹簧控制**：
- 空簧有两种请求模式：高度请求和刚度请求
- 高度控制：AirSuspTarHei_FL/FR/RL/RR
- 刚度控制：TarStfnLvlFrntLe/FrntRi/ReLe/ReRi
- 空簧请求AirSuspActvRqst = 0x1 Request

---

### 4.2.5 主动悬架

**边界定义**：VMC CST功能的垂向/载荷调整功能控制主动悬架的主动阻尼力。

**控制策略**：
- VMC CST功能激活时，根据Pitch Angle调整需求计算主动悬架的主动阻尼力，通过0x0C0报文发送控制目标请求给SUCU悬架控制器
- 主动悬架激活请求 ActvSuspActvRqst = 0x2 = Mode Damper Force
- 主动悬架目标阻尼力 ActvSuspTarForce_FL/FR/RL/RR
- 主动悬架执行器状态 ActSuspActrSts = 0x2 = Mode Damper Force 代表握手成功，执行VMC的目标阻尼力，此时由VMC独占进行阻尼力控制
- VMC CST功能控制频率10ms左右

**反馈信号**：
- ActSuspCtrlOrigTargetDampForce_FL/FR/RL/RR（轮减震器目标主动力）
- ActSuspActulDampForce_FL/FR/RL/RR（轮减振器实际减振力）

---

### 4.2.6 与智驾系统相关功能的仲裁关系

所有智驾功能激活时，CST功能不允许激活。CST功能在智驾功能激活后，需要退出。
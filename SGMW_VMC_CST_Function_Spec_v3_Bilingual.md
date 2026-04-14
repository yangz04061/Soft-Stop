# SGMW VMC Comfortable Stop (CST) Function Specification

# SGMW VMC 舒适制动（Comfortable Stop）功能规范

---

## 1. 功能描述 / Function Description

舒适制动（Comfortable Stop简称CST）功能是一个可选的舒适性功能，该功能致力于解决车辆前进行驶非紧急制动工况车辆刹停前出现的减速度波动，降低车辆制动俯仰，使用制动（只考虑电制动可选）和悬架控制（阻尼、刚度和高度）实现舒适制动的效果。

The Comfortable Stop (CST) function is an optional comfort feature that aims to solve the deceleration fluctuation during vehicle braking in non-emergency forward driving conditions, reduce vehicle brake pitch, and achieve comfortable braking effect through braking (only electric braking optional) and suspension control (damping, stiffness, and height).

CST功能仅在汽车非紧急情况减速停车时激活，为驾驶员提供平稳的感觉。

CST is only activated when the vehicle decelerates and stops in non-emergency situations, providing a smooth driving experience for the driver.

### 1.1 激活和退出条件 / Activation and Exit Conditions

1. 当车速低于一个门限值且制动压力大于某一门限值，CST功能激活（"CST_Status"=Active），此时减速行为通过制动（只使用电制动）控制，VMC CST功能负责保证激活时的平顺性。
2. When vehicle speed is below a threshold and brake pressure is above a certain threshold, CST function activates ("CST_Status"=Active). At this time, deceleration is controlled by braking (only electric braking), and VMC CST function is responsible for ensuring smoothness during activation.
3. 为了保证电制动能够平顺刹停车辆，在CST的最后阶段，舒适制动会通过转速接口来保证车辆静止。当车辆确认静止后（standstill状态确认），CST功能需要退出（"CST_Status"=Standby），制动系统介入保证车辆维持在当前位置，制动系统需要保证握手时的平顺性。
4. To ensure electric braking can smoothly stop the vehicle, in the final stage of CST, comfortable braking will ensure vehicle stationary through speed interface. After vehicle standstill is confirmed, CST function needs to exit ("CST_Status"=Standby), brake system intervenes to maintain vehicle position, and brake system needs to ensure smooth handshaking.
5. 当出现驾驶员紧急制动的情况，CST功能需要退出（"CST_Status"=Standby），制动系统介入保证满足驾驶员的制动请求，制动系统需要保证握手时的平顺性。
6. When driver performs emergency braking, CST function needs to exit ("CST_Status"=Standby), brake system intervenes to meet driver's braking request, and brake system needs to ensure smooth handshaking.
7. 当驾驶员释放制动踏板时（或者主缸压力小于xxbar），CST功能需要退出（"CST_Status"=Standby）。
8. When driver releases brake pedal (or master cylinder pressure less than xxbar), CST function needs to exit ("CST_Status"=Standby).
9. 当检测到车辆驶到坡道（坡度>=15% TBD），CST功能需要退出（"CST_Status"=Standby），制动系统介入保证满足驾驶员的制动请求，制动系统需要保证握手时的平顺性。
10. When vehicle is detected on slope (grade>=15% TBD), CST function needs to exit ("CST_Status"=Standby), brake system intervenes to meet driver's braking request, and brake system needs to ensure smooth handshaking.
11. 当整车稳定控制功能激活时：

    - 制动：ABS, EBD, TCS, YSC, DTC等稳定控制功能激活
    - VMC：TankTurn, CompasTurn, TBH等纵向功能功能激活

    CST功能需要退出（"CST_Status"=Standby），制动系统介入，制动系统需要保证握手时的平顺性。
12. When vehicle stability control function activates:

    - Brake: ABS, EBD, TCS, YSC, DTC and other stability control functions activate
    - VMC: TankTurn, CompasTurn, TBH and other longitudinal functions activate

    CST function needs to exit ("CST_Status"=Standby), brake system intervenes, and brake system needs to ensure smooth handshaking.
13. 当智驾系统功能（AEB/APA/ACC）激活时，CST功能需要退出（"CST_Status"=Standby），制动系统介入响应智驾的请求，制动系统需要保证握手时的平顺性。
14. When ADAS system functions (AEB/APA/ACC) activate, CST function needs to exit ("CST_Status"=Standby), brake system responds to ADAS request, and brake system needs to ensure smooth handshaking.
15. 如果驾驶员手动按压开关，HMI会基于VMC发送的状态（VMCSoftStopFlg：0x0:Off 0x1:Standby 0x2:Active 0x3:Failure）判定驾驶员激活还是关闭CST功能。

    - 当VMCSoftStopFlg=0x0:Off时，驾驶员按压开关，HMI发送CSTSwRqst=0x1:激活
    - 当VMCSoftStopFlg!=0x0:Off时，驾驶员按压开关，HMI发送CSTSwRqst=0x1:关闭
16. If driver manually presses switch, HMI determines whether to activate or deactivate CST based on VMC sent status (VMCSoftStopFlg: 0x0:Off 0x1:Standby 0x2:Active 0x3:Failure).

    - When VMCSoftStopFlg=0x0:Off, driver presses switch, HMI sends CSTSwRqst=0x1: activate
    - When VMCSoftStopFlg!=0x0:Off, driver presses switch, HMI sends CSTSwRqst=0x1: deactivate
17. 正常下电后，CST开关状态需要保持记忆，VMC需要将下电前的CST状态（VMCSoftStopFlg）通过RTE发给Host ECU。Host ECU(联电)需要将这个开关状态信号通过NVRAM存储。再次上电时，需要发送记忆状态给VMC，VMC会更新记忆的状态（VMCSoftStopFlg）然后发给HMI。HMI需要基于CST反馈的状态，显示当前HMI上CST功能的开关状态。
18. After normal power off, CST switch status needs to be memorized. VMC needs to send pre-power-off CST status (VMCSoftStopFlg) to Host ECU via RTE. Host ECU (United Tech) needs to store this switch status signal via NVRAM. On next power-on, memorized status needs to be sent to VMC, VMC will update memorized status (VMCSoftStopFlg) and then send to HMI. HMI needs to display current CST switch status on HMI based on CST feedback status.

---

## 2. 系统架构 / System Architecture

### 2.1 功能架构 / Functional Architecture

#### 2.1.1 与子系统自身控制功能边界区分 / Boundary Definition with Subsystem Control Functions

VMC的CST功能主要通过制动（仅电制动可选）和悬架的控制。

VMC CST function mainly controls through braking (only electric braking optional) and suspension control.

**VCU（电制动可选）**：

- VMC请求电制动扭矩发给VCU，如果VCU收到了来自制动系统的更高优先级功能的请求（例如一些稳定性功能DTC等），Override VMC，VCU优先执行制动高优先级请求，VMC的CST功能也会退出
- VMC sends electric brake torque request to VCU. If VCU receives higher priority function requests from brake system (e.g., stability functions like DTC), VCU overrides VMC, executes brake high priority requests, and VMC CST function also exits
- CST功能激活的最后时刻，VMC会将电制动请求缓慢降为0，然后把控制模式由扭矩模式转为转速模式，转速模式下会发送目标转速（目标转速=0）给前后电机。从而需要电机保证此时车辆静止
- At the final moment of CST activation, VMC will slowly reduce electric brake request to 0, then switch control mode from torque mode to speed mode. In speed mode, target speed (target speed=0) is sent to front and rear motors. Motors need to ensure vehicle stationary at this time
- 当VMC CST功能出于某些原因在车辆正常静止前退出（"CST_Status"=Standby/Off/Failure）,VCU应该保证接手驱动部分的控制，保证平滑过渡到VCU请求的扭矩值
- When VMC CST function exits for some reason before vehicle normal standstill ("CST_Status"=Standby/Off/Failure), VCU should ensure taking over drive part control, ensuring smooth transition to VCU requested torque value
- 当VMC激活时，VMC CST功能会基于VCU的coasting请求，ramp到目标请求，保证平顺性。谁握手谁来保证控制平顺性的原则
- When VMC is activated, VMC CST function will ramp to target request based on VCU's coasting request, ensuring smoothness. Principle: whoever handshakes ensures control smoothness

**制动执行器（不控制液压制动，但是需要从制动执行器获取相关信号保证激活时平顺握手控制）**：

- VMC CST激活后，制动执行器需要将制动请求（10kph只有液压制动）降为0，VMC CST功能需要基于制动执行器退出时残余制动扭矩，来增加CST的电制动请求值，保证车辆不出现闯动
- After VMC CST activates, brake actuator needs to reduce brake request (only hydraulic brake at 10kph) to 0. VMC CST function needs to increase CST electric brake request value based on residual brake torque when brake actuator exits, ensuring no vehicle jerk
- 当VMC CST功能出于某些原因退出（"CST_Status"=Standby/Off/Failure）, VMC CST功能需要将制动请求（只有电制动）降为某个目标值（8kph以上=coasting torque，8kph以下=0），制动执行器需要基于VMC退出时的电制动扭矩，调整制动功能的请求值，保证车辆不出现闯动。制动系统需要保证握手时的平顺性。谁握手谁来保证控制平顺性的原则
- When VMC CST function exits for some reason ("CST_Status"=Standby/Off/Failure), VMC CST function needs to reduce brake request (only electric brake) to a target value (above 8kph=coasting torque, below 8kph=0). Brake actuator needs to adjust brake function request value based on VMC exit electric brake torque, ensuring no vehicle jerk. Brake system needs to ensure smooth handshaking. Principle: whoever handshakes ensures control smoothness

**主动悬架**：

- VMC控四轮侧主动悬架的阻尼、刚度。配合制动（电制动）控制，减少制动俯仰的影响。CST功能激活期间，VMC拥有控制最高优先级
- VMC controls active suspension damping and stiffness at four wheels. Cooperates with braking (electric brake) control to reduce brake pitch influence. During CST activation, VMC has highest control priority

**CDC**：

- VMC控四轮侧CDC的阻尼、刚度。配合制动（电制动）控制（min/max电流控制），减少制动俯仰的影响。CST功能激活期间，VMC拥有控制最高优先级
- VMC controls CDC damping and stiffness at four wheels. Cooperates with braking (electric brake) control (min/max current control) to reduce brake pitch influence. During CST activation, VMC has highest control priority

**空气弹簧**：

- VMC控制空簧的刚度和高度。配合制动（电制动）控制，减少制动俯仰的影响。CST功能激活期间，VMC拥有控制最高优先级
- VMC controls air suspension stiffness and height. Cooperates with braking (electric brake) control to reduce brake pitch influence. During CST activation, VMC has highest control priority

---

## 3. 执行器需求 / Actuator Requirements

该功能需要控制后转、制动执行器等。需要至少有一个执行器可用。

This function requires controlling rear steering, brake actuators, etc. At least one actuator must be available.

| 序号 | 系统 | 零部件名称                | 配置需求 | 需求概述                                                            |
| ---- | ---- | ------------------------- | -------- | ------------------------------------------------------------------- |
| 1    | 转向 | RWS后轮转向执行器         | -        | CST不控制后转                                                       |
| 2    | 转向 | SBW线控转向/EPS非线控转向 | -        | CST不控制前转                                                       |
| 3    | 悬架 | CDC连续可变阻尼减振器     | 可选     | 阻尼调节（目标电流min/max）优化pitch control，握手后VMC进行独占控制 |
| 4    | 悬架 | 空气弹簧                  | 可选     | 空簧刚度调节优化pitch control，握手后VMC进行独占控制                |
| 5    | 悬架 | 主动悬架                  | 可选     | 主动施加damping force优化pitch control                              |
| 6    | 驱动 | 轴间四驱                  | 可选     | VMC分别控制前后轴电制动扭矩                                         |
| 7    | 驱动 | 分布式四驱                | 可选     | VMC分别控制前后左右四电机电制动扭矩                                 |
| 8    | 制动 | EHBi 集成式电机液压制动   | -        | CST不控制液压制动                                                   |
| 9    | 制动 | EMB 机械电子制动          | -        | CST不控制液压制动                                                   |

| No. | System     | Part Name                               | Config Requirement | Requirement Summary                                                                                                |
| --- | ---------- | --------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------ |
| 1   | Steering   | RWS Rear Wheel Steering Actuator        | -                  | CST does not control rear steering                                                                                 |
| 2   | Steering   | SBW Steer-by-Wire/EPS Non-Steer-by-Wire | -                  | CST does not control front steering                                                                                |
| 3   | Suspension | CDC Continuously Variable Damping       | Optional           | Damping adjustment (target current min/max) to optimize pitch control, after handshake VMC takes exclusive control |
| 4   | Suspension | Air Suspension                          | Optional           | Air spring stiffness adjustment to optimize pitch control, after handshake VMC takes exclusive control             |
| 5   | Suspension | Active Suspension                       | Optional           | Active damping force to optimize pitch control                                                                     |
| 6   | Drive      | Inter-axle Four-wheel Drive             | Optional           | VMC separately controls front/rear axle electric brake torque                                                      |
| 7   | Drive      | Distributed Four-wheel Drive            | Optional           | VMC separately controls four motor electric brake torque (front/rear left/right)                                   |
| 8   | Brake      | EHBi Integrated Electro-hydraulic Brake | -                  | CST does not control hydraulic brake                                                                               |
| 9   | Brake      | EMB Electronic Mechanical Brake         | -                  | CST does not control hydraulic brake                                                                               |

---

## 4. 功能逻辑策略 / Functional Logic Strategy

### 4.1 功能逻辑策略概览 / Functional Logic Overview

CST功能逻辑：仅通过制动（仅电制动）实现平稳减速的目标，同时悬架执行器也需要动态调整悬架刚度，进一步优化Pitch Control。

CST functional logic: Achieve smooth deceleration goal only through braking (only electric braking), while suspension actuators also need to dynamically adjust suspension stiffness to further optimize Pitch Control.

---

### 4.1.1 功能激活和退出策略 / Function Activation and Exit Strategy

CST功能具有以下状态：Off、Standby、Active、Failure

CST function has the following states: Off, Standby, Active, Failure

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

**Condition 1: All conditions below must be met, CST Standby switches to Active**

- CST switch is ON
- No fault degradation signal valid (vehicle speed, wheel speed, pedal signal, etc. valid)
- Vehicle stability control function not activated (ABS, TCS, YSC, etc. stability control functions not activated)
- Tank/Compass/TBH blowout stability function not activated
- Motor Regen torque not limited (high SOC/low temperature/motor torque limit)
- ADAS function not activated
- Brake pedal above threshold
- Brake pedal rate less than threshold (non-emergency braking)
- Vehicle speed in working range (TBD < speed < TBD)
- Deceleration in working range
- Grade less than threshold
- Vehicle in forward gear
- Lateral acceleration less than threshold
- Steering angle less than threshold

**条件2：满足下面任意条件，CST Active 切换到 Standby**

- 整车稳定控制功能激活（紧急制动工况，ABS, TCS, YSC等稳定控制功能激活）
- 坦克/圆规/蟹行/TBH爆胎稳定功能激活
- 驾驶员制动踏板位置低于阈值（驾驶员松开制动踏板）
- 电机Regen torque受限（高SOC/低温/电机限扭）
- 速度不在工作区间（高于TBD，低于TBD）
- 驾驶员制动踏板速率过大（紧急制动）
- ADAS功能激活

**Condition 2: Any condition below is met, CST Active switches to Standby**

- Vehicle stability control function activated (emergency braking condition, ABS, TCS, YSC, etc. stability control functions activated)
- Tank/Compass/Crab/TBH blowout stability function activated
- Driver brake pedal position below threshold (driver releases brake pedal)
- Motor Regen torque limited (high SOC/low temperature/motor torque limit)
- Speed not in working range (above TBD, below TBD)
- Driver brake pedal rate too high (emergency braking)
- ADAS function activated

**条件3：满足下面任意条件，CST Active 切换到 Off**

- 开关关闭
- 开关信号无效

**Condition 3: Any condition below is met, CST Active switches to Off**

- Switch turned off
- Switch signal invalid

**条件4：满足下面条件，CST Off 切换到 Standby**

- 场景A - CST处于未打开状态：车辆处于ready状态 且 制动、动力&VMC系统无任何故障 且 驾驶员手动按下开关（虚拟）打开CST功能
- 场景B - CST处于记忆状态（上一次打开后未通过开关关闭）：车辆处于ready状态 且 制动、动力&VMC系统无任何故障

**Condition 4: Conditions below are met, CST Off switches to Standby**

- Scenario A - CST not opened: Vehicle in ready state AND brake, powertrain & VMC system have no faults AND driver manually presses switch to open CST
- Scenario B - CST in memory state (opened before, not closed via switch): Vehicle in ready state AND brake, powertrain & VMC system have no faults

**条件5：满足下面任意条件，CST Standby 切换到 Off**

- 开关关闭

**Condition 5: Any condition below is met, CST Standby switches to Off**

- Switch turned off

**条件6：满足下面任意条件，CST Standby 切换到 Failure**

- 故障降级（包括电制动能力故障）
- 关键信号无效

**Condition 6: Any condition below is met, CST Standby switches to Failure**

- Fault degradation (including electric brake capability fault)
- Critical signal invalid

**条件7：同时满足下面所有条件，CST Failure 切换到 Standby**

- 故障恢复
- 关键信号恢复
- 开关保持开启

**Condition 7: All conditions below are met, CST Failure switches to Standby**

- Fault recovered
- Critical signal recovered
- Switch remains ON

**条件8：满足下面任意条件，CST Active 切换到 Failure**

- 故障降级（包括电制动能力故障）
- 关键信号无效

**Condition 8: Any condition below is met, CST Active switches to Failure**

- Fault degradation (including electric brake capability fault)
- Critical signal invalid

---

### 4.2 控制逻辑 / Control Logic

**核心控制算法**：通过前馈控制（基于减速度，俯仰角及俯仰角导数等）和反馈控制（控制目标为俯仰角）调节前后轴的制动（电制动）扭矩来减小俯仰角，从而达到舒适制动的效果。悬架也会将俯仰作为控制目标，通过调整悬架刚度来进一步优化车辆点头。

**Core Control Algorithm**: Through feedforward control (based on deceleration, pitch angle and pitch angle derivative, etc.) and feedback control (control target is pitch angle) to adjust front/rear axle braking (electric brake) torque to reduce pitch angle, thereby achieving comfortable braking effect. Suspension also uses pitch as control target, adjusting suspension stiffness to further optimize vehicle nose dive.

**驾驶模式选择**：不区分驾驶模式

**Driving Mode Selection**: No distinction by driving mode

**执行器使用策略**：CST控制功能工作时会使用所有以下范围内可用执行器：包括驱动系统执行器（电制动控制regen torque control）

**Actuator Usage Strategy**: CST control function will use all available actuators within the following scope: including drive system actuators (electric brake control regen torque control)

---

### 4.2.1 驱动系统执行器（电制动控制） / Drive System Actuator (Electric Brake Control)

#### 轴间四驱 / Axis Four-wheel Drive

**轴间四驱车型**：CST功能请求前后轴的电制动扭矩给VCU。

**Axis Four-wheel Drive Models**: CST function requests front/rear axle electric brake torque from VCU.

**前后电机请求的控制模式**：

| 信号                   | 0x0        | 0x1           | 0x2                  | 0x3                  |
| ---------------------- | ---------- | ------------- | -------------------- | -------------------- |
| FrntAxleTarDrvModeRqst | No Request | Speed Control | Drive Torque Control | Regen Torque Control |
| ReAxleTarDrvModeRqst   | No Request | Speed Control | Drive Torque Control | Regen Torque Control |

**Front/Rear Motor Request Control Mode**:

| Signal                 | 0x0        | 0x1           | 0x2                  | 0x3                  |
| ---------------------- | ---------- | ------------- | -------------------- | -------------------- |
| FrntAxleTarDrvModeRqst | No Request | Speed Control | Drive Torque Control | Regen Torque Control |
| ReAxleTarDrvModeRqst   | No Request | Speed Control | Drive Torque Control | Regen Torque Control |

**前后轴电机电制动请求扭矩**：

- VMCTarDrvTqFrnt：当FrntAxleTarDrvModeRqst=0x03（Regen Torque Control）时，VMCTarDrvTqFrnt请求的值只会是前轴主减前的电制动regen请求，VCU无需根据请求扭矩值的符号来做任何判定。VCU需要保证电机处于电制动请求状态（轮速和扭矩方向相反）
- VMCTarDrvTqFrnt: When FrntAxleTarDrvModeRqst=0x03 (Regen Torque Control), the value requested by VMCTarDrvTqFrnt is only the electric brake regen request before front axle main reducer. VCU does not need to make any judgment based on the sign of requested torque value. VCU needs to ensure motor is in electric brake request state (wheel speed and torque direction are opposite)
- 对于EV轴间四驱车型：前轴主减前的目标电制动扭矩和电机端的目标电制动扭矩是一致的
- For EV axis four-wheel drive models: target electric brake torque before front axle main reducer is consistent with motor end
- 对于PHEV车型，前轴主减前的目标电制动扭矩对应Z3的扭矩，VCU需要考虑Z2/Z1的传动比保证电机端的目标电制动扭矩
- For PHEV models, target electric brake torque before front axle main reducer corresponds to Z3 torque. VCU needs to consider Z2/Z1 gear ratio to ensure motor end target electric brake torque
- VMCTarDrvTqRe：当ReAxleTarDrvModeRqst=0x03（Regen Control）时，VMCTarDrvTqRe请求的值只会是后轴主减前的电制动regen请求，VCU无需根据请求扭矩值的符号来做任何判定。VCU需要保证电机处于电制动请求状态（轮速和扭矩方向相反）
- VMCTarDrvTqRe: When ReAxleTarDrvModeRqst=0x03 (Regen Control), the value requested by VMCTarDrvTqRe is only the electric brake regen request before rear axle main reducer. VCU does not need to make any judgment based on the sign of requested torque value. VCU needs to ensure motor is in electric brake request state
- 对于所有轴间四驱车型，后轴主减前的目标电制动扭矩和电机端的目标电制动扭矩是一致的
- For all axis four-wheel drive models, target electric brake torque before rear axle main reducer is consistent with motor end

**前后轴电机速度请求**：

- VMCTarSpdFrnt：当FrntAxleTarDrvModeRqst=0x01（Speed Control）时，VMCTarSpdFrnt请求前轴主减前的目标速度
- VMCTarSpdFrnt: When FrntAxleTarDrvModeRqst=0x01 (Speed Control), VMCTarSpdFrnt requests target speed before front axle main reducer

  - 对于EV轴间四驱车型：前轴主减前的目标速度和电机端速度应是一致的
  - For EV axis four-wheel drive models: target speed before front axle main reducer should be consistent with motor end
  - 对于PHEV车型，前轴主减前的目标速度对应Z3的速度，VCU需要考虑Z2/Z1的传动比保证电机端的目标速度
  - For PHEV models, target speed before front axle main reducer corresponds to Z3 speed. VCU needs to consider Z2/Z1 gear ratio to ensure motor end target speed
- VMCTarSpdRe：当ReAxleTarDrvModeRqst=0x01（Speed Control）时，VMCTarSpdRe请求后轴主减前的目标速度
- VMCTarSpdRe: When ReAxleTarDrvModeRqst=0x01 (Speed Control), VMCTarSpdRe requests target speed before rear axle main reducer

  - 对于所有轴间四驱车型，后轴主减前的目标速度和电机端的速度是一致的
  - For all axis four-wheel drive models, target speed before rear axle main reducer is consistent with motor end

---

#### 分布式四驱 / Distributed Four-wheel Drive

**分布式四驱**：CST功能请求四个电机侧的主减前的电制动扭矩给VCU。

**Distributed Four-wheel Drive**: CST function requests electric brake torque before main reducer for four motor sides from VCU.

**四电机的电机请求的控制模式**：

- TarDrvModeFrntLe（左前电机控制模式）
- TarDrvModeFrntRi（右前电机控制模式）
- TarDrvModeReLe（左后电机控制模式）
- TarDrvModeReRi（右后电机控制模式）
- TarDrvModeFrntLe (Left Front Motor Control Mode)
- TarDrvModeFrntRi (Right Front Motor Control Mode)
- TarDrvModeReLe (Left Rear Motor Control Mode)
- TarDrvModeReRi (Right Rear Motor Control Mode)

控制模式定义：0x0 No Request, 0x1 Speed Control, 0x2 Drive Torque Control, 0x3 Regen Torque Control

Control mode definition: 0x0 No Request, 0x1 Speed Control, 0x2 Drive Torque Control, 0x3 Regen Torque Control

**四电机的电制动请求扭矩**：

- VMCTarDrvTqFL_1st/VMCTarDrvTqFR_2nd/VMCTarDrvTqRL_3rd/VMCTarDrvTqRR_4th
- VMCTarDrvTqFL_1st/VMCTarDrvTqFR_2nd/VMCTarDrvTqRL_3rd/VMCTarDrvTqRR_4th
- 当TarDrvModeFrntLe/FrntRi/ReLe/ReRi=0x03（Regen Torque Control）时，请求的值只会是四个电机主减前的电制动regen请求，VCU无需根据请求扭矩值的符号来做任何判定。VCU需要保证电机处于电制动请求状态（轮速和扭矩方向相反）
- When TarDrvModeFrntLe/FrntRi/ReLe/ReRi=0x03 (Regen Torque Control), the requested value is only the electric brake regen request before four motors main reducer. VCU does not need to make any judgment based on the sign of requested torque value. VCU needs to ensure motor is in electric brake request state (wheel speed and torque direction are opposite)
- 对于所有四电机车型：主减前的目标电制动扭矩和电机端的目标电制动扭矩是一致的
- For all four-motor models: target electric brake torque before main reducer is consistent with motor end

**前后轴电机速度请求**：

- VMCTarSpdFL_1st/VMCTarSpdFR_2nd/VMCTarSpdRL_3rd/VMCTarSpdRR_4th
- VMCTarSpdFL_1st/VMCTarSpdFR_2nd/VMCTarSpdRL_3rd/VMCTarSpdRR_4th
- 当TarDrvModeFrntLe/FrntRi/ReLe/ReRi=0x01（SpeedControl）时，请求的是主减前的目标速度
- When TarDrvModeFrntLe/FrntRi/ReLe/ReRi=0x01 (SpeedControl), requests target speed before main reducer
- 对于所有四电机车型：主减前的目标速度和电机端速度是一致的
- For all four-motor models: target speed before main reducer is consistent with motor end

**从VCU接收的信号**：以下信号用来表征电机电制动能力的大小

- PrDrvMtrTorqMinLitVal_FD：双电机前轴主减前的电制动能力
- MCU2MtrTorqMinLitVal_FD：四电机左前主减前的电制动能力
- MCU3MtrTorqMinLitVal_FD：四电机右前主减前的电制动能力
- MCU4MtrTorqMinLitVal_FD：四电机左后主减前的电制动能力
- 双电机后轴及四电机右后主减前的电制动能力

**Signals Received from VCU**: The following signals represent motor electric brake capability

- PrDrvMtrTorqMinLitVal_FD: Dual motor front axle electric brake capability before main reducer
- MCU2MtrTorqMinLitVal_FD: Four-motor left front electric brake capability before main reducer
- MCU3MtrTorqMinLitVal_FD: Four-motor right front electric brake capability before main reducer
- MCU4MtrTorqMinLitVal_FD: Four-motor left rear electric brake capability before main reducer
- Dual motor rear axle and four-motor right rear electric brake capability before main reducer

---

### 4.2.2 后轮转向 / Rear Wheel Steering

**边界定义**：CST功能不使用后转执行器

**Boundary Definition**: CST function does not use rear steering actuator

---

### 4.2.3 前轮转向 / Front Wheel Steering

**边界定义**：CST功能不使用前转执行器

**Boundary Definition**: CST function does not use front steering actuator

---

### 4.2.4 悬架系统（CDC、空簧） / Suspension System (CDC, Air Suspension)

**边界定义**：VMC CST功能的垂向/载荷调整功能控制CDC的目标电流（min/max），以及空气弹簧的目标刚度等级。

**Boundary Definition**: VMC CST vertical/load adjustment function controls CDC target current (min/max), and air suspension target stiffness level.

**连续可调阻尼减振器（CDC）控制**：

- VMC CST功能激活时，通过0x0C0报文发送CDC控制目标请求给SUCU悬架控制器
- When VMC CST function activates, sends CDC control target request to SUCU suspension controller via 0x0C0 message
- CDC激活请求 CdcActvRqst = 0x1（Request请求）
- CDC activation request CdcActvRqst = 0x1 (Request)
- CDC电流百分比 CdcCurrentReq_xx
- CDC current percentage CdcCurrentReq_xx
- SUCU反馈：CDC减震器状态CdcActrStsFb = 0x1（Controlled）、SUCU电磁阀实际电流百分比SUCUVlvTrgtCrnt_XX、CDC基础电流百分比CdcBaseCurrent_xx
- SUCU feedback: CDC damper status CdcActrStsFb = 0x1 (Controlled), SUCU solenoid valve actual current percentage SUCUVlvTrgtCrnt_XX, CDC base current percentage CdcBaseCurrent_xx
- VMC CST功能控制频率10ms左右
- VMC CST function control frequency ~10ms

**空气弹簧控制**：

- 空簧有两种请求模式：高度请求和刚度请求
- Air suspension has two request modes: height request and stiffness request
- 高度控制：AirSuspTarHei_FL/FR/RL/RR
- Height control: AirSuspTarHei_FL/FR/RL/RR
- 刚度控制：TarStfnLvlFrntLe/FrntRi/ReLe/ReRi
- Stiffness control: TarStfnLvlFrntLe/FrntRi/ReLe/ReRi
- 空簧请求AirSuspActvRqst = 0x1 Request
- Air suspension request AirSuspActvRqst = 0x1 Request

---

### 4.2.5 主动悬架 / Active Suspension

**边界定义**：VMC CST功能的垂向/载荷调整功能控制主动悬架的主动阻尼力。

**Boundary Definition**: VMC CST vertical/load adjustment function controls active suspension active damping force.

**控制策略**：

- VMC CST功能激活时，根据Pitch Angle调整需求计算主动悬架的主动阻尼力，通过0x0C0报文发送控制目标请求给SUCU悬架控制器
- When VMC CST function activates, calculates active suspension active damping force based on Pitch Angle adjustment demand, sends control target request to SUCU suspension controller via 0x0C0 message
- 主动悬架激活请求 ActvSuspActvRqst = 0x2 = Mode Damper Force
- Active suspension activation request ActvSuspActvRqst = 0x2 = Mode Damper Force
- 主动悬架目标阻尼力 ActvSuspTarForce_FL/FR/RL/RR
- Active suspension target damping force ActvSuspTarForce_FL/FR/RL/RR
- 主动悬架执行器状态 ActSuspActrSts = 0x2 = Mode Damper Force 代表握手成功，执行VMC的目标阻尼力，此时由VMC独占进行阻尼力控制
- Active suspension actuator status ActSuspActrSts = 0x2 = Mode Damper Force represents successful handshake, executes VMC target damping force, at this time VMC exclusively controls damping force
- VMC CST功能控制频率10ms左右
- VMC CST function control frequency ~10ms

**反馈信号**：

- ActSuspCtrlOrigTargetDampForce_FL/FR/RL/RR（轮减震器目标主动力）
- ActSuspCtrlOrigTargetDampForce_FL/FR/RL/RR (Wheel Damper Target Active Force)
- ActSuspActulDampForce_FL/FR/RL/RR（轮减振器实际减振力）
- ActSuspActulDampForce_FL/FR/RL/RR (Wheel Damper Actual Damping Force)

---

### 4.2.6 与智驾系统相关功能的仲裁关系 / Arbitration Relationship with ADAS Functions

所有智驾功能激活时，CST功能不允许激活。CST功能在智驾功能激活后，需要退出。

When all ADAS functions are activated, CST function is not allowed to activate. After ADAS functions activate, CST function needs to exit.

---

*End of Document / 文档结束*

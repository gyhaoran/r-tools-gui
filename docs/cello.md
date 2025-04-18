# Cello
Cello是一个Cmos后端物理设计 标准单元库设计和优化软件平台，我们需要对他的功能进行测试摸底，希望熟悉这个软件的功能和设计
以下是我们设计的一些设计用例，请帮我重新梳理和补充完善


## testcase

1. 核心功能测试
​基础操作
​Main Menu功能检查
菜单项完整性（File/Edit/View/Tools/Help等）。
子菜单功能是否可正常触发（如Save, Export, Preferences）。
​Library管理
new library：支持自定义名称、路径、工艺节点绑定。
open library：兼容不同版本库文件，加载速度与内存占用。
close library：关闭时是否提示保存未提交的修改。
import tech：支持的工艺文件格式（如LEF, .tech, .tf），是否支持工艺参数自定义（金属层、DRC规则）。
​任务控制
create_layout：布局布线成功率，是否支持约束条件（面积、时序）。
re_route：优化后的布线长度、通孔数量变化。
stop/cancel/restart：任务中断时资源释放是否彻底，重启后能否恢复断点。
​高级功能
​单元库设计与优化
标准单元自动生成（逻辑门、触发器）是否符合DRC规则。
单元优化功能（面积、功耗、驱动强度）的算法效果验证。
​物理验证
DRC检查：支持主流规则（间距、宽度、天线效应）。
LVS检查：网表与版图一致性验证。
​分析工具
时序分析：结合SPICE仿真结果验证关键路径延迟。
功耗分析：静态/动态功耗估算精度。
​2. 流程完整性测试
​端到端设计流程
记录从启动到完成设计的全流程（示例）：

​启动软件：初始化时间，默认界面配置。
​创建/导入工艺文件：加载.tech文件，验证层定义与规则解析。
​新建Library：绑定工艺，设置单元命名规则。
​设计标准单元：通过GUI或脚本生成AND/OR门版图。
​布局布线：
自动布局：拥塞度评估。
手动调整：拖拽、旋转、对齐功能。
​物理验证：DRC/LVS错误定位与修复流程。
​导出数据：GDSII/LEF/DEF文件生成，验证与其他EDA工具（如Cadence, Synopsys）的兼容性。
​资源与性能监控
各步骤的CPU/内存占用率。
任务耗时与设计规模（单元数量、金属层数）的关系。
​3. 用户友好性测试
​历史记录与个性化
用户操作历史（最近打开的Library/Project）。
设置持久化：颜色方案、快捷键、默认工艺路径。
​GUI交互
可视化功能：版图缩放/平移流畅度，高亮显示DRC错误。
快捷键：自定义支持与冲突检测。
帮助文档：内置文档搜索功能，是否提供示例库。
​多语言支持
界面语言切换（中文/英文等），术语一致性。
​4. 并发与稳定性测试
​多任务并发
并发任务数上限设置（如10个并行Job）。
资源争用场景：多个任务同时进行DRC检查时的稳定性。
​异常处理
强制终止进程：数据恢复能力（自动保存机制）。
错误输入：非法工艺文件、超大规模版图导入时的崩溃风险。
​5. 扩展性与兼容性测试
​工艺节点兼容性
7nm/14nm/28nm等节点的特性文件支持。
​EDA工具链集成
导出文件与Virtuoso/Calibre的兼容性。
脚本接口：Tcl/Python API是否支持自动化流程。
​操作系统支持
Linux/CentOS/Windows下的安装与运行测试。
​6. 补充测试用例建议
​压力测试
超大规模设计（10万+单元）的布局布线能力。
​安全性与数据完整性
项目文件加密与权限控制。
自动备份机制（如每30分钟保存一次）。
​版本升级验证
旧版本项目文件在新版本中的兼容性。
​测试用例优先级排序
​优先级	​测试项	​说明
P0	基础功能（Library管理、DRC/LVS）	确保核心流程可用性
P1	并发任务与稳定性	防止生产环境崩溃
P2	用户交互与多语言支持	提升用户体验
P3	扩展性（EDA集成、脚本API）	支持复杂设计流程自动化

### 功能相关
- Main Menu功能检查
- import tech? 是否支持
- new library如何设计
- open library
- 是否支持close library, 已经如何设计
- 布局布线任务（create_layout）， 重布线（re_route任务），查看电路图
- job 是否支持多并发，并发个数是否可设置
- 任务是否支持控制（stop、cancel、restart）

### 流程记录 
- 记录一下从开启软件到完成一个


### 用户友好性相关
- 是否记录用户历史记录
- 历史设置数据是否记录（history project/ color settings/ tech import）
- 

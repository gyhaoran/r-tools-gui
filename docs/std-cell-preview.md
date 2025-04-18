pyqt5 gui cmos后端物理版图自动化设计应用（标准单元库布局布线）

现状
我们的软件目前支持对标准单元库布局、布线和重新布线，以及反向布线（从gds到gds），支持不同的布局布线算法和策略，布局布线的规则，对单元库的pin评估
我们软件的架构：
- 前端gui(单独的bin): 支持布局布线任务的准备工作（创建工作目录），任务的提交，结果的显示gds的展示
- 后端算法（单独的bin）：

前后端交互的方式：通过调用bin，传递命令行参数来执行布局布线或者重布线的功能
前后端接口的定义
- place_rout命令
```bash
iCell_pr -tech=/path/tech.json  -cell=cell_name  -work_dir=/path/testcase/output/lib_name/cell_name_date_id
```
place_route的时候, 前端创建该单元的work_dir，里面内容包括
- /path/testcase/output/lib_name/cell_name_date_id
    - place_route_config.json # 布局布线配置参数
    - cell_name.sp            # 布局布线的单元的网表
    - gds/layout_1.gds        # 后端生成的布局布线结果
    - place/place_1.json      # 后端生成的布局结果


- reroute 命令
```bash
iCell_pr reroute -layout=layout_name -tech=/path/tech.json  -cell=cell_name -work_dir=/path/testcase/output/lib_name/cell_name_date_id
```
place_route的时候, 前端创建该单元的work_dir，里面内容包括
- /path/testcase/output/lib_name/cell_name_date_id
    - reroute_config.json
    - cell_name.sp
    - gds/layout_1.gds 
    - place/place_1.json
    - route/route_1.json


总体需求：
帮我设计一套支持运行用户编写的python脚本的通用框架，支持python原生语言，支持我们自己开放的能力open api

详细需求
我们开放的能力，需要包括但不限制于下面
1. 用户可以通过open api支持对布局或者布线规则的定制，算法的自定义或者选择
2. 定义一些自定义规则
3. 用户可以自定义pin assess的算法（我们的软件有标准单元的数据， 例如：所有引脚的信息，或者是用户直接读取版图信息）
4. 运行第三方软件，例如Carlibre(DRC), LVS等（这种可能是支持运行shell 脚本）（这条需求， 优先级靠后）

希望你输出：
1. 方案文档
2. MVP 穿刺Demo

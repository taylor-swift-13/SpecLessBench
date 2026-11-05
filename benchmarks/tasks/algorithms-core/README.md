# 基础算法三平台构造批次 v0.3.1

六个既有候选家族已落实为Lean、原生Rocq和C/CompCert三版，每组固定参考实现、替代实现和刻意保留的变异实现。每组选择一个候选等价上下文与一个反例上下文，合计12个语义任务、36个平台实例，不新增原目录槽位。与QCIP四组合计为10组、24个语义任务、72个平台实例；其他候选尚未全部实现。

**最终命题未证明。** 原生实现及待证明命题类型已检查，CompCert3.17的18个实际Clight AST和目标类型已检查；测试只能支持暂定标签。源码与目标绑定见[groups.json](groups.json)，构建环境见[compcert/build.json](compcert/build.json)。

| 组 | 固定域 | 实现差异 | 负例 |
|---|---|---|---|
| basic-factorial | n∈[0,12] | 直接递归／累加器尾递归 | 乘以前驱而非当前因子 |
| sequence-reversal | 长度0–64，值±10⁶ | 递归append反转／累加器或迭代反转 | 初始累加器多出0 |
| sequence-sum | 长度0–64，值±10⁶ | 递归求和／累加器或循环 | 漏掉最后元素 |
| matrix-product | 三个维度0–6，元素±1000 | 点积逐格／共享维度累积 | 将右矩阵按另一布局索引 |
| first-match-search | 文本0–64，模式0–32，字节0–255 | 朴素首匹配／KMP | 失配时总退回0 |
| queue-traces | 至多64条入队/出队/peek，值±10⁶ | 单列表／front-rear双列表 | 归一化后rear未清空 |

## 输入与观察

输入是有限整数序列，三个平台共用字段次序。Lean/Rocq直接接收有精确长度的序列；C把该序列补零放进8192字输入global，再调用固定main。没有外部I/O、动态分配或未定义callee。`c/Algorithms.h`按固定family/style宏预处理成每个具体实现，模型不能更改选择器。C平台中的“列表”用固定数组表示；原生版用不可变列表，平台的操作成本与调用形状不要求逐行一致。

- 阶乘：`[n]`，观察单个返回整数。12!在有符号32位范围内，任何实现的中间值仍须按CompCert目标证明安全。
- 反转/求和：`[n] ++ 数据`，观察完整反转列表／一个和。负例反转允许结果长度不同，不能裁剪成前n项掩盖错误。
- 矩阵：`[rows,inner,cols] ++ A行主序 ++ B行主序`，观察完整rows×cols输出。零维度合法，包括inner=0但输出非空的零结果。变异索引`j*inner+t`保持在B范围内，不能把越界当作有效反例。
- 字符串：`[text_len,pattern_len] ++ text ++ pattern`，观察首个匹配位置或-1；空模式返回0由固定实现表达。KMP使用具体prefix表构造与失配回退；原生回退燃料不足返回失败，不能视为有效相等。
- 队列：`[q] ++ q条[op,value]`，op=0入队、1出队、2只读peek；非入队的value固定0。空查询合法，输出found/value。观察每条操作的opcode、固定入队完成标记和查询结果；不观察内部列表、数组或不可见的rear。重复入队值允许。

输出有统一长度前缀。C同时观察main返回0及完整初始化的输出buffer；测试确认未用输出槽全0。原生版结果为`Option Words`，`None`表示失败。所有有效输入都必须成功，才能证明等价分支。

## 每题的待证明目标

参考为V0，替代为V1，变异为V2。每组的`R-*-EQ`固定V0/V1，`R-*-CEX`固定V0/V2；这些EQ/CEX ID只在整理端可见。三平台公开目标均为`Equivalent ∨ Counterexample`，不给极性。

**接受接口修订优先于上述概念析取：** 当前模型必须显式选择分支，反例必须提交具体输入和观察，并证明`refutationAt`专门化目标；不接受裸析取Prop证明。旧目标/模板保留为设计历史，不单独计分。全体24上下文的规范目标见[proof-interface](../../proof-interface/README.md)。

Lean目标在[lean/BasicGoals.lean](lean/BasicGoals.lean)，无`sorry`；`lean/pending/*.lean.goal`给出未填证明的theorem模板。Rocq目标在[rocq/BasicGoals.v](rocq/BasicGoals.v)，用`Abort`保留未证明状态，不引入公理。CompCert各组目标在`compcert/*Goals.v`，直接引用实际已生成的`compcert/ast/*.v`。

原生目标形式为：

```text
Eq  := forall x, valid x -> exists o, V0 x=Some o /\ Vj x=Some o
Cex := exists x oa ob, valid x /\ V0 x=Some oa /\ Vj x=Some ob /\ oa<>ob
```

CompCert目标将原生函数求值换为标准初始内存、输入global注入、无stuck且安全有限终止的Clight执行，以及固定输出投影。完整观察关系来自已类型检查的[Execution.v](compcert/Execution.v)。没有另外给出阶乘数学值、矩阵乘积、匹配位置或队列抽象状态的功能后置条件作为第三份正确结果oracle。

## 构造检查与重现

```sh
python3 scripts/construction/prepare_algorithms.py
python3 scripts/construction/build_algorithms.py
python3 scripts/construction/run_algorithms.py --smoke
python3 scripts/construction/run_algorithms.py
```

最终报告在`evidence/<family>.json`。本批次对输入去重，分别报告随机尝试数、实际新增随机输入数、小域穷举、边界和见证。阶乘穷举整个允许的值输入域；其他穷举范围仅为小域：长度≤7的三值序列、维度≤2的三值矩阵、短二值文本/模式、长度≤6的五种队列命令轨迹。

每个有效输入运行3变体×3可执行平台，共9次行为求值；另外以Lean/Rocq可执行域判断检查所有有效输入和一组非法边界输入。有效域计算次数单独记录，不充当行为求值或独立样本。C用GCC+ASan/UBSan执行，Clight只做AST和目标类型检查，**没有执行Clight语义差分**。

所有随机种子、生成器hash、确定性gzip语料hash、源码registry hash及失败案例均保留。先冒烟再完整测试；若出现非预期差异，保存全部差异和最短已测代表见证，修复或改变上下文后必须提升修订并重测。不能仅删除反例让测试通过。

## 来源、分组与成本

本批次为新编写的经典算法实现，借鉴的是公开通用算法思想，没有复制其他benchmark的代码、规约或参考证明；这不声称新算法，也不排除常见代码被模型训练语料覆盖。原有三个Rocq证明探针保留为历史记录，没有复制进新题的证明目标。

`sequence-reversal`和`matrix-product`同时作为未来C-REV/C-MAT等相关上下文的split-group归属，后续移植不能另外算独立程序家族。其余共享generic IO、编码或标准库不自动合并组；原生和C的风格标签需分别标注。

共享IO头文件复用QCIP派生批次的任务基础设施，不引入上游实现或功能契约。调用体均可见。新增编写、命名修复、构建失败、负例见证和修订进入`benchmarks/construction`追加日志。成本按组汇总，多个任务对／平台不重复收费，共享模型usage仅在`batch-algorithms-v0.3.json`计一次。历史或远端无法观测的计量仍明确未知。

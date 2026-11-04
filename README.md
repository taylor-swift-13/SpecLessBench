# SpecLessBench

项目已全面改名为 SpecLessBench，源码命名空间、构造脚本及证明接口采用新名称。历史构造日志保留当时记录；逐文件命名迁移与注册表重绑定记录见 [迁移审计](benchmarks/construction/rename-speclessbench.json)，历史数据可追溯至其中标注的基线提交。旧批次的差分报告描述改名前的运行，新命名下经典算法批次已重新执行完整差分测试。

SpecLessBench 的核心任务是：**不给独立的声明式功能规约，直接对两个固定实现证明等价，或给出可检查的反例。**一个简单、可信的实现可以充当可执行行为基准；模型必须构造等价证明，或提交满足输入条件且能形式化证明输出观察不同的反例。单纯“没证明出来”不算反例，也不算成功。

任务仍会给出输入域、必要前提和可观察接口，确保“等价”有明确边界；这些只是比较范围，不是第三份功能规约。即使有好的声明式规约，优化和实现替换中的行为保持本身也值得验证。

这类证明支持性能优化、数据结构替换、重构和跨语言迁移。它证明的是行为保持，不是参考实现符合用户意图：如果参考实现有缺陷，等价实现也可能保留该缺陷，因此信任重点落在容易审查的参考实现上。

SpecLessBench 聚焦于两个固定、结构不同的实现之间的行为对应。核心证明挑战是解释不同的计算过程为何产生相同结果；实现可能有不同的中间状态、循环次数和推进方式，无法简单逐步对齐。

## 第一版赛道

**每道任务提供 Lean、原生 Rocq 和 C/CompCert 三种平台实现。** 成本与划分以实现组为单位。当前 29 组包含 63 个语义任务，对应 189 个平台实例。构造阶段可根据差分反例修订实现和目标，并保留问题和修订记录。最终命题处于待证明状态。

- **原生 Rocq**：对两个 Rocq 函数提交全域等价证明，或提交满足输入前提且结果不同的输入及其证明。
- **C／Clight**：以 `clightgen` 导出的 Clight AST 和 CompCert 语义为证明对象。提交行为等价证明，或提交相关初始状态和安全执行证书，证明返回值／指定输出内存观察不同。题目不要求整个最终内存相等。

每题都必须明确观察范围，包括返回值、指定的内存修改、I/O 和终止性中哪些属于行为。本版排除外部 I/O 和浮点程序；未来若加入浮点题，必须明确区分逐位相等与误差界内接近等不同目标。

Lean 原生版与Rocq原生版分别比较各自平台中的两个实现；C/CompCert版研究Clight执行与内存语义。C源码导出AST不等于将源码自动转换成普通Rocq函数；原生移植的跨语言一致性目前接受差分审查，不冒充形式化精化证明。

## 当前状态

最新五组包括依赖图传播、作用域遮蔽、租约续期、带宽对齐和定点重采样。对齐保留并列最优末步，重采样保留舍入、越界与饱和标记。来源清单区分 Ninja、Bash、Redis 的改编场景与 R AirPassengers 的实际数值。Clight AST 中直接调用链最长为 4–5 条边。修订目录共 35 个候选条目和 80 个上下文槽位。

三平台定义与目标类型已检查，并导出 91 个实际 Clight AST。行为覆盖与输入域判断见 [累计汇总](benchmarks/construction/summary.json)。C 差分使用 GCC 和 ASan/UBSan，Clight 负责语义目标的类型检查。失败和重试计入成本，覆盖取选定的全量及补充语料。共享 token 精确拆组、编辑开销、并发进程树峰值和远端内存仍有计量缺口。

- [第一版设计](docs/v1-design.md)
- [任务契约](docs/task-contract.md)
- [12 题试验集规划](benchmarks/pilot/README.md)
- [候选目录与35条／80槽位修订](benchmarks/task-catalog.md)
- [基础任务卡](benchmarks/task-cards.md)
- [复杂数据结构与函数调用任务卡](benchmarks/complex-task-cards.md)
- [QCIP 四家族：16 个 C 入口／12 个待证明任务](benchmarks/tasks/qcip-core/README.md)
- [四家族的具体输入域、观察与最终定理](benchmarks/tasks/qcip-core/TASKS.md)
- [三平台实现与36个平台实例](benchmarks/tasks/qcip-core/THREE-PLATFORM.md)
- [新增六组基础算法与待证明任务](benchmarks/tasks/algorithms-core/README.md)
- [新增八组边界语义与数据结构任务](benchmarks/tasks/boundaries-core/README.md)
- [八组的输入域、错误观察与16个待证明问题](benchmarks/tasks/boundaries-core/TASKS.md)
- [新增三组状态历史与多层调用任务](benchmarks/tasks/stateful-core/README.md)
- [分帧、事务、缓存的具体输入观察与六题目标](benchmarks/tasks/stateful-core/TASKS.md)
- [五组图、状态和计算算法的输入观察与十题目标](benchmarks/tasks/systems-core/TASKS.md)
- [Prim/Kruskal、稳定排序及三平台目标](benchmarks/tasks/classics-core/README.md)
- [后续经典算法与数据结构候选](benchmarks/classic-candidates.md)
- [经典算法候选的来源、观察语义与初步筛查](benchmarks/research/classic-comparisons.md)
- [Base64 计算参考、RFC 向量与两题目标](benchmarks/tasks/base64-core/README.md)
- [全局63个活跃上下文登记](benchmarks/active-groups.json)
- [实际构造方法与停止条件](docs/construction-method.md)
- [显式分支、具体见证与受保护证明目标](benchmarks/proof-interface/v1/README.md)
- [构造、修订、问题日志与严格成本口径](benchmarks/construction/PROTOCOL.md)
- [QCIP/QCP/OUTPUT 与网上源码选题审查](benchmarks/research/qcip-candidate-review.md)
- [16 份 C 程序整理用源码快照](benchmarks/source-material/README.md)
- [候选来源与许可登记](benchmarks/sources.md)
- [ICML 2027 论文初稿](paper/main.tex)

尚未具体化的候选家族仍是设计提案；已具体化四家族的状态、来源与改动单独记录。具体实现已加入也不表示其目标已证明或已具备评测发布条件。

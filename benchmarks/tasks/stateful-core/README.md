# 多层调用与状态历史任务

本批新增三组、六个语义上下文、十八个平台实例。每组固定V0参考、V1替代和V2保留变异，分别提供Lean、原生Rocq和C/CompCert实现。最终关系命题在构造阶段保持未证明。

| 实现组 | 固定正向实现对 | 状态与多层调用 | 保留反例差异 |
|---|---|---|---|
| incremental-frame-stream | 线性残留缓冲 / 环形存储 | feed→drain→checksum→peek；跨块残留、错误和重置 | 空feed错误丢弃未完成帧 |
| nested-transaction-store | 映射快照栈 / 撤销日志及savepoint | execute→rollback→undo_to→restore→write_slot | 内层commit丢弃外层rollback仍需要的日志 |
| intrusive-lru-cache | MRU顺序表 / 复用节点的索引双向链表 | execute→put→evict→erase→detach | get命中未更新访问顺序 |

这些任务的完整行为跨越多条操作，涉及错误后的状态、嵌套事务和后续淘汰。域不排除无活动事务回滚、不完整输入、缓存未命中、容量为零或缩容。公开的最小比较边界没有独立的正确输出函数；行为由固定实现表达。难度标记L3–L4暂定，调用层数不是证明难度的替代指标。

详细布局、错误与六题目标见[TASKS.md](TASKS.md)。[groups.json](groups.json)绑定实现、域、观察和目标hash；[compcert/build.json](compcert/build.json)绑定九个实际AST与工具指纹。[call-graphs.json](call-graphs.json)从这些AST提取直接调用：分帧器最长4条调用边，事务日志版和链表缓存最长5条，均有完整callee体。这是语法可达调用链，不是运行时栈采样；本版各程序仍在一个翻译单元中。

```sh
python3 scripts/construction/stateful_action.py scripts/construction/prepare_stateful.py
python3 scripts/construction/build_stateful.py
python3 scripts/construction/run_stateful.py --smoke
python3 scripts/construction/run_stateful.py
python3 scripts/construction/stateful_action.py scripts/construction/audit_stateful_calls.py
python3 scripts/construction/prepare_stateful_targets.py
python3 scripts/construction/check_stateful_contract.py
```

准备命令仅供构造端使用，冻结后的模型不得重写注册表或实现。差分每个唯一输入执行三变体×C/Lean/抽取Rocq，共九次行为求值，并单独检查Lean/Rocq域谓词和传输非法邻界输入。C由GCC+ASan/UBSan执行；Clight做AST与目标类型检查，不冒充Clight语义差分。

三组各有10,000次固定种子随机生成尝试，加小域穷举、边界、64步压力轨迹；分帧器还枚举短帧的全部切块方式并插入空块。去重后数量和随机尝试数分开报告。报告统计实际观察到的错误、深度上限、嵌套提交、淘汰等事件，不只报告输入数量。事件计数是多标签的操作/输出事件，不等于独立输入数，也不是全面语义覆盖。

最终选定证据共109965个唯一输入、989685次行为求值、219984次域判断，无意外差异，三组变异均有区分输入。分帧器另有3805个与主语料不重叠的确定性补充输入，增加2592次同feed多帧输出事件；见`evidence/frames-multiframe.json`。补充复用相同驱动，仅替换语料提供函数，明确绑定该提供器hash；主报告逐字节恢复，原始成功证据不被覆盖。初次补充因遗漏reset-after-error事件未过覆盖门槛，原报告与成本已保留，增加重置恢复用例后通过。`summary-stateful-v0.5.json`对两份语料的交集做空集检查；冒烟/失败/重试不扩大唯一覆盖数。

实现均为本仓库新编写的有界私有API，无外部I/O、动态分配或隐藏callee，没有复制其他benchmark的功能规约或证明。C中参考缓存用可变数组，替代缓存用结构体arena内的前驱/后继索引；原生版分别使用不可变序列和索引节点。跨平台测试一致不是形式化精化证明。

构造与失败成本按组记一次，共享模型usage单独记在`batch-stateful-v0.5.json`。prepare、构建、测试和主要审计命令均有计量包装；编辑、初始脚手架等剩余开销只计入共享请求墙钟，无法观测的CPU/RSS及远端推理内存保持未知，不补零。Lean初稿类型错误和调用图工具语法错误有失败日志、快照、修订与后续检查记录。

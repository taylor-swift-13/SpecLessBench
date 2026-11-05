# 三平台实现组与构造记录（v0.2）

当前4组、12个语义任务已各有Lean、原生Rocq、C/CompCert版本，共36个平台实例；不扩充为36个独立任务家族。全部最终命题留待证明。总目录54个上下文仍有其余候选未具体化，它们同样必须满足三平台要求，不能以历史R-/C-前缀豁免。

当前全库另新增基础算法六组，活跃计数以`benchmarks/active-groups.json`为准。**提交接受目标以[proof-interface](../../proof-interface/README.md)为准**：显式选择等价分支或带具体输入/观察的反例分支。旧裸逻辑析取声明和模板不单独计分，避免非构造性逻辑证明绕过实际比较。

| 实现组 | 4个变体 | 3个语义上下文 |
|---|---|---|
| qcip-bst-delete | 前驱删除、后继删除、旋转下推、漏value复制 | SUCCESSOR、ROTATE、VALUE |
| qcip-avl-insert | 递归、祖先栈、旋转调用分解、丢中间子树 | STACK、FACTOR、MIDDLE |
| qcip-xizi-ring | 双段复制、字节复制、count表示、混淆满空 | COPY、REP、FULL |
| qcip-dijkstra | 有序队列、扫描、二叉堆、冻结首次距离 | SCAN、HEAP、SEEN |

## 实现与目标

- [lean/Native.lean](lean/Native.lean)：16个由固定style选择的原生实现；[lean/Domain.lean](lean/Domain.lean)定义输入域/编码；[lean/Goals.lean](lean/Goals.lean)的12个预期分支和12个公开析取命题均已类型检查。`lean/pending/*.lean.goal`是待填theorem模板，故意不提供`sorry`或公理。
- [rocq_native/Native.v](rocq_native/Native.v)：16个原生实现；[rocq_native/Goals.v](rocq_native/Goals.v)提供12个预期分支与公开析取目标，以`Abort`保留未证明状态。Coq/Rocq8.20.1检查了定义/命题类型；提取的OCaml用于差分，不冒充命题证明。
- C入口仍为`bst/avl/ring/dijkstra/v0..v3.c`，派生来源和观察见[TASKS.md](TASKS.md)。v0.2的真实CompCert导出记录以[compcert/manifest.json](compcert/manifest.json)为准；v0.1的3.16规划与旧`rocq/`文件保留为历史记录。
- [three-platform.json](three-platform.json)将每个上下文绑定到三平台版本、目标和成本组。它与C初版`tasks.json`分开，避免静默改写旧证据。

原生版使用结构化树和列表，而C版使用指针/数组arena；BST的前驱/后继选择与旋转策略保留，但控制流和函数调用结构不逐行等同。每个平台单独记录实现风格，不能把C的循环/内存难度直接赋给原生版。部分递归使用显式fuel，耗尽返回失败；目标要求双方成功，两个失败不能构成等价。跨语言观察一致性当前只经测试，没有形式化精化证明。

## 差分设计和实测

每个输入运行四个变体、三个可执行平台，即12次。比较V0/V1/V2组内观察及每个Vj的跨语言观察。刻意保留V3的差异，记录见证而不修复成等价版本。C端使用GCC+ASan/UBSan执行，**不是CompCert解释器或Clight语义执行**。

| 组 | 随机输入 | 小域穷举 | 边界/种子 | 总输入 | 程序执行 |
|---|---:|---:|---:|---:|---:|
| BST | 5000 | 4144 | 3 | 9147 | 109764 |
| AVL | 5000 | 820 | 5 | 5825 | 69900 |
| Ring | 5000 | 3111 | 7 | 8118 | 97416 |
| Dijkstra | 5000 | 2187 | 5 | 7192 | 86304 |
| 合计 | 20000 | 10262 | 20 | **30282** | **363384** |

当前这些输入上无意外正向差异或跨语言差异；四个负例变体都有区分输入。没有反例不证明等价。穷举仅覆盖脚本声明的小域：BST三键短轨迹、AVL三键/两值短轨迹、容量1–2的二值字节短轨迹、三顶点非自环边可缺失或权0/1的图。其余完整有效域没有穷举。

[evidence/](evidence/)保存分组报告，带种子、精确语料hash和源registry hash；压缩语料和运行输出保留在报告所指的`_build`目录。执行数指实现求值次数，不是独立数据集样本数，也不是证明数。首次BST smoke和历史2640次C-only检查单独记录，不混入上表。

## 构造修订和成本

构造模型可修改实现并修改任务；发布后求解模型只编辑证明。修改前用`revise.py begin`保存源码快照，修改后`commit`记录新revision和受影响任务，然后更新绑定并重测。故意不等价版本的见证保留，意外错误的修复前输入/输出同样保留。

[构造协议](../../construction/PROTOCOL.md)定义口径；[summary.json](../../construction/summary.json)汇总四组；`construction/groups/*.json`各组只有一份记录，覆盖全部变体/平台/任务。编译与测试的所有尝试含失败记录在`commands.jsonl`，问题在`issues.jsonl`，源码修订在`revisions.jsonl`。

token来自当前会话provider实际usage，作为共享batch只记一次；无法准确拆分到组时不均摊冒充精确值。工具时间采用单调时钟，内存为GNU time内核报告的**最大单进程RSS**。并发进程树总峰值、远端模型推理显存和历史未埋点成本均明确未知。当前会话usage还需要回合结束后补采最后事件，不能将前缀说成最终总量。

## 重现（WSL仓库根目录）

```sh
python3 scripts/construction/build_three_platform.py
python3 scripts/construction/measure.py --group qcip-bst-delete --phase full-differential-construction --role envelope -- python3 scripts/construction/differential.py --family bst --random-cases 5000
# 其他组替换 --group 与 --family；不运行任务证明。
python3 scripts/construction/export_compcert.py
python3 scripts/construction/summarize.py
```

构造工具当前定位本机已装Lean4.34.0、原生Rocq8.20.1及已有FIVE CompCert3.17/Rocq9.2环境。16个实际AST及所有CompCert目标已导出并类型检查通过；不存在以参数代替实现的空位。二进制、架构及导出hash以manifest为准；完整可移植依赖锁定与solver任务包隔离仍需继续完成。最终目标证明不属于当前构造完成条件。

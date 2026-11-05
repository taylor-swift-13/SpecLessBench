# 边界语义与数据结构任务

本批新增八组、16个语义上下文、48个平台实例，每组固定V0参考、V1替代、V2保留变异。每个上下文都有Lean、原生Rocq和C/CompCert定义及待证明命题；本阶段不提供最终证明。

重点是**难以完整另写一份功能规约的行为**：字节格式、错误优先级、失败位置、部分结果和短路求值。错误内容留在输入域中；输入前提只限制传输布局、资源范围与结构安全。阶乘等数学任务仍是对照，不能据此声称其声明式规约难写。

| 组 | V0 / V1 | V2差异 | 暂定证明难度 |
|---|---|---|---|
| pointer-tree-mirror | 指针树递归 / 显式栈 | 漏访一个子树 | L3 |
| union-find-connectivity | 完整路径压缩 / 路径减半 | find只前进一层 | L3 |
| max-priority-queue | 最大堆 / 有序数组 | 下沉时不选择较大孩子 | L3 |
| tagged-evaluator | 按需求值并记忆 / 节点拓扑序DP | 短路前传播右侧错误 | L4，待校准 |
| binary-tlv-decoder | 索引循环 / 剩余后缀递归 | 16位字段字节序颠倒 | L3，待校准 |
| quoted-tokenizer | 逐字节状态机 / 普通字节跨度快路径 | 丢失空引号词元 | L2–L3 |
| packbits-decoder | 索引循环 / 剩余后缀递归 | 重复计数少1 | L3，待校准 |
| lexical-path-normalizer | 从左到右组件栈 / 从右到左待抵消计数 | 错消相邻父目录 | L3 |

V1解析器与V0共享具体的单记录/单块处理函数。这些是受保护程序体，不是预先承诺的功能契约；其控制流差异小于求值器和表示替换任务，不能把所有行都当作同等难度。C用真实指针或可变数组，原生版用不可变列表/索引节点；跨平台执行一致不是形式化精化证明。

完整布局、观察、错误约定与16个具体目标见[TASKS.md](TASKS.md)。注册表[groups.json](groups.json)绑定源码与目标hash，[compcert/build.json](compcert/build.json)绑定24个真实AST与工具指纹。规范提交接口是[显式分支接口](../../proof-interface/README.md)，新增目标在三个平台的`BoundaryTargets`模块。

```sh
python3 scripts/construction/prepare_boundaries.py
python3 scripts/construction/build_boundaries.py
python3 scripts/construction/run_boundaries.py --smoke
python3 scripts/construction/run_boundaries.py
python3 scripts/construction/prepare_boundary_targets.py
```

`prepare_boundaries.py`只用于整理端重新生成注册表；冻结后不得在求解沙箱运行。差分测试每个唯一输入执行三变体×三平台，另执行Lean/Rocq域谓词审计。C使用GCC及ASan/UBSan；Clight完成AST/目标类型检查，未做语义解释执行。完整报告在`evidence/<family>.json`，确定性压缩语料在报告引用的`_build`路径；报告单列随机尝试、去重、小域穷举、域判断、负例见证与错误类别覆盖。

本批实现为仓库内新编写，TREE/UF/PQ/EVAL沿用既有QCIP选题线索和公共算法思想，未声称为QCIP原程序的验证。四个格式/路径任务使用明确的私有有界接口，不声称符合POSIX shell、文件系统路径或完整外部格式标准。没有继承源系统的功能规约或参考证明。问题和修订追加到`benchmarks/construction`，每组只记一份成本，共享模型usage在`batch-boundaries-v0.4.json`记一次；未知历史/远端指标保持null。

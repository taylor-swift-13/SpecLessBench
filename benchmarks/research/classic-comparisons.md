# 经典算法多实现：来源与任务筛选

状态更新：全源最短路、强连通分量和坏字符字符串搜索已在 [graphsuite-core](../tasks/graphsuite-core/README.md) 落地为三平台任务，稳定插入／计数排序已在 [countsort-core](../tasks/countsort-core/README.md) 落地；最终命题尚未证明。下方筛查记录保留为构造历史，其他条目仍是候选。现有库有单源 Dijkstra、朴素匹配与 KMP、并查集连接性、Prim/Kruskal、插入/归并/选择排序；下表避免把这些已有实现简单换个名字重复计数。

| 优先 | 比较 | 执行方式差异 | 固定输入与可观察结果（候选） | 反例变异与辨识度 |
| --- | --- | --- | --- | --- |
| 高 | Floyd–Warshall / 逐源 Dijkstra | 按允许的中间顶点做三重动态规划 / 按源点反复贪心松弛 | 有向简单图、非负整数边权，允许零边、断连；观察每对顶点的距离或不可达；不观察路径 | 把零边误当作无边；需分别覆盖零权路径、并列距离、不可达 |
| 高 | 朴素匹配 / Boyer–Moore 坏字符规则 | 左到右逐位试探 / 右到左比较并跳跃 | 有界字节文本与模式；观察首次匹配位置，空模式返回 0、不存在返回 -1 | 错误地按模式长度跳跃可能跨过匹配；是现有 KMP 家族的**新实现**，划入同一切分家族 |
| 高 | Tarjan / Kosaraju–Sharir 强连通分量 | 单次 DFS 的发现序号与 lowlink / 反图与两次 DFS | 有向图；观察顶点对是否同一分量，可附分量数；不比较实现分配的分量编号 | 省略反图边或错误传播 lowlink；含自环、孤点、多条跨分量边 |
| 高 | Edmonds–Karp / Dinic 最大流 | 最短增广路 / 层次网络和阻塞流 | 固定源汇、非负整数容量、容量有界；观察最大流值；不要求边流量逐项相同 | 漏掉残量反向边；包括必须回退先前流量的网络 |
| 中 | 稳定归并 / 稳定计数排序 | 分治归并 / 有界 key 计数和稳定回填 | 小范围整数 key 与 payload；观察整个记录序列，含重复 key 的相对顺序 | 反向填充与前缀位置组合错误导致失稳；与现有排序共享划分家族 |
| 中 | 二叉堆 / 有序数组优先队列 | 堆序调整 / 顺序插入 | 固定 push、peek、pop 序列；观察返回与空队列状态，允许重复值 | 某子节点漏比较；注意相同优先级对象的 tie-breaking 是否可见 |
| 中 | 自顶向下 / 自底向上归并排序 | 递归拆分 / 迭代宽度倍增 | 有界 key/payload 序列，观察完整稳定输出 | 奇数长度或尾段合并漏元素；与排序家族一起划分 |
| 待细化 | Kahn / DFS 拓扑排序 | 入度队列 / 深度优先逆后序 | 只比较序列通常不成立：不同拓扑序均可能合法。须选择确定性共同输出、固定关系观察，或单独设计期望不等价任务 | 不可把不同有效顺序误标为 bug；该项暂不进入等式候选 |

各候选的假设和观察是评测接口，不构成额外提供给求解器的第三份功能规约。已落地的实现组有分别的 `equivalence`、`refutationAt` 类型、测试证据和成本记录；其他变异仍只是计划，不能把筛查当成已落实。

## 参考资料与来源边界

* Princeton Algorithms 4/e 同时提供 [Floyd–Warshall](https://algs4.cs.princeton.edu/code/edu/princeton/cs/algs4/FloydWarshall.java.html) 和 [逐源 Dijkstra](https://algs4.cs.princeton.edu/44sp/DijkstraAllPairsSP.java.html)。前者更一般地允许负边；此处比较域收窄到非负整数，以满足后者的前提。
* [Tarjan SCC 接口](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/TarjanSCC.html)列出 Kosaraju–Sharir 和 Gabow 作为相同 API 的其他实现。组件编号不宜直接比较。
* [字符串搜索说明](https://algs4.cs.princeton.edu/53substring/)区分朴素、KMP 和 Boyer–Moore；其中所列 Boyer–Moore 实现只使用坏字符规则，而非完整的强好后缀规则。
* [最大流资料](https://algs4.cs.princeton.edu/64maxflow/)提供 Edmonds–Karp 规则实现与输入来源。实际引入程序或数据前，必须固定版本并核查对应许可证。此次仅记录出处，没有复制这些第三方实现或数据；筛查脚本是新写的 Python 原型。

## 本轮可复现筛查

执行 `python3 scripts/research/classic_candidate_probe.py graph` 或 `string`。前者穷举三顶点有向图上每条非自环边为不存在、0、1 或 2 的组合，再以固定种子生成 10,000 个随机输入；去重后 11,749 个。Floyd–Warshall 与逐源 Dijkstra 的输出无差异；忽略零权边的变异在 9,214 个输入上不同。

后者穷举二值文本（长度 0–6）和模式（长度 0–4），并加 10,000 次随机生成；去重后 13,883 个。朴素匹配与坏字符跳跃实现无差异；固定按模式长度跳跃的变异在 782 个输入上不同，如文本 `[0,0,1]`、模式 `[0,1]` 的正确首次匹配位置为 1，而变异返回 -1。

测试脚本、固定种子、输入序列哈希、结果、运行时间和单进程峰值 RSS 分别记录在 [graph.json](classic-probes/graph.json) 和 [string.json](classic-probes/string.json)；成本另按候选组记录于 `benchmarks/construction/groups/`。这些是有限输入的 Python 筛查，既不证明算法正确，也不能说明 Lean、Rocq、C 或 Clight 实现一致。

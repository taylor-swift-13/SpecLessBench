# Construction protocol v0.2

Historical command stdout, stderr, and timing files are stored in `command-logs.tar.gz` instead of thousands of separate files. The archive contains the original repository-relative paths; its SHA-256 is in `command-logs.sha256`. Verify it with `python3 scripts/construction/verify_log_archive.py`. To inspect an individual file, use `tar -xOf benchmarks/construction/command-logs.tar.gz <original-path>`; to restore all files locally, use `tar -xzf benchmarks/construction/command-logs.tar.gz`. New instrumented commands may create additional files under `logs/`.

每一个实现组必须提供 **Lean、原生 Rocq、C/CompCert** 三种实现版本。组是成本、修订和数据划分的单位；从同组派生多个实现对或平台实例，不重复计算构造成本。四家族的12个语义上下文将对应36个平台实例，而不是36个独立程序家族。

构造期允许模型运行差分测试、发现并最小化反例、修改实现／域／观察／目标。每次修改记录旧新hash、原因、受影响实例和重测证据，提升组revision，废弃旧标签与证据，不能静默替换。冻结后求解模型仍只能修改证明区域。刻意保留的不等价实现可形成负例任务；意外错误可以修复，但原见证和失败成本必须保留。

最终目标固定为三平台各自的“全域等价或存在反例”。原生实现若采用显式fuel，耗尽必须返回失败；等价分支必须要求两边都成功返回相同观察，不能用 `None=None` 通过。CompCert继续要求安全终止的Clight执行。平台移植是否保持语义目前只做多语言差分检查，不冒充跨语言形式化证明。

**构造阶段不要求证明最终命题。** 构造完成的必要条件为：具体实现、有效输入、观察、类型正确的目标、可运行差分入口、完整来源/修订/问题日志，以及规定覆盖下的测试和成本证据。此状态称construction-ready，与拥有参考证明的reference-ready不同。既有要求“每题入库前必须参考证明”在本阶段暂停；后续是否要求证明门槛需单独设定，不能把当前标签说成经内核确认。

差分测试不是决定程序等价的算法。没有反例仅产生provisionally-equivalent标签；发现差异则记录有效输入和实际输出。证明真假最终由冻结实现及其观察决定，不由生成者指定标签决定。非等价目标可保留，求解者应证明反例分支。

**接受接口修订：**不能仅提交裸`Eq ∨ Cex : Prop`证明；它可能被经典逻辑非构造性地证明而不完成比较。必须显式选择分支，反例输入和观察为可序列化的具体值，proof类型专门化到这些值。该设计问题、修订和目标类型检查记录在`PROP-DISJUNCTION-ESCAPE`及[proof-interface/v1](../proof-interface/v1/README.md)。实现未变化，既有差分无需重跑；接受契约的类型和前端须重新检查。

## 严格成本口径

- 一组一个汇总文件，内部列全部尝试、失败、修复、构建和测试，不按任务对或平台重复收费。
- 被埋点的外部命令记录 UTC 开始/结束、单调时钟耗时、完整 argv、退出码、stdout/stderr 文件、源码 revision、CPU user/system 时间及内核报告的最大进程 RSS；历史或临时命令若未埋点，单独标记缺口，不推算或补零。
- `max_process_rss_bytes` 明确定义为该命令及被wait回收后代中**单进程高水位的最大值**；它不是并发进程树RSS之和。另可采样进程树总RSS，须注明采样间隔和可能漏峰，不能冒充精确总峰值。本WSL没有可写的专用cgroup，因此精确进程树总峰值记null。
- 本地编译/测试内存和远端模型推理内存分别记录；后者平台未提供就记null，不估算显存。
- token只使用provider回报的usage事件，不用字符数估算。区分输入、缓存输入、输出和reasoning；reasoning是输出子集，不重复求和。
- 共享的一次模型构造会话成本在batch记一次，各组引用；缺少可靠组内归属时组token必须为null，不能均摊后称精确。一组独立模型run才可直接计入该组。所有失败调用同样计入。
- 当前chat回合结束前只能取得usage前缀；保留`usage_complete_through`与incomplete状态，后续snapshot收齐末尾，不把未收齐的数称最终总量。
- 历史未埋点的token、时间和内存峰值明确未知。启动计量前的环境探索也记录为缺口。禁止补0、编造总数或用多次命令峰值相加。

`batch-three-platform-v0.2.json`保存共享token快照；`groups/*.json`每组一份成本汇总；`events.jsonl`和`issues.jsonl`保存追加事件。快照只保存usage字段及源日志前缀hash，不复制对话正文或凭据。

本轮可启动一次性的`close_usage.py`本地收尾采集器：观察当前请求的final消息后，采集其后且下一用户请求前的provider usage事件，最长等待5分钟。若没有无歧义的末尾事件，继续标记incomplete；不编造完整总量。采集器自身的CPU、墙钟和Windows内核工作集峰值另外记录在batch，不混入WSL或推理内存。

后续批次使用独立batch文件（例如`batch-algorithms-v0.3.json`），不得重用旧批次baseline或把两次请求usage重复收费。`measure`读取环境中的batch/revision标识；同组汇总保持唯一。全局`summary.json`合并各批次，原QCIP报告保留在`summary-qcip-v0.2.json`。实际执行流程见[construction-method.md](../../docs/construction-method.md)。早期收尾采集器未能观测到final，故旧usage明确保持incomplete，当前不把该前缀宣称为完整账单。

## 项目级总账及论文更新

`total-cost.json` 是按项目汇总的机器可读总账，使用 `python3 scripts/construction/summarize_total_cost.py` 刷新；`summarize_all.py` 也会刷新它。该脚本收集所有已有 batch（含构造研究与成本审计），对同一会话中有重叠的 provider 累计计数区间合并后再求差；请求时间窗口和所有有记录的命令窗口分别取区间并集，避免把并发和嵌套命令的墙钟时间重复计算。不同会话的 provider token 独立汇总；缓存输入和推理输出是对应总量的子集，不再相加。脚本记录源 batch 哈希、区间、截止时间和缺失状态，遇到计数不一致则失败，不猜测数值。

项目级内存只取所有有记录命令的最大单进程 RSS 高水位，绝不将不同命令峰值相加；并发进程树峰值和远端推理内存没有可靠计量时为 null。请求窗口包含思考、等待和可能的空闲，不等于 CPU 时间、人时或整个历史构造持续时间；provider 窗口也可能包含无法单独归属的同一对话工作。因此现阶段仅能报告**已观察部分**，不能把它称为完整或精确的总成本。

pilot 评分原型另使用用户级 systemd scope：对每个有完整遥测的合成作业记录 cgroup v2 `memory.peak`、CPU 计数和资源限制，日志为 `pilot-jobs.jsonl`。这个作业级峰值覆盖监督进程与该沙箱后代到进程退出、最终清理之前，不能替代早期整个构造过程的进程树峰值或远端模型内存；总账分别保存两种指标，不混为同一个值。

后续每次构造开始前先建立独立 batch 并为工具命令设置对应 batch/revision；记录构造期失败、修复和探索，同一实现组只保存一次成本。阶段结束后刷新各 batch 快照、各组及 `summary.json`，运行 `summarize_total_cost.py` 和 `update_paper_total_cost.py`，并编译论文。最终冻结时在有明确截止点后收集可用的 post-turn usage、复核所有批次覆盖区间与遗漏，标明仍不可获得的内存／历史成本；不得仅因已到论文截稿就把缺口记为零。

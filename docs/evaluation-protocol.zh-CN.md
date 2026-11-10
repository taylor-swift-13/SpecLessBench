# SpecLessBench 评测指令（中文版）

状态：启动 Lean 与 Rocq 的 Goal 开／关比较，模型统一为 gpt-6-luna medium。69 个任务上下文、2 平台、2 模式，共 276 次独立运行；每次限时 2 小时、3 GiB，严格串行。CompCert 暂停，其 4 小时失败尝试完整保留并封存。

同一道定理先不开 Goal，再在全新会话与工作目录开启原生 Goal。两组初始任务说明、平台接口、工具和评分器相同。不开 Goal 只执行一次普通回合；开 Goal 通过真实 API 创建持久目标，由原生调度器继续，不由外部脚本发送“继续”，没有 10 轮手动重试机制。

每个运行都保存独立 report、全部可获取的对话和工具/RPC事件、目标与原始提交、评分审计及成本。Goal 自报完成不等于证明通过。超时也保存已观测的原生回合数和最后 Goal 状态。

## 任务 prompt

你需要判断给定的两个固定实现是否具有相同的可观察行为，并提交机器可检查的证明。任务文件位于只读目录 `/task`，你的工作目录是 `/work`。

任务文件定义输入域、观察结果和目标定理。请选择一个结论：

- 等价：证明两个实现对所有合法输入产生任务规定的相同行为。
- 不等价：给出一个具体合法输入，证明两个实现的观察结果不同。

将选择写入 `/work/claim.json`：

```json
{"claim":"equivalence"}
```

或：

```json
{"claim":"counterexample","input":[...],"left":[...],"right":[...]}
```

反例字段必须是字面整数列表，并遵守下方的平台接口。将证明写入指定的 Submission 文件，提供名为 `solve`、类型与所选目标一致的完整定理。你可以增加辅助定义和引理，证明方法不限。

实现、合法输入条件、观察语义和目标定理不可修改。证明不能包含未证明的占位符或自行引入的公理。测试可以帮助寻找反例，但提交的结论必须有形式化证明。

评分器独立检查提交文件、目标类型和公理依赖；全部通过才判为成功。

运行配置：总时间预算 `{budget_seconds}` 秒，包括 agent 工作与独立评分。外部控制器不发送手动续跑，不设置原来的 10 轮尝试上限。

## 平台接口（每次只发送当前平台）

### Lean

- 读取 `/task/Task.lean`。
- 提交 `/work/Submission.lean`，导入 `Task`，定义 `Submission.solve`。
- 等价目标为 `Task.equivalent`；反例目标为 `Task.refutationAt <input> <left> <right>`。
- 反例的 left/right 是 `some` 中完整的 Words，包含开头的载荷长度。
- 本地编译：`LEAN_PATH=/task:/work lean /work/Submission.lean`。
- 不允许 `sorry` 和候选程序自行引入的公理；评分器允许 Lean 标准的 `propext`、`Classical.choice`、`Quot.sound`。

### Rocq

- 读取 `/task/Task.v`。
- 提交 `/work/Submission.v`，导入 `From Trusted Require Import Task.`，定义顶层定理 `solve`，不要再包裹 `Module Submission`。
- 等价目标为 `Task.equivalent`；反例目标为 `Task.refutationAt <input> <left> <right>`。
- 反例的 left/right 是 `Some` 中完整的 Words，包含开头的载荷长度。
- 本地编译：`coqc -Q /task Trusted -Q /work Candidate /work/Submission.v`。
- 不允许 `Admitted`、`admit` 或候选程序自行引入的公理；最终证明还须通过独立的 `coqchk` 检查与公理审计。

### CompCert / Clight

- C 源码为 `/task/Left.c`、`Right.c`；权威 Clight AST 为 `Left.v`、`Right.v`。`Task.v` 和 `Execution.v` 定义目标与执行语义。
- 提交 `/work/Submission.v`，导入 `From Trusted Require Import Task Execution Left Right.`，定义顶层定理 `solve`。
- 等价目标为 `Task.equivalent`，包含任务规定的安全性、终止性及观察结果要求。
- 反例 claim 的 input 是未填充的输入；left/right 包含长度槽和有效载荷。评分器分别补零至 8192 个字，并与主函数返回值 0 配对。相应定理为：

```coq
Task.refutationAt input
  (0%Z, left ++ repeat 0%Z (8192 - left_length))
  (0%Z, right ++ repeat 0%Z (8192 - right_length))
```

- 使用字面列表及其实际长度。完整输出缓冲区是现有任务语义的一部分。
- 可以使用函数模型，但必须证明它与原有 Clight 执行语义的对应关系。
- 本地编译：`coqc -Q /task Trusted -Q /work Candidate /work/Submission.v`。
- 不允许 `Admitted`、`admit` 或候选程序自行引入的公理；允许评分器白名单中的 CompCert 标准假设，仍需独立检查及公理审计。

## Goal 状态与记录

原生 Goal 通过 thread/goal/set 设置，并用 thread/goal/get 确认；不是把 /goal 作为普通文字发送。两组均在独立工作目录和全新会话运行，不能共享尝试或参考答案。Goal 内部回合数只作为观测指标记录，不与外部手动重试混淆。

记录 Goal 开关、目标原文、API 确认、生命周期、原生回合数、客户端 turn/start 数、模型配置、实际任务 prompt 和哈希、工具调用、原始提交、评分及公理审计。成本使用最后一个会话累计 token 快照；原生目标的 tokensUsed 与模型 token 事件都保留，不重复相加。金额和服务端模型内存未知时为空。

当前单题探针在首轮结束后若原生调度 120 秒无续跑，则标记 native-continuation-not-observed；这只是验证运行机制的停滞状态，不是定理不可证的结论。

## 2026-11-10 原生计算判定修正

以上接口文字保留原始冻结 prompt。按用户要求，评分策略修订为
`lean-native-kernel-replay-v1`：`native_decide` 产生的封闭计算事实可以由宿主
内核独立验证后解除依赖，不再仅因其生成了额外公理名而判失败。名字本身不能证明
该事实来自官方 tactic，也不能作为放行依据；伪造的错误事实、`sorry`、任意未解除
的公理和错误目标仍拒绝。复核资源不足单独记为未完成，不等于数学结论错误。

历史原始提交、报告、prompt、校验和和模型成本不变；新判定存入独立版本目录，
每次尝试只选择一个权威结果参与聚合，宿主复核成本另列。详见
[原生计算复核说明](native-computation-audit.md)。

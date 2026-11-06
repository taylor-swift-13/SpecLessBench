# SpecLessBench 评测指令（中文版）

状态：此前运行产物已清空。取消外部 10 轮手动续跑，拟比较同一模型开启原生 Goal 和不开 Goal。单题 CompCert Goal 探针已在 4 小时上限结束，45 个原生回合、1067 次工具命令，未完成 solve。尚未启动全量实验或不开 Goal 的对照，结果见 goal-probe.md。

两组使用相同任务说明、平台接口、工具、输入域、目标和时间预算。不开 Goal 只执行一次普通回合；开 Goal 创建持久目标，由原生调度器决定后续回合，不由外部脚本发送“继续”。原生目标状态和独立评分结果分别记录。Goal 自报完成不等于证明通过。

当前探针使用 gpt-6-luna medium，CompCert 限时 4 小时，3 GiB 沙箱。客户端只发送一次 turn/start，原始 RPC、Goal 状态和所有后续原生回合均记录。后续全量比较的启动取决于这次单题试验，不提前扩大运行范围。

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

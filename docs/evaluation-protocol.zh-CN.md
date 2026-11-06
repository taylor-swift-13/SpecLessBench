# SpecLessBench 评测指令（中文版）

状态：只使用普通版 baseline，严格串行运行 207 个平台实例。强化版及其产物已删除。每次最多总计 10 轮（首次加 9 次同会话续跑）；Lean/Rocq 限时 2 小时，CompCert 限时 4 小时，包含检查。

实际发送给模型的英文原文统一维护在 `scripts/pilot/evaluation_prompts.py`，修订日期为 `2026-11-06`。下列任务说明和平台接口保留完整验收标准。

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

运行配置：总时间预算 `{budget_seconds}` 秒，最多 `{max_rounds}` 轮。时间由控制器统一计量，包括 agent 工作与评分检查；续跑沿用同一会话和工作目录。

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

## 续跑消息

所有条件使用同一份结构化检查反馈，避免把额外提示混入对照：

```text
本轮评分结果：{result}
剩余共享时间：{remaining_seconds} 秒
剩余轮数：{remaining_rounds}
检查日志：
{checker_output}
```

控制器负责是否启动下一轮。反馈不透露预期分支、其他题目或参考证明。

## 记录

历史验证已清空。当前保留普通版新实验的通过结果，不复用已删除的历史证明。每个 attempt 的 config.json 和 report.json 在 configuration.prompt_protocol 中记录 baseline、修订日期、语言、初始提示哈希与组成部分哈希。prompt-components.json 保存原文；每轮另存实际 prompt.txt 和 round_prompt_sha256。模型配置、续跑策略、提交、检查记录及成本各自保留。

10 轮是统一实验预算，不保证每题都能在其中完成。当前两个普通版成功样本分别用了 7 轮和 2 轮，CompCert 尚无完整新样本。按通过、轮数上限和时间上限分别统计停止原因；触及轮数上限时记录剩余时间。需要增加轮数时开展独立补充实验，不混入主实验。

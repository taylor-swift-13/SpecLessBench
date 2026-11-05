# SpecLessBench pilot v1：冻结与发布状态

这是一份 **71 个语义上下文、30 个切分家族、213 个平台实例**的冻结源码快照。完整阶乘家族已划为公开金标准参考，不进入测试集；[evaluation-policy.json](evaluation-policy.json) 从冻结清单排除该家族，剩余 69 个上下文、29 个家族和 207 个平台实例。它还不是可交付求解器的正式评测包。

## 快照和复现

冻结时记录了 472 个受保护任务／目标文件的哈希，另以独立 addendum 绑定输入校验器、构建配置、注册表、构建脚本和编译器可执行文件。原始源码和构建支持共 591 个文件的快照位于 WSL 私有目录中的 `frozen-sources.tar.gz`，受 `manifest.json` 的哈希约束。工具可执行文件有哈希，但完整标准库、系统和内核尚未锁定。

私有材料位于 WSL 的 `~/.local/share/speclessbench/pilot-v1/`，目录权限为 `0700`，文件权限为 `0600`；其中包含原题映射、随机 secret、冻结源码和可能暴露标签的日志。Windows 挂载目录上的 `chmod` 不能作为 Unix 私有权限保证，因此不把映射留在仓库目录。**必须由整理方自行安全备份该 WSL 目录**；不要将它挂载到求解器，也不要把它推送到公开仓库。丢失 secret 或映射后，不能从匿名 ID 恢复已冻结的对应关系。

在 WSL 的既有工具链环境中执行：

```bash
python3 scripts/pilot/verify_freeze.py
python3 scripts/pilot/verify_archive.py
python3 scripts/pilot/verify_audit.py
```

第一项检查当前工作区的冻结任务文件；日后如工作区继续修改而触发失败，应使用备份的冻结源码与新工作区，不要修改 pilot 来追随工作区。其余检查验证私有归档和审计证据。

## Single-run evaluation

`scripts/pilot/run_evaluation.py` runs one prepared theorem with a fresh offline sandbox and writes a private report. At present, only the prepared Lean factorial equivalence task is supported. The agent executable must already be available inside the sandbox (under `/usr` or the selected toolchain); network access is disabled. The runner does not include an online-model or agent-specific adapter.

For the existing WSL installation, `scripts/pilot/run_codex_wsl.py` is a preliminary Codex-specific integration for that same theorem: it requests `gpt-6-luna` with medium reasoning and a 3,600-second agent limit. The Codex process has network access for the model; its tool subprocesses use a second sandbox with network disabled and authentication-file access denied. A local isolation probe checked those boundaries, but this is not a complete hostile-code security audit. The runner requires the pinned local Codex and Lean paths and an already authenticated WSL account. Reports and model-generated proofs remain in the private WSL runs directory.

Provide a JSON configuration containing an argv array; `{prompt}` is replaced with the fixed task prompt. For example, replace the command below with an installed offline agent that implements the protocol:

```json
{
  "agent": {
    "name": "my-agent",
    "version": "1.0",
    "model_provider": "local",
    "model_name": "my-model",
    "model_version": "pinned-version",
    "command": ["/usr/bin/my-agent", "--jsonl", "{prompt}"]
  },
  "limits": {"wall_seconds": 120}
}
```

```bash
python3 scripts/pilot/prepare_factorial.py
python3 scripts/pilot/run_evaluation.py \
  --task P-dbec465c356ed73d --platform lean --claim equivalence --reference \
  --config /path/to/agent-config.json
```

The agent sees the task at `/trusted`, has a new `/work`, and must produce `/work/Submission.lean` with `Submission.solve : Obligation.goal`. Emit JSON objects, one per stdout line, for messages, tool calls and tool results. A `session_end` event may state `transcript_complete: true`; the runner records this as an agent claim, not an independently verified guarantee. The agent must emit every interaction it wants recorded: the runner cannot recover hidden reasoning or omitted tool calls. A single `usage` event with `scope: "run_total"` can report `input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_output_tokens`, and `total_tokens`. These are self-reported, not provider-verified. Optional `pricing` config may provide `input_usd_per_million`, `cached_input_usd_per_million`, `output_usd_per_million`, and `version`; the resulting estimate is not a bill.

Each run is written under `~/.local/share/speclessbench/runs/` by default, with `report.json`, `report.md`, the original and parsed configuration, prompt, raw stdout/stderr, `events.jsonl`, submission if present, checker trace, and resource data. Logs can contain proofs, task answers, and sensitive data: use a private WSL filesystem and do not put credentials in arguments or configuration. The sandbox output limit is 128 MiB per stream; timeouts, missing output, truncated logs, unreported usage, and absent model metadata are reported as such. No automatic redaction can guarantee that an agent will not emit secrets.

To generate an example report without a model, use `--config scripts/pilot/example-agent.json` in the command above. The synthetic agent submits `sorry`, so the expected result is `rejected` and the CLI exits with status 1. Test the report pipeline and proof-bypass checks with `python3 scripts/pilot/test_run_evaluation.py` and `python3 scripts/pilot/test_grade_sealed.py`. These use fake agents and toy propositions; they do not run a model evaluation or prove benchmark goals.

## 三平台检查

在不改动冻结源的独立副本中，已重新执行三平台构建；103 个重新导出的 Clight AST 与冻结版本逐字节一致。71 个上下文的正反分支接口在 Lean、Rocq 和 CompCert 工具链中重新通过类型检查。结果见 `platform-audit.json`、`ast-audit.json` 和 `interface-audit.json`，具体构建日志放在 WSL 私有目录的 `audit-logs/`。

另外针对全部 213 个平台实例，生成并检查了 213 个等价目标类型和 213 个带字面量输入的反例目标类型；见 `obligation-audit.json`。反例目标检查使用任意合法探针输入和人为构造的不同观察值，它们不代表有效反例。24 份编译日志保存在私有的 `obligation-logs/`。

这些检查不是最终题目证明，也不证明三个平台版本相互精化；CompCert 的 Clight 语义仍未做逐任务执行或最终证明。

## 隔离与泄漏：尚未达到发布条件

`leak-audit.json` 记录了旧任务编号和共享源码中的显式提示风险。新索引本身不暴露原题号，但**中性编号不是完整的防泄漏求解包**：共享源码中还有 `mutant` 等提示、其他版本的分支和原符号；原仓库公开历史也已存在。真正发布前必须逐题裁剪和匿名化模型可见内容、验证其绑定到原目标，并独立复核泄漏。

`scripts/pilot/sandbox.py` 是评分边界原型：使用 bubblewrap 的文件系统／网络／进程命名空间和用户级 systemd cgroup，设置资源上限，并记录作业级内存峰值。`grader-prototype.json` 仅记录玩具命题测试：正常证明、`sorry`／`Admitted`、额外公理、错误目标及文件／网络／资源限制等。它尚未接入真实题目的可信封装；Rocq 假设检查输出、加载器和对抗场景仍需审计，且共享主机内核并非完整虚拟机安全边界。

The sealed grader checks task packages against trusted hashes and starts each run in a fresh sandbox. Lean permits `propext`, `Classical.choice` and `Quot.sound`; native Rocq requires a closed proof. CompCert permits assumptions in the fully qualified `compcert` namespace and the explicitly named Rocq library dependencies in `rocq_grader_core.py`. Submission-defined and other assumptions are rejected. The task, digest and target must be selected by the trusted evaluator, not the agent. Adversarial review of this prototype remains open.

`test_single_task_runner.py` 检查其他目录、前次运行及题目篡改隔离；`test_grade_sealed.py` 对三个工具链测试接受合法证明和拒绝未完成证明、额外公理、篡改目标包；`test_attempt_to_grade.py` 测试从沙箱输出到 Lean 评分的完整链路。这些测试使用玩具命题。

The Lean factorial equivalence and fixed-witness counterexample references use isolated packages. `test_real_factorial.py` and `test_factorial_cex.py` check rejection of `sorry`, extra axioms, and incorrect goals. Reference scoring requires `--reference`. Both factorial Rocq goals and both CompCert goals have also been checked against rebuilt frozen sources, with `coqchk` and assumption audits. The CompCert checks use the documented trusted-library assumptions and bytecode conversion. See [reference reports](../reports/README.md) for proof status and replay commands.

2026-11-05 的原型测试继续向 `benchmarks/construction/pilot-jobs.jsonl` 记录沙箱作业的 cgroup 资源；本次外层命令没有逐条加入早期的命令计时器，因此总命令时间仍不完整。`pilot-freeze-v0.12` 的 token 快照覆盖了两次用户请求，时间窗口包括两次请求之间的等待，不能当作实际工作时长。

因此 `scripts/pilot/release_gate.py` 对其余未封装题目返回 `unavailable`，不会给出成功分数。构造和审计成本在 `benchmarks/construction/` 单独保留，不虚报为完整历史成本。

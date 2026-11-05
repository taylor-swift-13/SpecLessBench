# 显式分支与具体见证的证明接口 v1

**此接口取代旧的“仅提交`Eq ∨ Cex : Prop`证明”的接受方式。** 原有实现、输入域和观察未改变，旧析取声明/模板作为设计历史保留，不再是可单独计分的提交目标。

原因是：对两个总函数，经典逻辑可以非构造性地推出“全域相等或存在不同输入”，却不实际选择可检查的行为结论或给出具体输入。只接受这个析取的证明会偏离benchmark目标。该问题记录为`PROP-DISJUNCTION-ESCAPE`，没有通过证明实际任务来演示它。

现在要求JSON提交显式且字面量的`claim`：

- `equivalence`：proof常量必须直接具有该固定实现对的全域等价类型。
- `counterexample`：提交具体输入及两边的具体观察；受保护前端将JSON纯整数数据转换成Lean/Rocq值，proof必须具有**专门化到这些值**的有效输入、成功执行及观察不同的类型。不能用字符串程序、经典choice项或一个未给出见证的存在性证明代替输入。

每个上下文在三个平台都有等价与具体反例两种目标类型，整理端预期极性独立保存。`manifest.json` 登记 71 个上下文，新增的 `CountSortTargets` 包含两个上下文。目标定义已通过类型检查，最终命题保持待证明。具体见证和非法请求的检查统计见 `validation.json`。

```json
{
  "context_id": "R-FAC-CEX",
  "platform": "lean",
  "claim": "counterexample",
  "proof_module": "Submission",
  "proof_theorem": "solve",
  "input": [1],
  "left_observation": {"return": 0, "payload": [1]},
  "right_observation": {"return": 0, "payload": [0]}
}
```

此例的ID是整理端名称，发布仍须中性重命名并去掉标签。`payload`没有长度头；保护前端生成长度，并为CompCert观察补齐输出数组。输入始终是有限的JSON整数／列表／规定字段对象，不允许嵌入代码。原生版目标要求`Some`成功结果；CompCert目标要求合法初始输入和安全有限执行，不能通过两个失败来完成。

`scripts/construction/submission_contract.py`验证提交并生成：

1. `Obligation`：受保护的具体目标定义，不含证明；
2. `Gate`：要求`Submission.solve`的类型就是该目标。

单独的析取证明不能满足Gate的分支类型。该前端和义务生成已有回归检查；没有提供Submission证明，也没有运行最终任务求解。**完整的solver隔离、允许公理审计和评测发布器仍未完成**，不能把这里当作已发布的完整grader。

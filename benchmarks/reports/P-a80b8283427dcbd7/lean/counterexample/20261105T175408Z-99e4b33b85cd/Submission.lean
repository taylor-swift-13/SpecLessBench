import Obligation

theorem Submission.solve : Obligation.goal := by
  unfold Obligation.goal Task.refutationAt Task.valid
  decide

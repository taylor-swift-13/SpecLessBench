import Obligation

namespace Submission

def solve : Obligation.goal := by
  unfold Obligation.goal Task.refutationAt Task.valid Task.a Task.b
  decide

end Submission

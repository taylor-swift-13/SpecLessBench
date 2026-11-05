import Obligation

namespace Submission

private theorem factorialAcc_eq (n : Nat) (a : Int) :
    Task.factorialAcc n a = a * Task.factorialRec n := by
  induction n generalizing a with
  | zero => simp [Task.factorialAcc, Task.factorialRec]
  | succ n ih =>
      simp [Task.factorialAcc, ih, Task.factorialRec]
      ac_rfl

theorem solve : Obligation.goal := by
  intro x _
  refine ⟨Task.finish [Task.factorialRec (Task.iz x 0).toNat], ?_, ?_⟩
  · simp [Task.a]
  · simp [Task.b, factorialAcc_eq]

end Submission

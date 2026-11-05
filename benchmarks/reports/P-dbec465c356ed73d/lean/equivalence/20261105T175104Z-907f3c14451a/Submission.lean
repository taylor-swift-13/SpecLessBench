import Obligation

namespace Submission

theorem factorialAcc_eq (n : Nat) (a : Int) :
    Task.factorialAcc n a = a * Task.factorialRec n := by
  induction n generalizing a with
  | zero => simp [Task.factorialAcc, Task.factorialRec]
  | succ n ih =>
    simp only [Task.factorialAcc, Task.factorialRec, ih]
    exact Int.mul_assoc _ _ _

theorem solve : Obligation.goal := by
  intro x _
  refine ⟨Task.finish [Task.factorialRec (Task.iz x 0).toNat], rfl, ?_⟩
  simp [Task.b, factorialAcc_eq]

end Submission

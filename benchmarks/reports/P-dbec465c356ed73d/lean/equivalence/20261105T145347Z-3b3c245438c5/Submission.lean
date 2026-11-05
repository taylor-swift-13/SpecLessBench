import Obligation

namespace Submission

private theorem factorialAcc_eq (n : Nat) (a : Int) :
    Task.factorialAcc n a = Task.factorialRec n * a := by
  induction n generalizing a with
  | zero => simp [Task.factorialAcc, Task.factorialRec]
  | succ n ih =>
      rw [Task.factorialAcc, ih, Task.factorialRec]
      simp [Int.mul_assoc, Int.mul_comm, Int.mul_left_comm]

theorem solve : Obligation.goal := by
  intro x _
  refine ⟨Task.finish [Task.factorialRec (Task.iz x 0).toNat], ?_, ?_⟩
  · rfl
  · simp [Task.b, Task.a, factorialAcc_eq]

end Submission

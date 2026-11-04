From Coq Require Import Lists.List.
Require Import Common.

Lemma reverse_acc_correct :
  forall (A : Type) (xs acc : list A),
    reverse_acc xs acc = reverse_ref xs ++ acc.
Proof.
  intros A xs. induction xs as [|x rest IH]; intros acc; simpl.
  - reflexivity.
  - rewrite IH. rewrite <- app_assoc. reflexivity.
Qed.

Theorem reverse_certificate :
  forall (A : Type),
    outcome (fun _ : list A => True) (@eq (list A))
      reverse_ref reverse_candidate.
Proof.
  intros A. left. intros xs _. unfold reverse_candidate.
  rewrite reverse_acc_correct. simpl. rewrite app_nil_r. reflexivity.
Qed.

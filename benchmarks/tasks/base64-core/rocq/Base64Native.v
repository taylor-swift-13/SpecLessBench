From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words := list Z.
Definition get (xs : words) i := nth i xs 0%Z.
Definition alphabet x : Z :=
 if Nat.ltb x 26 then Z.of_nat (65+x) else if Nat.ltb x 52 then Z.of_nat (97+x-26)
 else if Nat.ltb x 62 then Z.of_nat (48+x-52) else if Nat.eqb x 62 then 43%Z else 47%Z.
Fixpoint blocks fuel bytes : option words :=
 match bytes with
 | [] => Some []
 | a::tail => match fuel with
   | O => None
   | S f => let b:=nth 0 tail 0 in let c:=nth 1 tail 0 in
     match blocks f (skipn 2 tail) with
     | None => None
     | Some rest => Some ([alphabet (a/4); alphabet ((a mod 4)*16+b/16);
        if Nat.eqb (length tail) 0 then 61%Z else alphabet ((b mod 16)*4+c/64);
        if Nat.ltb (length tail) 2 then 61%Z else alphabet (c mod 64)]++rest)
     end end
 end.
Fixpoint emit_sextets fuel buffer bits out :=
 match fuel with
 | O => (buffer,bits,out)
 | S f => if Nat.ltb bits 6 then (buffer,bits,out) else
    let remaining:=bits-6 in let divisor:=2^remaining in
    emit_sextets f (buffer mod divisor) remaining (out++[alphabet (buffer/divisor)])
 end.
Definition stream style bytes :=
 let '(buffer,bits,out):=fold_left (fun state b =>
   let '(buffer,bits,out):=state in emit_sextets 3 (buffer*256+b) (bits+8) out)
   bytes (0,0,([]:words)) in
 let out:=if Nat.eqb bits 0 then out else out++[alphabet (buffer*2^(6-bits))] in
 let padding:=(4-length out mod 4) mod 4 in
 out++repeat 61%Z (if Nat.eqb style 2 then Nat.min padding 1 else padding).
Definition entry (_family style:nat) xs : option words :=
 let bytes:=map Z.to_nat (firstn (Z.to_nat (get xs 0)) (skipn 1 xs)) in
 let out:=if Nat.eqb style 0 then blocks 64 bytes else Some (stream style bytes) in
 match out with None=>None|Some out=>Some (Z.of_nat (length out)::out) end.
Definition Equivalent (valid:words->Prop) (a b:words->option words) :=
 forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition RefutationAt (valid:words->Prop) (a b:words->option words) x oa ob :=
 valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.

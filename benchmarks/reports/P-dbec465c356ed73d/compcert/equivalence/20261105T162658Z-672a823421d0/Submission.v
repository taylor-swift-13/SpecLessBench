From Trusted Require Import Obligation.
From Trusted Require Import Execution BasicDomain FACTORIAL_V0 FACTORIAL_V1.
From Stdlib Require Import List ZArith Lia.
From compcert Require Import Coqlib Maps Integers AST Values Memory Events Globalenvs Smallstep Ctypes Cop Clight.
Import ListNotations.
Open Scope Z_scope.
Local Transparent Mem.alloc Mem.free Mem.store Mem.load Mem.storebytes Mem.loadbytes.

Definition rangeb m b lo hi k p := forallb
 (fun i => if Mem.perm_dec m b (lo+Z.of_nat i) k p then true else false)
 (seq 0 (Z.to_nat (hi-lo))).
Lemma rangeb_correct : forall m b lo hi k p, rangeb m b lo hi k p = true <-> Mem.range_perm m b lo hi k p.
Proof.
 intros. unfold rangeb. rewrite forallb_forall. split.
 - intros H ofs B. specialize (H (Z.to_nat (ofs-lo))).
   assert (lo + Z.of_nat (Z.to_nat (ofs-lo)) = ofs) by (rewrite Z2Nat.id by lia; lia).
   assert (In (Z.to_nat (ofs-lo)) (seq 0 (Z.to_nat (hi-lo)))) by (apply in_seq; split; [lia|lia]).
   specialize (H H1). rewrite H0 in H. destruct (Mem.perm_dec m b ofs k p); congruence.
 - intros H i I. apply in_seq in I. destruct (Mem.perm_dec m b (lo+Z.of_nat i) k p); auto. exfalso; apply n; apply H; lia.
Qed.
Definition crange m b lo hi k p : {Mem.range_perm m b lo hi k p}+{~Mem.range_perm m b lo hi k p}.
Proof. destruct (rangeb m b lo hi k p) eqn:B; [left|right]; [apply rangeb_correct; auto|intro H; apply rangeb_correct in H; congruence]. Defined.
Ltac replace_fun body old new :=
 let z := eval pattern old in body in
 lazymatch z with ?f old => exact (f new) end.
Definition cvalid := ltac:(let z := eval unfold Mem.valid_access_dec in Mem.valid_access_dec in replace_fun z Mem.range_perm_dec crange).
Definition cstore := ltac:(let z := eval unfold Mem.store in Mem.store in replace_fun z Mem.valid_access_dec cvalid).
Lemma cstore_eq : forall ch m b o v, cstore ch m b o v = Mem.store ch m b o v.
Proof.
 intros. unfold cstore, Mem.store. destruct (cvalid m ch b o Writable), (Mem.valid_access_dec m ch b o Writable); try contradiction; try reflexivity.
Qed.
Definition cload := ltac:(let z := eval unfold Mem.load in Mem.load in replace_fun z Mem.valid_access_dec cvalid).
Lemma cload_eq : forall ch m b o, cload ch m b o = Mem.load ch m b o.
Proof. intros. unfold cload, Mem.load. destruct (cvalid m ch b o Readable), (Mem.valid_access_dec m ch b o Readable); try contradiction; reflexivity. Qed.
Definition cdrop := ltac:(let z := eval unfold Mem.drop_perm in Mem.drop_perm in replace_fun z Mem.range_perm_dec crange).
Lemma cdrop_eq : forall m b lo hi p, cdrop m b lo hi p = Mem.drop_perm m b lo hi p.
Proof.
 intros. unfold cdrop, Mem.drop_perm. destruct (crange m b lo hi Cur Freeable), (Mem.range_perm_dec m b lo hi Cur Freeable); try contradiction; try reflexivity.
 f_equal. apply Mem.mkmem_ext; reflexivity.
Qed.
Fixpoint zeros (n:nat) m b o : option mem :=
 match n with O => Some m | S n => match cstore Mint8unsigned m b o Vzero with Some m' => zeros n m' b (o+1) | None => None end end.
Lemma zeros_eq : forall n m b o, zeros n m b o = store_zeros m b o (Z.of_nat n).
Proof.
 induction n; intros; rewrite store_zeros_equation; simpl.
 - destruct (zle 0 0); auto; lia.
 - destruct (zle (Z.pos (Pos.of_succ_nat n)) 0); try lia.
   rewrite cstore_eq. destruct (Mem.store Mint8unsigned m b o Vzero); auto.
   change (zeros n m0 b (o+1) = store_zeros m0 b (o+1) (Z.of_nat (S n)-1)). rewrite IHn. f_equal; lia.
Qed.
Definition czeros m b o n := zeros (Z.to_nat n) m b o.
Lemma czeros_eq : forall m b o n, czeros m b o n = store_zeros m b o n.
Proof.
 intros m b o n. unfold czeros. rewrite zeros_eq.
 destruct (zle 0 n).
 - rewrite Z2Nat.id by lia. reflexivity.
 - replace (Z.to_nat n) with O by lia. simpl. rewrite (store_zeros_equation m b o n), (store_zeros_equation m b o 0). simpl. destruct (zle n 0); auto; lia.
Qed.
Definition cdata := ltac:(let z := eval unfold Genv.store_init_data in (@Genv.store_init_data fundef type) in replace_fun z Mem.store cstore).
Lemma cdata_eq : forall ge m b o d, cdata ge m b o d = Genv.store_init_data ge m b o d.
Proof. intros; destruct d; simpl; try rewrite cstore_eq; auto. destruct (Genv.find_symbol ge i); auto. apply cstore_eq. Qed.
Fixpoint cdatalist ge m b o ds := match ds with
 | [] => Some m | d::ds => match cdata ge m b o d with Some m' => cdatalist ge m' b (o+init_data_size d) ds | None => None end end.
Lemma cdatalist_eq : forall ds ge m b o, cdatalist ge m b o ds = Genv.store_init_data_list ge m b o ds.
Proof. induction ds; intros; simpl; auto. rewrite cdata_eq. destruct (Genv.store_init_data ge m b o a); auto. Qed.
Definition cglobal (ge:Genv.t fundef type) m (g:ident * globdef fundef type) :=
 match snd g with
 | Gfun _ => let (m',b) := Mem.alloc m 0 1 in cdrop m' b 0 1 Nonempty
 | Gvar v => let sz := init_data_list_size (gvar_init v) in
   let (m',b) := Mem.alloc m 0 sz in
   match czeros m' b 0 sz with
   | Some m' => match cdatalist ge m' b 0 (gvar_init v) with
       | Some m' => cdrop m' b 0 sz (Genv.perm_globvar v) | None => None end
   | None => None end
 end.
Lemma cglobal_eq : forall ge m g, cglobal ge m g = Genv.alloc_global ge m g.
Proof.
 intros ge m [id [f|v]]; unfold cglobal, Genv.alloc_global; cbn -[Mem.alloc czeros cdrop cdatalist Genv.store_init_data_list store_zeros].
 - destruct (Mem.alloc m 0 1) as [m' b]. apply cdrop_eq.
 - destruct (Mem.alloc m 0 (init_data_list_size (gvar_init v))) as [m' b]. rewrite czeros_eq.
   destruct (store_zeros _ _ _ _); auto. rewrite cdatalist_eq. destruct (Genv.store_init_data_list _ _ _ _ _); auto. apply cdrop_eq.
Qed.
Fixpoint cglobals ge m gs := match gs with [] => Some m | g::gs => match cglobal ge m g with Some m' => cglobals ge m' gs | None => None end end.
Lemma cglobals_eq : forall gs ge m, cglobals ge m gs = Genv.alloc_globals ge m gs.
Proof. induction gs; intros; simpl; auto. rewrite cglobal_eq. destruct (Genv.alloc_global ge m a); auto. Qed.
Definition cinit (p:AST.program fundef type) := cglobals (Genv.globalenv p) Mem.empty (AST.prog_defs p).
Lemma cinit_eq : forall p, cinit p = Genv.init_mem p.
Proof. intros; apply cglobals_eq. Qed.
Definition cstorev ch m addr v := match addr with
 | Vptr b o => if zle (Ptrofs.unsigned o + size_chunk ch) Ptrofs.modulus then cstore ch m b (Ptrofs.unsigned o) v else None
 | _ => None end.
Lemma cstorev_eq : forall ch m addr v, cstorev ch m addr v = Mem.storev ch m addr v.
Proof. intros. unfold cstorev, Mem.storev. destruct addr; auto. rewrite cstore_eq. reflexivity. Qed.
Definition cloadv ch m addr := match addr with
 | Vptr b o => if zle (Ptrofs.unsigned o + size_chunk ch) Ptrofs.modulus then cload ch m b (Ptrofs.unsigned o) else None
 | _ => None end.
Lemma cloadv_eq : forall ch m addr, cloadv ch m addr = Mem.loadv ch m addr.
Proof. intros. unfold cloadv, Mem.loadv. destruct addr; auto. rewrite cload_eq. reflexivity. Qed.
Definition rd (ty:type) (m:mem) (b:block) (o:ptrofs) : option val :=
 match access_mode ty with
 | By_value ch => cloadv ch m (Vptr b o)
 | By_reference | By_copy => Some (Vptr b o)
 | _ => None end.
Definition loc (ge:genv) (e:env) (id:ident) (ty:type) : option block :=
 match PTree.get id e with Some (b,t) => if type_eq t ty then Some b else None | None => Genv.find_symbol ge id end.
Fixpoint ev (ge:genv) (e:env) (le:temp_env) (m:mem) (a:expr) : option val :=
 match a with
 | Econst_int i _ => Some (Vint i)
 | Etempvar id _ => PTree.get id le
 | Evar id ty => match loc ge e id ty with Some b => rd ty m b Ptrofs.zero | _ => None end
 | Ederef a ty => match ev ge e le m a with Some (Vptr b o) => rd ty m b o | _ => None end
 | Eunop op a _ => match ev ge e le m a with Some v => sem_unary_operation op v (typeof a) m | _ => None end
 | Ebinop op a b _ => match ev ge e le m a, ev ge e le m b with Some v,Some w => sem_binary_operation ge op v (typeof a) w (typeof b) m | _,_ => None end
 | Ecast a ty => match ev ge e le m a with Some v => sem_cast v (typeof a) ty m | _ => None end
 | _ => None end.
Definition lv (ge:genv) (e:env) (le:temp_env) (m:mem) (a:expr) : option (block * ptrofs) :=
 match a with
 | Evar id ty => match loc ge e id ty with Some b => Some (b,Ptrofs.zero) | _ => None end
 | Ederef a _ => match ev ge e le m a with Some (Vptr b o) => Some (b,o) | _ => None end
 | _ => None end.

Ltac split_match := match goal with
 | H: context [match ?x with _ => _ end] |- _ => destruct x eqn:?; try discriminate
 end.
Lemma rd_sound : forall ty m b o v, rd ty m b o = Some v -> deref_loc ty m b o Full v.
Proof. intros. unfold rd in H. destruct (access_mode ty) eqn:A; rewrite ?cloadv_eq in H; try discriminate; inversion H; subst; eauto using deref_loc_value, deref_loc_reference, deref_loc_copy. Qed.
Lemma loc_sound : forall ge e id ty b, loc ge e id ty = Some b -> eval_lvalue ge e (PTree.empty val) Mem.empty (Evar id ty) b Ptrofs.zero Full.
Proof. intros. unfold loc in H. destruct (PTree.get id e) as [[bb tt]|] eqn:E; repeat split_match; inversion H; subst; [eapply eval_Evar_local|eapply eval_Evar_global]; eauto. Qed.
Lemma ev_sound : forall ge e le m a v, ev ge e le m a = Some v -> eval_expr ge e le m a v.
Proof.
 intros ge e le m a; induction a; intros v H; simpl in H; try discriminate;
 repeat split_match; inversion H; subst; try (econstructor; eauto; fail).
 - eapply eval_Elvalue; [|eapply rd_sound; eauto].
   unfold loc in Heqo. destruct (PTree.get i e) as [[bb tt]|] eqn:E; repeat split_match; inversion Heqo; subst; eauto using eval_Evar_local, eval_Evar_global.
 - eapply eval_Elvalue; [econstructor; eauto|eapply rd_sound; eauto].
Qed.
Lemma lv_sound : forall ge e le m a b o, lv ge e le m a = Some (b,o) -> eval_lvalue ge e le m a b o Full.
Proof.
 intros. destruct a; simpl in H; try discriminate.
 - unfold loc in H. destruct (PTree.get i e) as [[bb tt]|] eqn:E.
   + repeat split_match. inversion H; subst; eapply eval_Evar_local; congruence.
   + destruct (Genv.find_symbol ge i) eqn:G; inversion H; subst; eapply eval_Evar_global; eauto.
 - destruct (ev ge e le m a) eqn:E; try discriminate. destruct v; inversion H; subst. constructor. eapply ev_sound; eauto.
Qed.
Lemma deref_det : forall ty m b o bf v w,
 deref_loc ty m b o bf v -> deref_loc ty m b o bf w -> v=w.
Proof.
 intros. inversion H; inversion H0; subst; try congruence.
 inversion H5; subst. inversion H1; inversion H4; subst; congruence.
Qed.
Lemma eval_det : forall ge e le m,
 (forall a v, eval_expr ge e le m a v -> forall w, eval_expr ge e le m a w -> v=w) /\
 (forall a b o bf, eval_lvalue ge e le m a b o bf -> forall b' o' bf', eval_lvalue ge e le m a b' o' bf' -> b=b' /\ o=o' /\ bf=bf').
Proof.
 intros. apply eval_expr_lvalue_ind; intros;
 match goal with
 | H: eval_lvalue _ _ _ _ _ _ _ _ |- _ /\ _ => inversion H; subst
 | H: eval_expr _ _ _ _ _ _ |- _ => inversion H; subst end;
 try congruence; try solve [repeat match goal with H:eval_lvalue _ _ _ _ (Econst_int _ _) _ _ _ |- _ => inversion H end].
all: repeat match goal with
 | H: eval_lvalue _ _ _ _ (Econst_int _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Econst_float _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Econst_single _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Econst_long _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Etempvar _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Eaddrof _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Eunop _ _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Ebinop _ _ _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Ecast _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Esizeof _ _) _ _ _ |- _ => inversion H
 | H: eval_lvalue _ _ _ _ (Ealignof _ _) _ _ _ |- _ => inversion H
 | IH: forall w, eval_expr ?g ?e ?l ?m ?a w -> ?v = w,
   E: eval_expr ?g ?e ?l ?m ?a ?w |- _ => let X := fresh in pose proof (IH _ E) as X; clear IH; inversion X; subst
 | IH: forall b o bf, eval_lvalue ?g ?e ?l ?m ?a b o bf -> _,
   E: eval_lvalue ?g ?e ?l ?m ?a ?b ?o ?bf |- _ => let X := fresh in pose proof (IH _ _ _ E) as X; clear IH; destruct X as [? [? ?]]; subst
 end; try congruence; try solve [repeat split; congruence]; try solve [eapply deref_det; eauto].
Qed.
Definition bind {A B} (x:option A) (f:A -> option B) := match x with Some a => f a | None => None end.
Notation "x <- a ;; b" := (bind a (fun x => b)) (at level 100, a at next level, right associativity).
Fixpoint args (ge:genv) e le m (al:list expr) (tl:list type) : option (list val) :=
 match al,tl with
 | [],[] => Some []
 | a::al,ty::tl => v <- ev ge e le m a ;; w <- sem_cast v (typeof a) ty m ;; vl <- args ge e le m al tl ;; Some (w::vl)
 | _,_ => None end.
Definition next (ge:genv) (s:state) : option state :=
 match s with
 | State f st k e le m =>
   match st with
   | Sset id a => v <- ev ge e le m a ;; Some (State f Sskip k e (PTree.set id v le) m)
   | Sassign a b => bo <- lv ge e le m a ;; v <- ev ge e le m b ;; w <- sem_cast v (typeof b) (typeof a) m ;;
     match access_mode (typeof a) with
     | By_value ch => m' <- cstorev ch m (Vptr (fst bo) (snd bo)) w ;; Some (State f Sskip k e le m')
     | _ => None end
   | Scall id a al =>
     match classify_fun (typeof a) with
     | fun_case_f tl tr cc => vf <- ev ge e le m a ;; vl <- args ge e le m al tl ;; fd <- Genv.find_funct ge vf ;;
       if type_eq (type_of_fundef fd) (Tfunction tl tr cc) then Some (Callstate fd vl (Kcall id f e le k) m) else None
     | _ => None end
   | Ssequence a b => Some (State f a (Kseq b k) e le m)
   | Sifthenelse a b c => v <- ev ge e le m a ;; test <- bool_val v (typeof a) m ;; Some (State f (if test then b else c) k e le m)
   | Sloop a b => Some (State f a (Kloop1 a b k) e le m)
   | Sskip => match k with
     | Kseq a k => Some (State f a k e le m)
     | Kloop1 a b k => Some (State f b (Kloop2 a b k) e le m)
     | Kloop2 a b k => Some (State f (Sloop a b) k e le m)
     | Kswitch k => Some (State f Sskip k e le m)
     | _ => m' <- Mem.free_list m (blocks_of_env ge e) ;; Some (Returnstate Vundef k m') end
   | Sbreak => match k with
     | Kseq a k => Some (State f Sbreak k e le m)
     | Kloop1 _ _ k | Kloop2 _ _ k | Kswitch k => Some (State f Sskip k e le m)
     | _ => None end
   | Sreturn a => m' <- Mem.free_list m (blocks_of_env ge e) ;;
     match a with
     | None => Some (Returnstate Vundef (call_cont k) m')
     | Some a => v <- ev ge e le m a ;; w <- sem_cast v (typeof a) (fn_return f) m ;; Some (Returnstate w (call_cont k) m') end
   | _ => None end
 | Callstate (Internal f) vl k m =>
   match fn_vars f with
   | [] =>
     if list_norepet_dec ident_eq (var_names (fn_params f)) then
     if list_disjoint_dec ident_eq (var_names (fn_params f)) (var_names (fn_temps f)) then
     le <- bind_parameter_temps (fn_params f) vl (create_undef_temps (fn_temps f)) ;;
     Some (State f (fn_body f) k empty_env le m)
     else None else None
   | _ => None end
 | Returnstate v (Kcall id f e le k) m => Some (State f Sskip k e (set_opttemp id v le) m)
 | _ => None end.
Lemma args_sound : forall ge e le m al tl vl, args ge e le m al tl = Some vl -> eval_exprlist ge e le m al tl vl.
Proof.
 intros ge e le m al; induction al; intros tl vl H; destruct tl; simpl in H; try discriminate.
 - inversion H; constructor.
 - unfold bind in H. repeat split_match. inversion H; subst. econstructor; eauto using ev_sound.
Qed.
Lemma next_sound : forall ge s s', next ge s = Some s' -> step2 ge s E0 s'.
Proof.
 intros ge s s' H. destruct s as [f st k e le m|fd vl k m|v k m]; simpl in H.
 - destruct st; simpl in H; rewrite ?cstorev_eq, ?cstore_eq in H; unfold bind in H; repeat split_match; inversion H; subst;
   try solve [econstructor; eauto using ev_sound, lv_sound, args_sound, assign_loc_value];
   try solve [apply step_skip_call; simpl; auto];
   try solve [apply step_skip_or_continue_loop1; auto];
   try solve [apply step_skip_break_switch; auto].
   + destruct p as [bb oo]. simpl in *. rewrite cstore_eq in Heqo2. eapply step_assign; eauto using lv_sound, ev_sound.
     eapply assign_loc_value; eauto. unfold Mem.storev. rewrite Heqs. exact Heqo2.
   + eapply step_ifthenelse with (b:=true); eauto using ev_sound.
   + eapply step_ifthenelse with (b:=false); eauto using ev_sound.
 - destruct fd; try discriminate. destruct (fn_vars f) eqn:V; try discriminate.
   unfold bind in H. repeat split_match. inversion H; subst. apply step_internal_function.
   econstructor; eauto. rewrite V; constructor. rewrite V; constructor.
 - destruct k; inversion H; subst. constructor.
Qed.
Lemma args_det : forall ge e le m al tl vl,
 eval_exprlist ge e le m al tl vl -> forall wl, eval_exprlist ge e le m al tl wl -> vl=wl.
Proof.
 intros ge e le m al tl vl H; induction H; intros wl W; inversion W; subst; auto.
 match goal with X:eval_expr _ _ _ _ a ?w |- _ => pose proof (proj1 (eval_det ge e le m) _ _ H _ X) end. subst. f_equal; eauto. congruence.
Qed.
Lemma next_unique : forall ge s u, next ge s = Some u -> forall t v, step2 ge s t v -> t=E0 /\ v=u.
Proof.
 intros ge s u N t v S. inversion S; subst;
 try match goal with D: _ = Sskip \/ _ = Scontinue |- _ => destruct D; subst end;
 try match goal with D: _ = Sskip \/ _ = Sbreak |- _ => destruct D; subst end;
 simpl in N; rewrite ?cstorev_eq, ?cstore_eq in N; unfold bind in N;
 try discriminate; repeat split_match; inversion N; subst; simpl in *; try match goal with E:cstore _ _ _ _ _ = _ |- _ => rewrite cstore_eq in E end; try contradiction;
 repeat match goal with
 | E: ev ?g ?e ?l ?m ?a = Some ?w, H: eval_expr ?g ?e ?l ?m ?a ?w' |- _ =>
   let Q := fresh in pose proof (proj1 (eval_det g e l m) _ _ (ev_sound _ _ _ _ _ _ E) _ H) as Q; clear H; inversion Q; subst
 | E: lv ?g ?e ?l ?m ?a = Some (?b,?o), H: eval_lvalue ?g ?e ?l ?m ?a ?b' ?o' ?bf |- _ =>
   let Q := fresh in pose proof (proj2 (eval_det g e l m) _ _ _ _ (lv_sound _ _ _ _ _ _ _ E) _ _ _ H) as Q; clear H; destruct Q as [? [? ?]]; subst
 | E: args ?g ?e ?l ?m ?al ?tl = Some ?vl, H: eval_exprlist ?g ?e ?l ?m ?al ?tl ?wl |- _ =>
   let Q := fresh in pose proof (args_det _ _ _ _ _ _ _ (args_sound _ _ _ _ _ _ _ E) _ H) as Q; clear H; subst
 end; try solve [split; congruence].
all: try match goal with E: lv _ _ _ _ _ = Some ?p |- _ => destruct p end.
all: repeat match goal with
 | E: lv ?g ?e ?l ?m ?a = Some (?b,?o), H: eval_lvalue ?g ?e ?l ?m ?a ?b' ?o' ?bf |- _ =>
   let Q := fresh in pose proof (proj2 (eval_det g e l m) _ _ _ _ (lv_sound _ _ _ _ _ _ _ E) _ _ _ H) as Q; clear H; destruct Q as [? [? ?]]; subst
 end.
all: try match goal with H:assign_loc _ _ _ _ _ _ _ _ |- _ => inversion H; subst; try congruence end.
all: try solve [split; congruence].
- assert (chunk=m0) by congruence. assert (v0=v1) by congruence. subst.
  unfold Mem.storev in H3. simpl in *. rewrite Heqs in H3. split; congruence.
- inversion H; subst. pose proof (args_det _ _ _ _ _ _ _ (args_sound _ _ _ _ _ _ _ Heqo0) _ H1). split; congruence.
- inversion H; subst. match goal with A:alloc_variables _ _ _ _ _ _ |- _ => rewrite Heql in A; inversion A; subst end. split; f_equal; congruence.
Qed.
Fixpoint finish (fuel:nat) (ge:genv) (s:state) : option (int * mem) :=
 match s with
 | Returnstate (Vint r) Kstop m => Some (r,m)
 | _ => match fuel with
        | O => None
        | S fuel => u <- next ge s ;; finish fuel ge u
        end
 end.
Inductive certified (ge:genv) : state -> Prop :=
| cert_done : forall r m, certified ge (Returnstate (Vint r) Kstop m)
| cert_next : forall s u, next ge s = Some u -> certified ge u -> certified ge s.
Lemma finish_correct : forall fuel ge s r m, finish fuel ge s = Some (r,m) ->
 certified ge s /\ star step2 ge s E0 (Returnstate (Vint r) Kstop m).
Proof.
 induction fuel; intros ge s r m H;
 destruct s as [f st k e le mm|fd vl k mm|v k mm];
 try destruct v; try destruct k; cbn -[next] in H;
 try discriminate; try solve [inversion H; subst; split; [constructor|constructor]].
 all: unfold bind in H; destruct (next ge _) eqn:N; try discriminate;
 destruct (IHfuel _ _ _ _ H) as [C T]; split; [econstructor; eauto|].
 all: eapply star_left; [eapply next_sound; eauto|exact T|reflexivity].
Qed.
Lemma certified_step : forall ge s, certified ge s -> forall t u, step2 ge s t u -> certified ge u.
Proof.
 intros ge s C t u S. inversion C; subst.
 - inversion S.
 - destruct (next_unique _ _ _ H _ _ S); subst; auto.
Qed.
Lemma certified_safe : forall p s, certified (globalenv p) s -> safe_from p s.
Proof.
 intros p s C u t T. assert (certified (globalenv p) u).
 { induction T; eauto using certified_step. }
 inversion H; subst.
 - left; eexists; constructor.
 - right. exists E0, u0. eapply next_sound; eauto.
Qed.
Fixpoint cwords m b o xs := match xs with [] => Some m | x::xs => match cstore Mint32 m b o (Vint (Int.repr x)) with Some m' => cwords m' b (o+4) xs | None => None end end.
Lemma cwords_eq : forall xs m b o, cwords m b o xs = store_words m b o xs.
Proof. induction xs; intros; simpl; auto. rewrite cstore_eq. destruct (Mem.store _ _ _ _ _); auto. Qed.
Fixpoint cloadwords n m b o := match n with O => Some [] | S n => match cload Mint32 m b o, cloadwords n m b (o+4) with Some (Vint i), Some xs => Some (Int.signed i::xs) | _,_ => None end end.
Lemma cloadwords_eq : forall n m b o, cloadwords n m b o = load_words n m b o.
Proof. induction n; intros; simpl; auto. rewrite cload_eq, IHn. reflexivity. Qed.
Definition coutput (p:program) id m := match Genv.find_symbol (globalenv p) id with Some b => cloadwords OutputWords m b 0 | None => None end.
Lemma coutput_eq : forall p id m, coutput p id m = output_words p id m.
Proof. intros. unfold coutput, output_words. destruct (Genv.find_symbol _ _); auto. apply cloadwords_eq. Qed.
Definition boot_compute (p:program) (id:ident) (xs:list Z) : option state :=
 m <- cinit p ;;
 b <- Genv.find_symbol (globalenv p) (prog_main p) ;;
 fd <- Genv.find_funct_ptr (globalenv p) b ;;
 if type_eq (type_of_fundef fd) (Tfunction [] type_int32s cc_default) then
 bi <- Genv.find_symbol (globalenv p) id ;;
 m' <- cwords m bi 0 xs ;; Some (Callstate fd [] Kstop m')
 else None.
Lemma boot_compute_sound : forall p id xs s, boot_compute p id xs = Some s -> boot p id xs s.
Proof.
 intros. unfold boot_compute, bind in H. rewrite cinit_eq in H. repeat split_match. match goal with E:cwords _ _ _ _ = _ |- _ => rewrite cwords_eq in E end. inversion H; subst.
 econstructor; eauto. econstructor; eauto.
Qed.
Definition check_run (fuel:nat) (p:implementation) (xs:list Z) : option observation :=
 s <- boot_compute (Execution.program p) (input_symbol p) xs ;;
 rm <- finish fuel (globalenv (Execution.program p)) s ;;
 ys <- coutput (Execution.program p) (output_symbol p) (snd rm) ;;
 Some (Int.signed (fst rm),ys).
Lemma check_run_sound : forall fuel p xs o, check_run fuel p xs = Some o -> run p xs o.
Proof.
 intros. unfold check_run, bind in H.
 destruct (boot_compute _ _ _) eqn:B; try discriminate.
 destruct (finish _ _ _) as [[r m]|] eqn:F; try discriminate.
 rewrite coutput_eq in H. destruct (output_words _ _ _) eqn:W; try discriminate. inversion H; subst.
 destruct (finish_correct _ _ _ _ _ F) as [C T].
 exists s,r,m,l. repeat split; eauto using boot_compute_sound, certified_safe.
Qed.
Definition out (n:Z) : observation := (0, 1 :: n :: repeat 0 8190).
Definition boot_from (p:program) m (id:ident) (xs:list Z) : option state :=
 b <- Genv.find_symbol (globalenv p) (prog_main p) ;;
 fd <- Genv.find_funct_ptr (globalenv p) b ;;
 if type_eq (type_of_fundef fd) (Tfunction [] type_int32s cc_default) then
 bi <- Genv.find_symbol (globalenv p) id ;;
 m' <- cwords m bi 0 xs ;; Some (Callstate fd [] Kstop m')
 else None.
Definition check_from fuel (p:implementation) m xs : option observation :=
 s <- boot_from (Execution.program p) m (input_symbol p) xs ;;
 rm <- finish fuel (globalenv (Execution.program p)) s ;;
 ys <- coutput (Execution.program p) (output_symbol p) (snd rm) ;;
 Some (Int.signed (fst rm),ys).
Lemma check_from_sound : forall fuel p m xs o,
 cinit (Execution.program p) = Some m -> check_from fuel p m xs = Some o -> run p xs o.
Proof.
 intros. apply (check_run_sound fuel). unfold check_run, boot_compute, bind. rewrite H.
 exact H0.
Qed.
Fixpoint fac (n:nat) : Z := match n with O => 1 | S k => Z.of_nat (S k) * fac k end.
Definition obs_dec (a b:observation) : {a=b}+{a<>b}.
Proof. decide equality; [apply list_eq_dec; apply Z.eq_dec|apply Z.eq_dec]. Defined.
Definition matches (x:option observation) (o:observation) :=
 match x with Some x => if obs_dec x o then true else false | None => false end.
Lemma matches_sound : forall x o, matches x o = true -> x = Some o.
Proof. intros [x|] o H; simpl in H; try discriminate. destruct (obs_dec x o); congruence. Qed.
Definition batch (fuel:nat) (p q:implementation) (ml mr:mem) : bool :=
 forallb (fun n : nat =>
 matches (check_from fuel p ml (BasicDomain.encode [Z.of_nat n])) (out (fac n)) &&
 matches (check_from fuel q mr (BasicDomain.encode [Z.of_nat n])) (out (fac n))) (seq 0 13).
Definition fuel : nat := 100000.
Definition paired (p q:implementation) : bool :=
 match cinit (Execution.program p) with
 | Some ml =>
   match cinit (Execution.program q) with
   | Some mr => batch fuel p q ml mr
   | None => false end
 | None => false end.
Definition all_checked : bool := paired Obligation.left_impl Obligation.right_impl.
Lemma concrete_checks : all_checked = true.
Proof. Time vm_compute. Time reflexivity. Time Qed.
Local Opaque cinit check_from.
Lemma paired_sound : forall p q, paired p q = true -> forall n, (n < 13)%nat ->
 run p (BasicDomain.encode [Z.of_nat n]) (out (fac n)) /\
 run q (BasicDomain.encode [Z.of_nat n]) (out (fac n)).
Proof.
 intros p q C n N. unfold paired in C.
 destruct (cinit (Execution.program p)) eqn:L; [|change (false = true) in C; discriminate].
 destruct (cinit (Execution.program q)) eqn:R; [|change (false = true) in C; discriminate].
 unfold batch in C. apply forallb_forall with (x:=n) in C; [|apply in_seq; lia].
 apply andb_prop in C. destruct C as [A B]. apply matches_sound in A. apply matches_sound in B.
 split; eapply check_from_sound; eauto.
Qed.
Lemma all_runs : forall n, (n < 13)%nat ->
 run Obligation.left_impl (BasicDomain.encode [Z.of_nat n]) (out (fac n)) /\
 run Obligation.right_impl (BasicDomain.encode [Z.of_nat n]) (out (fac n)).
Proof. apply paired_sound. exact concrete_checks. Qed.
Theorem solve : Obligation.goal.
Proof.
 unfold Obligation.goal, Equivalent. intros x V.
 unfold BasicDomain.valid, BasicDomain.validb in V.
 apply andb_prop in V. destruct V as [Len Range]. apply Nat.eqb_eq in Len.
 destruct x as [|a xs]; simpl in Len; try discriminate Len.
 destruct xs; simpl in Len; try discriminate Len.
 unfold BasicDomain.in_range, BasicDomain.get in Range; simpl in Range.
 apply andb_prop in Range. destruct Range as [Lo Hi].
 apply Z.leb_le in Lo. apply Z.leb_le in Hi.
 assert (A: Z.of_nat (Z.to_nat a) = a) by (apply Z2Nat.id; lia).
 exists (out (fac (Z.to_nat a))).
 assert (N: (Z.to_nat a < 13)%nat) by lia.
 pose proof (all_runs (Z.to_nat a) N) as T. rewrite A in T. exact T.
Qed.

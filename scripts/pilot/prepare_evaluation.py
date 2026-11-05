"""Prepare source-bound, single-pair evaluation packages (never gold proofs)."""
import json
import fcntl
import os
import re
import resource
import subprocess
import time
from pathlib import Path

from private_paths import PRIVATE
from selection import selection
from single_task_runner import tree_digest
from verify_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = Path.home()/'.local/share/speclessbench/packages'
LEAN = Path.home()/'.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean'
SOURCE = ROOT/'benchmarks/tasks/algorithms-core/lean'


def compile_lean(folder, name, paths):
    result = subprocess.run([str(LEAN), '-j', '1', '-o', str(folder/(name+'.olean')),
                             str(folder/(name+'.lean'))], cwd=folder,
                            env=dict(os.environ, LEAN_PATH=':'.join(map(str, paths))),
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(name+':\n'+result.stdout+result.stderr)
    return result.stdout+result.stderr


def definition(source, name):
    match = re.search(r'^def '+re.escape(name)+r'\b.*?(?=\n(?:def |end )|\Z)', source, re.M | re.S)
    if not match:
        raise ValueError('Missing frozen definition: '+name)
    return match.group().strip()+'\n'


def matrix_definition(name, style):
    header = f'''def {name} (xs : Words) : Words :=
  let r := (iz xs 0).toNat; let k := (iz xs 1).toNat; let c := (iz xs 2).toNat
'''
    if style == 1:
        return header+'''  (List.range r).foldl (fun out i =>
    (List.range k).foldl (fun out t => (List.range c).foldl (fun out j =>
      put out (i*c+j) (iz out (i*c+j)+iz xs (3+i*k+t)*iz xs (3+r*k+t*c+j))) out) out)
    (List.replicate (r*c) 0)
'''
    index = 'j*k+t' if style == 2 else 't*c+j'
    return header+f'''  (List.range (r*c)).map (fun pos =>
    let i := pos/c; let j := pos%c
    (List.range k).foldl (fun a t => a+iz xs (3+i*k+t)*iz xs (3+r*k+({index}))) 0)
'''


def prepare(row):
    """Native sequence/matrix adapters; other families remain pending."""
    ctx = row['context']; family = ctx.get('family_index')
    if ctx.get('tranche') != 'algorithms' or family not in (1, 2, 3):
        return None
    package = PACKAGES/row['pilot_id']/'lean'
    if (package/'registry.json').exists():
        meta = json.loads((package/'registry.json').read_text())
        if tree_digest(package/'task') != meta['public_sha256']:
            raise ValueError('Existing package changed: '+str(package))
        return meta
    started = time.monotonic()
    if package.exists():
        raise ValueError('Incomplete preparation needs inspection: '+str(package))
    task = package/'task'; binding = package/'binding'
    task.mkdir(parents=True, mode=0o700); binding.mkdir(mode=0o700)
    native = (SOURCE/'BasicNative.lean').read_text()
    targets = (ROOT/'benchmarks/proof-interface/lean/BranchTargets.lean').read_text()
    target = definition(targets, ctx['equivalence_goal'])
    styles = re.findall(r'SpecLessBenchBasic.entry '+str(family)+r' (\d+)', target)
    if styles[0] != '0' or len(styles) != 2 or styles[1] not in ('1', '2'):
        raise ValueError('Unsupported frozen pair')
    style = int(styles[1])
    names = {1: ('reverseRec', 'reverseAcc'), 2: ('sumRec', 'sumAcc'), 3: ()}[family]
    definitions = ''.join(definition(native, n) for n in ('iz', 'finish', *names))
    left = 'reverseRec data' if family == 1 else '[sumRec data]'
    right = ('reverseAcc data '+('[0]' if style == 2 else '[]')) if family == 1 else (
        '[sumAcc '+('(data.take (data.length-1))' if style == 2 else 'data')+' 0]')
    source = 'import Lean\nnamespace Task\nabbrev Words := List Int\n'+definitions+'''
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop :=
  (inRange (iz xs 0) 0 64 && xs.length == 1+(iz xs 0).toNat &&
   (xs.drop 1).all (fun v => inRange v (-1000000) 1000000)) = true
'''
    data_prefix = '  let data := (xs.drop 1).take (iz xs 0).toNat\n'
    if family == 3:
        source = 'import Lean\nnamespace Task\nabbrev Words := List Int\n'+definitions+definition(native, 'put')
        source += matrix_definition('matrixA', 0)+matrix_definition('matrixB', style)+'''
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def valid (xs : Words) : Prop :=
  (let a := iz xs 0; let b := iz xs 1; let c := iz xs 2
   let n := a.toNat; let m := b.toNat; let z := c.toNat
   inRange a 0 6 && inRange b 0 6 && inRange c 0 6 && xs.length == 3+n*m+m*z &&
     (xs.drop 3).all (fun v => inRange v (-1000) 1000)) = true
'''
        left, right, data_prefix = 'matrixA xs', 'matrixB xs', ''
    for name, expr in (('a', left), ('b', right)):
        source += f'def {name} (xs : Words) : Option Words :=\n'+data_prefix+f'  some (finish ({expr}))\n'
    source += '''def equivalent : Prop := ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def refutationAt (x oa ob : Words) : Prop := valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
end Task
'''
    (task/'Task.lean').write_text(source)
    (task/'Obligation.lean').write_text('import Task\nnamespace Obligation\ndef goal : Prop := Task.equivalent\nend Obligation\n')
    logs = [compile_lean(task, name, [task]) for name in ('Task', 'Obligation')]
    original = ROOT/'_build/pilot-v1/evaluation-binding'
    original.mkdir(parents=True, exist_ok=True)
    for name in ('BasicNative', 'BasicDomain'):
        path = original/(name+'.lean'); frozen = SOURCE/path.name
        if not path.exists() or path.read_bytes() != frozen.read_bytes() or not (original/(name+'.olean')).exists():
            path.write_bytes(frozen.read_bytes()); logs.append(compile_lean(original, name, [original]))
    helper = ''
    for name in names:
        acc = name.endswith('Acc')
        params = '(xs a : Task.Words)' if family == 1 and acc else ('(xs : Task.Words) (a : Int)' if acc else '(xs : Task.Words)')
        args = 'xs a' if acc else 'xs'
        helper += f'''theorem {name}_eq {params} : Task.{name} {args} = SpecLessBenchBasic.{name} {args} := by
  induction xs {'generalizing a' if acc else ''} with
  | nil => rfl
  | cons x xs ih => simp [Task.{name}, SpecLessBenchBasic.{name}, ih]
'''
    helper_names = ', '.join(n+'_eq' for n in names)
    for name, selected in (('a', 0), ('b', style)):
        if family == 3:
            helper += f'theorem {name}_eq (x : Task.Words) : Task.{name} x = SpecLessBenchBasic.entry {family} {selected} x := by rfl\n'
        else:
            helper += f'''theorem {name}_eq (x : Task.Words) : Task.{name} x = SpecLessBenchBasic.entry {family} {selected} x := by
  simp [Task.{name}, Task.finish, Task.iz, SpecLessBenchBasic.entry, SpecLessBenchBasic.finish, SpecLessBenchBasic.iz, {helper_names}]
'''
    helper += f'''theorem valid_eq : Task.valid = SpecLessBenchBasic.valid {family} := by funext x; rfl
example : Task.equivalent = SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid {family}) (SpecLessBenchBasic.entry {family} 0) (SpecLessBenchBasic.entry {family} {style}) := by
  unfold Task.equivalent SpecLessBenchBasic.Equivalent
  rw [valid_eq, funext a_eq, funext b_eq]
example (x oa ob : Task.Words) : Task.refutationAt x oa ob = (SpecLessBenchBasic.valid {family} x ∧ SpecLessBenchBasic.entry {family} 0 x = some oa ∧ SpecLessBenchBasic.entry {family} {style} x = some ob ∧ oa ≠ ob) := by
  unfold Task.refutationAt
  rw [valid_eq, a_eq x, b_eq x]
'''
    (binding/'Binding.lean').write_text('import BasicDomain\nimport Task\n'+helper)
    logs.append(compile_lean(binding, 'Binding', [task, original]))
    (binding/'compile.log').write_text('\n'.join(logs))
    meta = {'pilot_id': row['pilot_id'], 'platform': 'lean', 'public_sha256': tree_digest(task),
            'binding': 'lean-kernel-checked-correspondence-for-both-branches',
            'source_goal': ctx['equivalence_goal'], 'source_context': row['source_context_id'],
            'preparation_wall_seconds': time.monotonic()-started,
            'preparation_controller_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            'final_proof_attempted': False}
    (package/'registry.json').write_text(json.dumps(meta, indent=2)+'\n')
    return meta


def main():
    os.umask(0o077)
    PACKAGES.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (PACKAGES/'activity.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        verify_freeze()
        eligible = {r['pilot_id'] for r in selection()[0]}
        rows = json.loads((PRIVATE/'mapping.json').read_text())['contexts']
        for row in rows:
            if row['pilot_id'] in eligible:
                meta = prepare(row)
                if meta:
                    print(json.dumps({'task': meta['pilot_id'], 'platform': meta['platform'], 'prepared': True}), flush=True)


if __name__ == '__main__':
    main()

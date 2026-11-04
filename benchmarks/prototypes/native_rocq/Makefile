COQC ?= coqc
COQCHK ?= coqchk

MODULES = Common FactorialEquivalent FactorialCounterexample ReverseEquivalent

.PHONY: check clean

check: Common.vo FactorialEquivalent.vo FactorialCounterexample.vo ReverseEquivalent.vo
	$(COQCHK) -silent $(MODULES)

Common.vo: Common.v
	$(COQC) Common.v

FactorialEquivalent.vo: FactorialEquivalent.v Common.vo
	$(COQC) FactorialEquivalent.v

FactorialCounterexample.vo: FactorialCounterexample.v Common.vo
	$(COQC) FactorialCounterexample.v

ReverseEquivalent.vo: ReverseEquivalent.v Common.vo
	$(COQC) ReverseEquivalent.v

clean:
	rm -f *.vo *.vos *.vok *.glob .*.aux *.aux

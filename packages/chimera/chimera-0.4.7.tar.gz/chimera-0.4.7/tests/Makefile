all: test

test: 
	@${PYTHON} runalltests.py

valgrind:
	@echo "Profiling the process. Run kcachegrind on the output"
	valgrind  --tool=callgrind --suppressions=valgrind-python.supp python2.4 runalltests.py

profile:
	@find . -name "hotspot*" -exec rm {} \;
	@${PYTHON} ./profilealltests.py

clean: 
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "*~" -exec rm {} \;
	@find . -name "hotspot*" -exec rm {} \;
	@find . -name "callgrind.out*" -exec rm {} \;

tags:



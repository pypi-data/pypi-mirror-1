######################################################################
## Different doc packages need different things. Some have to 
## import the source, others just need to parse it. The hacks in
## this file attempt to make this happen for some of the common doc
## systems.
######################################################################
export PRODUCT_DIR=${CURDIR}/../
export PYTHONPATH=`./getbuildpath.py`

#DOC_TARGETS += epydoc_html
DOC_TARGETS += epydoc_pdf
DOC_TARGETS += pydoc

all: doc


happydoc_html:
	@happydoc -F HTMLTable  ${PYTHONPATH}/chimera

happydoc_dia:
	@happydoc --dia ${PYTHONPATH}/chimera

epydoc_html:
	@epydoc -qq --html -o ${PRODUCT_DIR}/docs ${PYTHONPATH}/chimera

epydoc_pdf:
	@epydoc -qq --pdf -o ${PRODUCT_DIR}/docs ${PYTHONPATH}/chimera

pydoc:
	@${PYTHON} ./writedocs.py ${PRODUCT_DIR}


doc: ${DOC_TARGETS}

clean: 
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "*~" -exec rm {} \;
	@find . -name "chimera*.html" -exec rm {} \;
	@rm -rf index.html epydoc.css public private
	@rm -rf api.* *.aux *.tex
tags:



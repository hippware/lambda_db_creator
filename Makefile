APP=lambda_db_creator
PGLIB=psycopg2
ZIP=${APP}.zip

SRC_FILES=${APP}.py
DST_FILES=${APP}.pyc

.PHONY: compile clean

all: compile ${APP}.zip

clean:
	-rm ${ZIP} *.pyc

${ZIP}: ${DST_FILES}
	zip -r $@ ${SRC_FILES} ${PGLIB}

%.pyc: %.py
	python -m py_compile $<

compile: ${DST_FILES}

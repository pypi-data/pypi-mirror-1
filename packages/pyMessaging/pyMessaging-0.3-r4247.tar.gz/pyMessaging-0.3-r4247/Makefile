check: clean
	find pymessaging -name '*.py'  -exec pep8 --ignore=E501,W291 --repeat {} \;
	pylint pymessaging

test:
	python pymessaging/zwitschr.py


build:
	python setup.py build sdist bdist_egg

upload: build doc
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyMessaging/
	rsync -r html root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyMessaging/

doc: build
	rm -Rf html
	mkdir -p html
	sh -c '(cd html; pydoc -w ../pymessaging/*.py)'

install: build
	sh -c 'sudo python setup.py install'

clean:
	rm -Rf build dist html test.db svn-commit.tmp pyMessaging.egg-info
	find . -name '*.pyc' -or -name '*.pyo' -delete

.PHONY: build test

c:\Python24\python.exe dolint.py --include-ids=y --additional-builtins=_ --disable-msg=I0011 --rcfile pylintrc turboblog
dot -Tps graphs\import-graph.dot > graphs\import-graph.ps
dot -Tpng graphs\import-graph.dot > graphs\import-graph.png
dot -Tps graphs\int-import-graph.dot > graphs\int-import-graph.ps
dot -Tpng graphs\int-import-graph.dot > graphs\int-import-graph.png

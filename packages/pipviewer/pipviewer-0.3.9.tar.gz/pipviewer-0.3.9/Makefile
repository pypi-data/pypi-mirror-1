
ALL_UI=pipviewer/ScoreGui.py \
       pipviewer/ViewerGui.py \
       pipviewer/SpeciesGenomesGui.py \
       pipviewer/UserManuelGui.py \
       pipviewer/ProbesListGui.py

all: ${ALL_UI}

.PHONY: dist
pack: ${ALL_UI}
	python setup.py asciidoc
	cp docs/html/guide.html pipviewer/
	python setup.py pack

install:
	python setup.py install

clean:
	rm -r ${ALL_UI}

pipviewer/ScoreGui.py: ui/scoregui.ui
	pyuic ui/scoregui.ui > pipviewer/ScoreGui.py

pipviewer/ViewerGui.py: ui/viewergui.ui
	pyuic ui/viewergui.ui > pipviewer/ViewerGui.py

pipviewer/SpeciesGenomesGui.py: ui/speciesgenomesgui.ui
	pyuic ui/speciesgenomesgui.ui > pipviewer/SpeciesGenomesGui.py

pipviewer/UserManuelGui.py: ui/usermanuelgui.ui
	pyuic ui/usermanuelgui.ui > pipviewer/UserManuelGui.py

pipviewer/ProbesListGui.py: ui/probeslistgui.ui
	pyuic ui/probeslistgui.ui > pipviewer/ProbesListGui.py
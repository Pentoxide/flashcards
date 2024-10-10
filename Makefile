help:
	@echo "Downloads flashcards from flashcardo.com and packs them into .mochi formatted file"
	@echo "Usage: make all lang=language"
init:
	test -d venv || python3 -m venv venv
	. venv/bin/activate; python3 -m pip install -r requirements.txt
	mkdir data || exit 0
validate:
	. venv/bin/activate && pylint *.py
process:
	. venv/bin/activate && python3 flashcards.py $(lang)
pack: process
	cd data/$(lang); mkdir temp; cp data.json temp/; cp audio/*.mp3 temp/; cd temp; zip $(lang)1000.mochi data.json *.mp3
	mv data/$(lang)/temp/$(lang)1000.mochi ./
	rm -rf data/$(lang)/temp
all: init process pack

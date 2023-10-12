CMS_DIR = ./cms/
SRC_DIR = ./src/
BUILD_DIR = ./build/

DEPS = python3 python3-markdown python3-bs4 python3-yaml python3-pil

FTP_DOMAIN = ftp.ammd.net:~/

.PHONY: all


all:
	@make --no-print-directory site
	@make --no-print-directory assets

site:
	@echo 'Building site...'
	@python3 $(CMS_DIR) $(SRC_DIR) $(BUILD_DIR)

assets:
	@echo 'Syncing static assets...'
	@rsync -a $(SRC_DIR)/static/ $(BUILD_DIR)
	@echo 'Done'

list-deps:
	@echo $(DEPS)

watch:
	@python3 -m pyinotify -c make -r -e IN_CREATE,IN_DELETE,IN_MODIFY $(SRC_DIR)

test:
	@echo 'Opening home page in default browser...'
	@x-www-browser build/home.html

deploy:
	@echo 'Uploading...'
	@rsync -a $(BUILD_DIR) $(shell read -p "Enter plagiat ftp user name: " x && echo $${x})@$(FTP_DOMAIN)
	@echo 'Done'

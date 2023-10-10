CMS_DIR = ./cms/
SRC_DIR = ./src/
BUILD_DIR = ./build/

DEPS = python3 python3-markdown python3-bs4 python3-yaml python3-pil

FTP_DOMAIN = ftp.ammd.net:~/

.PHONY: all


all:
	@echo 'Building site...'
	@python3 $(CMS_DIR) $(SRC_DIR) $(BUILD_DIR)
	@echo 'Syncing static assets...'
	@rsync -a $(SRC_DIR)/static/ $(BUILD_DIR)
	@echo 'Done'

assets:
	@echo 'Syncing static assets...'
	@rsync -a $(SRC_DIR)/static/ $(BUILD_DIR)
	@echo 'Done'

list-deps:
	@echo $(DEPS)

test:
	@echo 'Opening home page in default browser...'
	@x-www-browser build/home.html

deploy:
	@echo 'Uploading...'
	@rsync -a $(BUILD_DIR) $(shell read -p "Enter plagiat ftp user name: " x && echo $${x})@$(FTP_DOMAIN)
	@echo 'Done'

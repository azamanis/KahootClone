export DJANGOPORT := 8001
export DEBUG := True
# you must update the value of HEROKUHOST
export HEROKUHOST := git:remote protected-bastion-43256
PSQL = psql
CMD = python3 manage.py
HEROKU = heroku run export SQLITE=1 &
# Add applications to APP variable as they are
# added to settings.py file
APP = models services restServer

COVERAGE = python3 -m coverage

## delete and create a new empty database
#clear_db:
#	@echo Clear Database
#	dropdb --if-exists $(PGDATABASE)
#	createdb

# create alumnodb super user
create_super_user:
	$(CMD) shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('alumnodb', 'admin@myproject.com', 'alumnodb')"

populate:
	@echo populate database
	$(CMD) populate

runserver:
	$(CMD) runserver $(DJANGOPORT)

update_models:
	$(CMD) makemigrations $(APP)
	$(CMD) migrate

#reset_db: clear_db update_models create_super_user

shell:
	@echo manage.py  shell
	@$(CMD) shell

dbshell:
	@echo manage.py dbshell
	@$(CMD) dbshell

addparticipants:
	@echo populate database
	python3 ./manage.py addparticipants



static:
	@echo manage.py collectstatic
	python3 ./manage.py collectstatic

fully_update_db:
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations $(APP) 
	python3 ./manage.py migrate

test_authentication:
	$(CMD) test models.test_authentication --keepdb

test_models:
	$(CMD) test models.test_models --keepdb

test_additional_models:
	export TESTING='true' && $(CMD) test models.test_additional --keepdb

test_additional_services:
	$(CMD) test services.test_additional --keepdb

test_services:
	$(CMD) test services.test_services --keepdb

test_services_games:
	$(CMD) test services.test_services_game --keepdb

test_restServer:
	$(CMD) test restServer.test_restServer --keepdb

test_additional_restServer:
	$(CMD) test restServer.test_additional --keepdb

test: test_authentication test_models test_additional_models test_services test_services_games test_restServer test_additional_restServer


########################################################################
## Coverage
########################################################################

TEST_MODELS=models.test_models models.test_authentication models.test_additional
TEST_SERVICES=services.test_services services.test_services_game services.test_additional
TEST_REST_API=restServer.test_restServer restServer.test_additional

coverage_models:
	${COVERAGE} erase
	export TESTING='true' && ${COVERAGE} run --omit="*/test*" --source=models ./manage.py test ${TEST_MODELS}
	${COVERAGE} report -m -i > coverage_models.txt

coverage_services:
	${COVERAGE} erase
	export TESTING='true' && ${COVERAGE} run --omit="*/test*" --source=services ./manage.py test ${TEST_SERVICES}
	${COVERAGE} report -m -i > coverage_services.txt

coverage_restServer:
	${COVERAGE} erase
	export TESTING='true' && ${COVERAGE} run --omit="*/test*" --source=restServer ./manage.py test ${TEST_REST_API}
	${COVERAGE} report -m -i > coverage_restServer.txt

coverage:
	${COVERAGE} erase
	export TESTING='true' && ${COVERAGE} run --omit="*/test*" --source=. ./manage.py test ${TEST_MODELS} ${TEST_SERVICES} ${TEST_REST_API}
	${COVERAGE} report -m -i > coverage.txt


compile_user_guide:
	pandoc -o user_guide.pdf user_guide.md
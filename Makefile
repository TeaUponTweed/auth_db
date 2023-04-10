freeze:
	pip-compile

make install:
	pip install -U pip-tools black isort pip
	pip install -r requirements.txt -e .

polish:
	black --quiet src/
	isort src/

local: inline
	python -c "from auth_db.db import init_db; init_db('./logs/auth.db', './schema.sql')"
	DB_FILE_LOC=./logs/auth.db  gunicorn --bind 0.0.0.0:8080 auth_db.app:app

inline:
	# npm install -g inliner
	# inline HTML
	mkdir -p src/auth_db/static
	inliner -i html/forgot_password.html > src/auth_db/static/forgot_password.html
	inliner -i html/index.html > src/auth_db/static/index.html
	inliner -i html/login.html > src/auth_db/static/login.html
	inliner -i html/signup.html > src/auth_db/static/signup.html
	# inline templates
	mkdir -p src/auth_db/templates
	inliner -i html/template_reset_password_non_inlined.html > src/auth_db/templates/reset_password.html

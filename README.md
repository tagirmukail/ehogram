# ehogram
Chat
(flask, mongodb)
Для запуска приложения необходимо установленная mongodb.
1.	Устанавливаем и запускаем виртуальное окружение.
2. 	Устанавливаем необходимые библиотеки:
		$ pip install -r requirements.txt
3.	В config.py устанавливаем свои настройки.
4.	В etc/mongod.conf необходимо изменить настройки.
5. 	Запускаем сервер mongodb.
		$ service mongod start
6. 	Запускаем приложение:
		$ python chat_example.py


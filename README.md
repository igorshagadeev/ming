Music INGest service

python 2.7 + flask + SQLAlchemy

create fingerprints from mp3 files
and store them to database


Usage:

go to ming_service/ming
feed some test files

    $ python ming.py -f ../../fixtures/

go to ming_service
start flask monitor and querying

    $ python app.py

tests:
in ming_service dir run command

    $ python -m unittest discover
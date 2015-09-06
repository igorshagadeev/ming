Music INGest service

python 2.7 + flask + SQLAlchemy

create fingerprints from mp3 files
and store them to database


Usage:

go to ming_service/ming <br />
and feed some test files:

    $ python ming.py -f ../../fixtures/

go to ming_service <br />
start flask monitor and querying service:

    $ python app.py

tests <br />
go to ming_service directory and run command:

    $ python -m unittest discover
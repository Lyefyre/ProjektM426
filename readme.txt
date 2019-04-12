########

git clone https://github.com/Lyefyre/ProjektM426.git

cd /ProjektM426

######
local rtequirements
python 3.6 and pip must be instlled
######

python3.6 -m pip install setuptools

sudo python3.6 -m pip install --upgrade pip

######
a virtual environment must be created
######

virtualenv coolenv

######
activate it
######

source coolenv/bin/activate

pip install -r requirements.txt

python manage.py runserver

######
all fine, now enjoy coolbox
######

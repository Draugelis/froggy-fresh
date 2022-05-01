#!/bin/bash


# Checking if virtualenv is installed on host
if [[ ! $(pip list|grep "virtualenv") ]]
then
    echo "Installing virtualenv"
    pip3 install --upgrade pip
    pip3 install virtualenv
    
else
    echo "✓ virtualenv is installed"
fi

echo "✓ Activating virtual env"
python3 -m venv .
source bin/activate

# Installing requirements 
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "✓ Setup completed"
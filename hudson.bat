pip install BitVector
pip install BitPacket
pip install pylint
pip install coverage

coverage run bitgames.py -t
coverage xml
echo %ERRORLEVEL%
python26 run_pylint.py
echo %ERRORLEVEL%

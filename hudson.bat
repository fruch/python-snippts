easy_install BitVector
easy_install BitPacket

python26 bitgames.py -t
echo %ERRORLEVEL%
python26 run_pylint.py
echo %ERRORLEVEL%
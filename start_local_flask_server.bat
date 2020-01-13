set root="C:\Users\Soren Mortvedt\AppData\Local\Continuum\anaconda3"

call %root%\Scripts\activate.bat %root%

set root="C:\javaScript\baseball"
python pythonBaseballFlaskServer.py
pause
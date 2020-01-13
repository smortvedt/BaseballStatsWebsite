net start mysql80

set root="C:\Users\Soren Mortvedt\AppData\Local\Continuum\anaconda3"

call %root%\Scripts\activate.bat %root%

python -m http.server
pause
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c streamlit run ""C:\Users\ASUS\OneDrive\PRESTAMOS\IA\IA V2\app.py"" > NUL 2>&1", 0, false
Set WshShell = Nothing

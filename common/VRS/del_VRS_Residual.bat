REM Deletes the residual folder/files from the VRS simulation

del /q C:\ProgramData\boost_interprocess\*
for /d %%x in (C:\ProgramData\boost_interprocess\*) do @rd /s /q "%%x"
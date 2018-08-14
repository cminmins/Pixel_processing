@echo off
REM wrapper to use shebang first line of nib-nifti-dx
set mypath=%~dp0
set pyscript="%mypath%nib-nifti-dx"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call "%py_exe%" %pyscript% %*

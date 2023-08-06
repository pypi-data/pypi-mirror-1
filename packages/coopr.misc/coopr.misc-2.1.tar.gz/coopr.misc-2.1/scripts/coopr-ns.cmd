@echo off
REM
REM This batch file is customized to work within a virtualenv
REM environment.  This script can be called without using the virtualenv
REM activate.bat command.
REM

set VIRTUAL_ENV=__VIRTUAL_ENV__
set PATH=%VIRTUAL_ENV%\bin;%PATH%
set COOPR_BIN=%VIRTUAL_ENV%\bin

@python "%COOPR_BIN%\coopr-ns" %* & exit /b

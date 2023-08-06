@echo off
setlocal 
if "%1" == "" %0 build
set python=call python

:do_arg
set arg=%1
if %arg% == -v (set pyversion=%2 & set python=call python%2 & shift & goto next)
if %arg% == test (pushd test && %python% test_multifileiter.py & popd & goto next)
if %arg% == html (echo Building readme.html && c:\apps\python26\Scripts\rst2html.py readme.txt readme.html & goto next)
if %arg% == release (call %0 html && call :tag & goto next)
if %arg% == upload (call :upload & goto next)
if %arg% == tag (call :tag & goto next)
for %%c in (build install sdist bdist_wininst register) do @if %arg% == %%c (%python% setup.py %%c & goto next)
if %arg% == help goto help
echo Unknown target: %arg%
exit /b 1

:next
shift
if not "%1" == "" goto do_arg
goto :EOF

:tag
set hay_diff=
for /f %%n in ('svn diff') do (set hay_diff=SI & goto :tag01)
:tag01
if defined hay_diff (echo ATENCION: Hay cambios sin confirmar!!!! & echo.)
for /f %%v in ('setup.py --version') do set version=%%v
echo Ok to create tag release_%version%?
pause
call svn delete https://multifileiter.googlecode.com/svn/tags/release_%version% -m "Release %version%" 
call svn copy https://multifileiter.googlecode.com/svn/trunk https://multifileiter.googlecode.com/svn/tags/release_%version% -m "Release %version%" 
goto :EOF

:upload
echo Uploading to PyPI
setup.py register sdist bdist_wininst upload
call python31 setup.py bdist_wininst upload
echo Uploading to Google Code
for /f %%v in ('setup.py --version') do set version=%%v
for /f %%p in (googlecodepassword.txt) do set password=%%p
googlecode-upload.py -s "multifileiter %version% source package" -p multifileiter --labels=Type-Source,OpSys-All -u ggenellina --password=%password% dist\multifileiter-%version%.zip
googlecode-upload.py -s "multifileiter %version% Windows binaries (Python 2.6)" -p multifileiter --labels=Type-Installer,OpSys-Windows -u ggenellina --password=%password% dist\multifileiter-%version%.win32-py2.6.exe
googlecode-upload.py -s "multifileiter %version% Windows binaries (Python 3.1)" -p multifileiter --labels=Type-Installer,OpSys-Windows -u ggenellina --password=%password% dist\multifileiter-%version%.win32-py3.1.exe
goto :EOF

:help
echo make [-v pythonversion] [command] ...
echo.
echo commands = build install test html sdist bdist_wininst release upload tag
echo.


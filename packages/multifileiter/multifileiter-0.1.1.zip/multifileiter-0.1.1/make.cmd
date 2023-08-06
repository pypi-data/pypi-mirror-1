@echo off
setlocal 
if "%1" == "" %0 build

:do_arg
set arg=%1
if %arg% == test (pushd test && test_multifileiter.py & popd & goto next)
if %arg% == html (c:\apps\python26\Scripts\rst2html.py readme.txt readme.html & popd & goto next)
if %arg% == release (call %0 html && call :upload & goto next)
for %%c in (build install sdist bdist_wininst register upload) do if %arg% == %%c (setup.py %%c & goto next)
if %arg% == help goto help
echo Unknown target: %arg%
exit /b 1

:next
shift
if not "%1" == "" goto do_arg
goto :EOF

:upload
echo Uploading to PyPI
setup.py register sdist bdist_wininst upload
echo Uploading to Google Code
for /f %%v in ('setup.py --version') do set version=%%v
googlecode-upload.py -s "multifileiter %version% source package" -p multifileiter -u ggenellina dist\multifileiter-%version%.zip
googlecode-upload.py -s "multifileiter %version% Windows binaries (Python 2.6) " -p multifileiter -u ggenellina dist\multifileiter-%version%.win32-py2.6.exe
goto :EOF

:help
echo make [command] ...
echo.
echo commands = build install test html sdist bdist_wininst release
echo.


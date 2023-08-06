@echo off
setlocal 
if "%1" == "" %0 build

:do_arg
set arg=%1
if %arg% == test (pushd test && test_multifileiter.py & popd & goto next)
if %arg% == html (c:\apps\python26\Scripts\rst2html.py readme.txt readme.html & popd & goto next)
if %arg% == release (call %0 html && setup.py register sdist bdist_wininst upload & goto next)
for %%c in (build install sdist bdist_wininst register upload) do if %arg% == %%c (setup.py %%c & goto next)
if %arg% == help goto help
echo Unknown target: %arg%
exit /b 1

:next
shift
if not "%1" == "" goto do_arg
goto :EOF

:help
echo make [command] ...
echo.
echo commands = build install test html sdist bdist_wininst release
echo.

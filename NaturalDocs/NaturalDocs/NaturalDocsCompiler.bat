@echo off

set input = ..\..\
set output = HTML ..\
set project = .\

.\NaturalDocs.bat -i %input% -o %output% -p %project%
.\NaturalDocs.bat -i ..\..\ -o HTML ..\ -p .\
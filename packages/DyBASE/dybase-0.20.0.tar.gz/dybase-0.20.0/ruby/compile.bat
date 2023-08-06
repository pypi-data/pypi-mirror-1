if not defined RUBY_HOME set RUBY_HOME=\ruby-1.8.0

cl -ML -DIMPORT -DUSEIMPORTLIB /GX -LD -Zi -I..\inc -I%RUBY_HOME% -I%RUBY_HOME%\win32 dybaseapi.c  ..\lib\dybasedll.lib %RUBY_HOME%\win32\msvcrt-ruby18.lib



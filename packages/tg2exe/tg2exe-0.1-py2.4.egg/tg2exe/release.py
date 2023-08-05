# Release information about tg2exe

version = "0.1"

description = "Make TurboGears project to the Stand Alone Windows Application"
long_description = """tg2exe is a "tg-admin" extension which could help you converting the TurboGears project to an
                        Stand Alone Application on windows platform.

                    Advantage
                    --------------
                    The benifit is you can use TurboGears' power to write OffLine applications with web interface
                    and AJAX. When the application is running, your computer host as a web server (Actually it is).
    
                    Your user can quickly evaluate your application without install python or related modules.

                    Install
                    --------------
                    You could use $easy_install tg2exe to install this module
                    
                    pywin32 is required
                    http://sourceforge.net/projects/pywin32/
                    
                    Usage
                    ----------
                    Once you installed tg2exe, you'll got an 'makexe' command within the "tg-admin" command line utility.
                    Enter your project folder, type "tg-admin makexe" and tg2exe will produce a dist folder for you.
                    You could package it into an installer (such as innosetup)

                    Note
                    -----------
                    The owe is its distribution size. The raw dist with quickstart project is about 30 MB (Zip size is 11 MB).
                    Half-size distribution is expected for future TurboGears.

                    Current Stage: make it work
                    (next stages are make it better, make it small)

                    Credit
                    ------------
                    tg2exe is based on the script written by Volodymyr Orlenko,
                            he post the original script on TurboGears MailList in Jul 2006.

                    If you have any question, please go to google turbogears group.
                    
                """

author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2006"

# if it's open source, you might want to specify these
url = "docs.turbogears.org"
download_url = "http://www.python.org/pypi/tg2exe"
license = "MIT"

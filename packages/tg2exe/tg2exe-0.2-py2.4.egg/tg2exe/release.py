# Release information about tg2exe

version = "0.2"

description = "Make TurboGears project to the Stand Alone Windows Application"
long_description = """tg2exe is a "tg-admin" command line utility extension
                      which could help you converting the TurboGears project to an
                      Stand Alone Application on windows platform.

                    Advantage
                    --------------
                    The benifit is you can use TurboGears' power to write 
                    Off-line applications with web interface and AJAX.

                    When the application is running, your computer host as 
                    a web server (Actually it is).
    
                    Your user can quickly evaluate your application without install 
                    python or related modules.

                    Install
                    --------------
                    You could use::

                        $ easy_install tg2exe

                    command to install this module
                    
                    pywin32 is required
                    http://sourceforge.net/projects/pywin32/
                    
                    Usage
                    ----------
                    Once you installed tg2exe, you'll got an 'makexe' command within 
                    the "tg-admin" command line utility.

                    Enter your project folder, type::

                      tg-admin makexe

                    and tg2exe will produce a dist folder for you.
                    
                    This utility does not make an *.exe, it assembles all the 
                    dependencies and runtime libraries into a single directory,
                    so that it's easy to wrap everything into a single setup package.

                    You are free to package 'dist' folder into an installer (such as InnoSetup).

                    Notice that the stand alone file are equivalent to production project,
                    so you need to have a setted prod.cfg. The simple approach is to 
                    rename the sample-prod.cfg to prod.cfg.
                    
                    Note
                    -----------
                    The owe is its distribution size. The raw dist with quickstart 
                    project is about 12 MB.

                    After a quick remove, 10MB (1/3) is possible.

                    Current Stage: make it work
                    
                    (next stages are make it better, then make it small)

                    Credit
                    ------------
                    tg2exe is based on the script written by Volodymyr Orlenko,
                            he post the original script on TurboGears MailList in Jul 2006.

                    If you have any question, please go to google turbogears group.
                    
                    History
                    ------------
                    0.1 2006/11/14
                        initial workable
                    0.2 2006/11/15 
                        reduce 70% distribution size (30MB->12MB)
                    
                """

author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2006"

# if it's open source, you might want to specify these
url = "docs.turbogears.org"
download_url = "http://www.python.org/pypi/tg2exe/"
license = "MIT"

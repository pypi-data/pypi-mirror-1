Dependence analysis utils
=========================

This packages to provide tools for dependence analysis of python modules.

Programs
--------

    find_requires
        Program find all dependences required by python module
        or module set.
        
        Used::

            find_requires [<MODULE> [...]] [-f (RPM|PYPI)] [-r]
            
        -f
            Dependencies will be printed in RPM or PYPI format,
            it is PYPI by default;
            
        -r
            The name of file will be printed
            after dependence emited by them.

        The program must be run in directory contains module.
 
    find_provides
        Programm find all dependencies provided by python module
        or module set.
        
        Used::

            find_provides [<MODULE> [...]] [-f (RPM|PYPI)]
      
        -f
            Dependencies will be out in RPM or PYPI format, it is PYPI by
            default;
          
        The program must be run in directory contains module.

    imalyzer
        Program do analyse dependencies beetween files in module
        set, but it is only experimental version and it using is not
        recommended now.
        
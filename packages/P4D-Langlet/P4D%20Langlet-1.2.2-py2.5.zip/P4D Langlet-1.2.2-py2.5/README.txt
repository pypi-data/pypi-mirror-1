Welcome to P4D!

P4D ( Python For Data ) is a Python extension language used to write data in a pythonic way that are isomorphic to those encoded in XML. 
P4D provides E4X style syntactical extensions to extract data from P4D elements that are built as some sort of Python statement.


INSTALLATION

P4D requires Python 2.5 being installed. It won't work with prior or later versions of Python.

Just type

    python setup.py install

while being in the root directory of the project. 

P4D is written using EasyExtend as an EasyExtend langlet. EasyExtend doesn't have to be installed separately. 
You can find P4D in the directory

              <MyPythonPath>/lib/site-packages/EasyExtend/langlets/p4d


Psyco
-----
Installation of Psyco is optional but strongly recommended. Psyco leads to 3 times speedup of the P4D parser. 

Psyco for Python 2.5 is available and it can be found here:

            http://psyco.sourceforge.net/


GETTING STARTED

Switch to the p4d directory and type `python run_p4d.py` and a P4D aware Python shell should open. 

Typing 
          python run_p4d.py pymodule.py

shall execute a Python module as expected.

The recommended way to place P4D specific definitions in a module is to use the p4d file suffix because this ain't confuse users:

          python run_p4d.py p4dmodule.p4d


Alternatively you might switch to the 

          <MyPythonPath>/scripts

directory and use the p4d.py script or p4d.bat on Windows.


FURTHER DOCUMENTATION

More comprehensive documentation can be found at

	http://www.fiber-space.de/EasyExtend/doc/p4d/p4d.html


Release Information
-------------------

The current P4D release is 1.2 Changes on P4D will be notified in the P4D documentation directly.









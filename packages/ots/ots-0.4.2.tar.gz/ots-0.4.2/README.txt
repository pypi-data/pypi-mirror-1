Wrapper around the OTS (http://libots.sourceforge.net) library for
text summarization.

REQUIRES:
	libots
	libxml2
	pyrex



INSTALLATION:

If you don't have libots installed on your platform the source is
inclued in the ./lib directory

you can build it with a standard 
    
    ./configure --prefix=/usr
    make 
    make install 


after that you can use setuptools to build and install ots


    python setup.py install.



    

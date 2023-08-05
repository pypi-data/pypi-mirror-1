# Utility script to generate a Mac OS X Application bundle
#
# uses py2app 
# from http://svn.pythonmac.org/py2app/py2app/trunk/doc/index.html
#
# @Thibauld Nion

# Go in upper (main) directory and clean
cd ..
rm -rf dist build setup.py


# actually create the .App
python setupbundle.py py2app

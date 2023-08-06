#! /bin/bash

# If we are on Mac OS X, look for the latest SDK and do a universal build
if [ `uname` == "Darwin" ]; then
  LATEST_SDK=''
  for f in /Developer/SDKs/*; do
    LATEST_SDK=$f
  done
  if [[ $LATEST_SDK == /Developer/SDKs/MacOSX10.4u.sdk ]]; then
    export CFLAGS='-isysroot '${LATEST_SDK}' -arch i386 -arch ppc -arch x86_64 -arch ppc64'
    export LDFLAGS='-isysroot '${LATEST_SDK}' -arch i386 -arch ppc -arch x86_64 -arch ppc64'
  elif [[ $LATEST_SDK == /Developer/SDKs/MacOSX10.5.sdk ]]; then
    export CFLAGS='-isysroot '${LATEST_SDK}' -arch i386 -arch ppc -arch x86_64 -arch ppc64'
    export LDFLAGS='-syslibroot,'${LATEST_SDK}' -arch i386 -arch ppc -arch x86_64 -arch ppc64'
  else
     export CFLAGS='-isysroot '${LATEST_SDK}' -arch i386 -arch ppc -arch x86_64'
     export LDFLAGS='-syslibroot,'${LATEST_SDK}' -arch i386 -arch ppc -arch x86_64'
  fi
fi

rm -rf readline-lib
tar xzvf readline-6.0.tar.gz
mv readline-6.0 readline-lib
cd readline-lib
patch -p0 < ../readline60-001
patch -p0 < ../readline60-002
patch -p0 < ../readline60-003
patch -p0 < ../readline60-004
./configure CPPFLAGS='-DNEED_EXTERN_PC'
make

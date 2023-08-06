#E:\profile
#VS90COMNTOOLS D:\setup\vs8\Common7\Tools\

from distutils.core import setup, Extension

setup(
        name = 'clhash',
        version = '1.002',
        ext_modules = [
            Extension('clhash', ['clhash.cpp'],),
        ],
        description="merge crc32 and lookup",
        long_description="""
Merge hash function from crc32 and lookup

c version by jingmi , python wrapper by zsp:

    from clhash import get_unsigned_hash,get_hash

    print get_unsigned_hash("stdyun.com zsp007@gmail.com")

    print get_hash("stdyun.com zsp007@gmail.com")


Reference:
http://burtleburtle.net/bob/hash/doobs.html
"""
)

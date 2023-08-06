#       pybloomfilter.py
#       
#       Copyright 2009 ahmed youssef <xmonader@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.



__all__=["new_bloomfilter"]


from ctypes import *
from ctypes.util import find_library

calgfound=find_library("calg")
if calgfound is None:
    print "[-]calg library: http://c-algorithms.sourceforge.net"
    exit(-1)
calg=CDLL(calgfound)




#types

bloomfilter_value=c_void_p
HASH_FUNC=CFUNCTYPE(c_ulong, bloomfilter_value)

    
    
#bloomfilter

#struct _BloomFilter {
	#BloomFilterHashFunc hash_func;
	#unsigned char *table;
	#unsigned int table_size;
	#unsigned int num_functions;
#};

class BloomFilter(Structure):
    
    __fields__=[
        ("hash_func", HASH_FUNC),
        ("table", c_char_p),
        ("table_size", c_uint ),
        ("num_functions",c_uint ),
    ]
    
bloomfilter_p=POINTER(BloomFilter)
#bloomfilter_p=c_void_p


#BloomFilter *bloom_filter_new(unsigned int table_size, 
                              #BloomFilterHashFunc hash_func,
                              #unsigned int num_functions);
                              
bf_new=calg.bloom_filter_new
bf_new.restype=bloomfilter_p
bf_new.argstype=[c_uint, HASH_FUNC, c_uint ]

#void bloom_filter_free(BloomFilter *bloomfilter);
bf_free=calg.bloom_filter_free
bf_free.restype=None
bf_free.argstype=[bloomfilter_p]

#void bloom_filter_insert(BloomFilter *bloomfilter, BloomFilterValue value);
bf_insert=calg.bloom_filter_insert
bf_insert.restype=None
bf_insert.argstype=[bloomfilter_p, bloomfilter_value]


#int bloom_filter_query(BloomFilter *bloomfilter, BloomFilterValue value);
bf_query=calg.bloom_filter_query
bf_query.restype=c_int
bf_query.argstype=[bloomfilter_p, bloomfilter_value]



#void bloom_filter_read ( BloomFilter * bloomfilter, unsigned char *array) 		
bf_read=calg.bloom_filter_read
bf_read.restype=None
bf_read.argstype=[bloomfilter_p, c_char_p]

#void bloom_filter_load ( BloomFilter * bloomfilter, unsigned char *array) 	
bf_load=calg.bloom_filter_load
bf_load.restype=None
bf_load.argstype=[bloomfilter_p, c_char_p]

#hash functions.
#unsigned long string_hash(void *string);
string_hash=calg.string_hash
string_hash.restype=c_ulong
string_hash.argstype=[c_void_p]

#unsigned long int_hash(void *location);
int_hash=calg.int_hash
int_hash.restype=c_ulong
int_hash.argstype=[c_void_p]

class BloomFilterWrapper(object):
    """A bloom filter is a space efficient data structure that can be used to test whether a given element is part of a set. Lookups will occasionally generate false positives, but never false negatives."""
        
    def __init__(self, tablesize=128, hashfunction=string_hash, nfunctions=1):
        self.b=bf_new(tablesize, hashfunction, nfunctions)
    
    def insert(self, val):
        """Insert a value into the bloom filter. """
        bf_insert(self.b, val)
        
    def query(self, val):
        """Query a bloom filter for a particular value. """
        return bf_query(self.b, val)
        
    def __contains__(self, val):
        return self.query(val)
    
    def __del__(self):
        bf_free(self.b) #Destroy the bloom filter. 

def new_bloomfilter(tablesize=128, hashfunction=string_hash, nfunctions=1):
    return BloomFilterWrapper(tablesize, hashfunction, nfunctions)
    
if __name__=="__main__":
    
    b=new_bloomfilter()
    b.insert("ahmed")
    b.insert("ayman")
    print "ahmed" in b
    print "ayman" in b
    print "memo" in b

    del b
    

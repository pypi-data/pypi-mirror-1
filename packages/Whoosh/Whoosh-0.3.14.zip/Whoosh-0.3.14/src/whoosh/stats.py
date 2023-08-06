#===============================================================================
# Copyright 2009 Matt Chaput
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

from heapq import nlargest


def distinctive_terms(reader, fieldid, top=10):
    gen = ((tf * (1.0/df), text)
           for text, df, tf in reader.iter_field(fieldid))
    return nlargest(top, gen)


if __name__ == "__main__":
    from time import clock as now
    from whoosh.index import open_dir
    ix = open_dir("c:/workspace/Whoosh-trunk/bmark/testindex")
    r = ix.reader()
    t = now()
    print distinctive_terms(r, "text", 20)
    print now() - t
    
    
    

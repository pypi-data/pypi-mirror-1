
import sys

#sys.path.append('../FileHStore/')

import FileHStore as FHS

store = FHS.FileHStore("./.hstore","sha256", 3)

id = store.add("./testfile")

print store.getpath(id)

store.remove(id)


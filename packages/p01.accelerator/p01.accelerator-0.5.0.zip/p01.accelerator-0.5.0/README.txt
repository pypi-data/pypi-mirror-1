This package provides a browser request and publication for Zope3. File uploads
get directly stored in a persistent temporary file. This file can be used in 
file storages with zero-copy processing. The temporary file is controlled by 
a special transaction data manager which also takes care of removing the 
temporary file if the transaction get aborted or commited.

# Parallel processing

This package provides `PFileProcessor` for parallel download and processing of files.

The main process continuously downloads and queues files. N worker processes 
collect and process the files. Logging from all spawned processes is routed 
through to the main process.

## Getting started
See [example_pfprocess.py](./examples/example_pfprocess.py) for an example of 
using `PFileProcessor`.
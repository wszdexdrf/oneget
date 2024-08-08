# Oneget
This program is designed to download multiple files simultaneously, employing various techniques to overcome potential bottlenecks in the process.

### Parallelizing Multiple Downloads
Downloading a single file over the internet can be slow due to various factors. To address this issue, our program is designed to download multiple files concurrently, thereby enhancing throughput.

### Caching Files
File downloads are performed asynchronously, which implies download of many files will cause a radom order write. Traditional long-term storage solutions, such as magnetic spinning hard drives, offer slower random access speeds but faster serial write speeds, primarily due to the time it takes for the read/write head to seek the correct location. To mitigate this, our program initially caches downloads in TEMPFS, typically within _Random Access_ Memory (RAM), which provides rapid _random access_. Once the files have finished downloading, their addresses are added to a queue. A separate thread monitors this queue and moves the files serially onto the hard drive. Considering RAM accesses to be near instantaneous compared to long term storage, this converts the algorithm to be serial instead of random. A sequential write, as compared to random write, can be up to 100 times faster on modern hard drives. A fast internet connection (2.5Gb/s or more) is required to match or exceed the serial write speeds of a modern hard drive, which removes all possible bottlenecks for most of the users.

### Chunking Files
The files to be downloaded can be quite large. To optimize resource usage, our program implements a basic chunking strategy. This approach breaks the files into smaller, more manageable pieces, which can be downloaded separately. This not only improves reliability (as a failed download can resume from the last successful chunk) but also allows for parallel downloads of different chunks, potentially speeding up the process.
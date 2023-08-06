humansize.py
(c) 2009 Mark Pilgrim, MIT-licensed

This is a sample program from "Dive Into Python 3" that converts file sizes to human-readable form.

Available functions:
approximate_size(size, a_kilobyte_is_1024_bytes)
    takes a file size and returns a human-readable string

Examples:
>>> approximate_size(1024)
'1.0 KiB'
>>> approximate_size(1000, False)
'1.0 KB'

For more information, see http://diveintopython3.org/your-first-python-program.html

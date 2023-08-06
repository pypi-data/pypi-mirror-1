Size reporter and Dupe Finder README

Joe Koberg 2008-04-14
joe@osoft.us

  This program may be distributed under the terms of the GNU Public License, v3.    
  See the file "LICENSE.TXT" which should be included with this program.
  Or find the license at http://www.gnu.org/licenses/gpl.html .


Description:

This size reporter program will traverse a directory tree and
produce data files listing every file and directory and their
sizes. Additionally it creates a directory map in PDF.

It will then search for files with duplicate content, and
directories with duplicate content and structure.

(These instructions assume you are using the Windows binary package.
If not, use EZ Install to install the script, and run it as "sizedupe")


Simple usage instructions:

1. Unpack the distribution archive. There is no need to move
    files around or install anything into Windows. (this
    example will assume you unpacked to c:\sizedupe).
    additionally you can map to a shared drive with this
    executable, including via RDP (\\tsclient\...). It is
    not sensitive to directory location, as long as the 
    executable remains in the folder with its DLLs and library.

2. Run the program on the directory you are interested in. Either
   double click the EXE, or open a command prompt and:

      C:\Sizereport> sizedupe.exe c:\
   
3. Three tab-separated files are generated in current directory:

    * sizereport_YYYYMMDD_HHMMSS_dirs.txt
       List of every directory. Columns:
         DirectoryID
         Parent Directory Name
         Directory Name
         Number of directly contained directories
         Number of all contained directories
         Number of directly contained files
         Number of all contained files
         Size of directly contained files
         Size of all contained files        

    * sizereport_YYYYMMDD_HHMMSS_extensions.txt
       List of extensions found in each directory. Columns:
         DirectoryID
         Extension
         Size of directly contained files of this extension
         Size of all contained files of this extension

    * sizereport_YYYYMMDD_HHMMSS_files.txt
       List of every file. Columns:
         DirectoryID
         File Name
         Extension
         Size
         Date Created
         Date Modified
         Date Accessed

5. The PDF file map is a graph of directories and files by size.
   The top-level directories form the leftmost column of rectangles.
   To the right of each of those directories are rectangles representing
   the directories and files contained therein. The heights of 
   all rectangles are relative to their disk usage.  Intense colors
   represent recent files and pale colors are "old" files.  A label is
   printed to the right of any file or directory big enough to fit it.
   

6. If you specify -d on the command line, duplicates will be found after
   the size report run.  These files are in a readable python syntax format
   for ease of later parsing.
    * sizereport_YYYYMMDD_HHMMSS_dupes.txt
    * sizereport_YYYYMMDD_HHMMSS_dupedirs.txt





# Distributed file system
# Name: Rakshith Ramesh Shetty
The project has two parts, a client and a server. Client has the option of Uplaoding, Listing and Downloading the Files.

To get the servers up and running a configuration file and the port number should be passed which will be the servers port. Server can be run by the following command:
python dfs.py /DFS[n] [port number]
where [n=1,2,3,4] is the server number.

To run the client program an argument of the configuration file should be passed which contains the server's IP addresses, port numbers and a username and password to authenticate client. Following command can be used to run the client:
python dfc.py dfc.conf


For Uploading, the file is divided into four parts and each of the part is sent to two servers for having redundancy. The decision of which file should be sent to which server is based on the Md5 hash value of the file content. A seperate directory for a user is created in which the files are saved. For upoading the file, all four servers must be up and running.
Command for Uploading is:
put filename username password
*(where filename is filename with extention, username and password is case sensitive)


For List Function, all the servers that are active are scanned accoridng to the user directory. If all four parts of the file is present in all servers combined, the User will receive the response as a filename that is listed, else, the file would be shown as incomplete.
Command for List is:
list username password

For Downloading, first it is determined wether the file is complete or not, if not, the user will be notified. If the file is complete, the code will only one instance of each file part for traffic optimization and then reconstruct the file back.
Command for Downloading is:
get filename username password


Servers can handle upto 5 users simultaneously. 

Key features:
- Redundancy
- Traffic optimisation
- Supports any format of file of any length(tested with .txt files of about 1 MB size)

"""
A very basic usage example. 

I'll expand this out a bit more and maybe add some command line handling. 
The power of this comes more from being able to programitically drive file
upload/downloading. If your on the command line I suggest using sftp 
instead ;)

Oisin Mulvihill
2009-02-04

"""
from zoinksftp import Connection


def main():
    """This is more for illustration purposes then anything else, as
    you'll need to change the details in order for it to work.
    """
    username = "myuser"
    password = "haveague33"
    
    myssh = Connection('example.com', username=username, password=password)

    # Upload a file from the current directory to the remote side:
    myssh.put('ssh.py')

    # Download a file into the current directory:
    myssh.get('mydata.db')

    # Recover the contents of a remote directory into a local one:
    myssh.getdir('/home/myuser/reports', "/tmp/reports")

    myssh.close()


if __name__ == "__main__":
    main()

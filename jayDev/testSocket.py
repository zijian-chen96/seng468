import socket, sys

# Print info for the user
print("\nEnter: StockSYM, userid");
print("  Invalid entry will return 'NA' for userid.");
print("  Returns: quote,sym,userid,timestamp,cryptokey\n");

# Get a line of text from the user

#fromUser = "ADD, jiosesdo, 100.00\r"

# Create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('quoteserve.seng.uvic.ca',4447))
#while True:
fromUser = sys.stdin.readline();
    # Connect the socket

    # Send the user's query
s.send(fromUser)
    # Read and print up to 1k of data.
data = s.recv(1024)
print (data)


# close the connection, and the socket
s.close()

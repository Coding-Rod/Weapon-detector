echo "Welcome to the crime detection system controller"
echo "Please your username and password to start the system"

read -p "Username: " username &&
stty -echo &&
read -p "Password: " password &&
stty echo &&
echo "" &&

# Start the Python scripts in the background subshell
(python3 app.py "$username" "$password" &
python3 inference.py &)

# If you started the system with the correct credentials, you can now access the web interface, if after that you close the terminal, the system will stop and you should restart the system again
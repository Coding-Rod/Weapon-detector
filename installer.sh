# Install libraries
echo "Installing python3 dependencies..."
sudo apt-get update
sudo apt-get install -y liblapack-dev libblas-dev gfortran libfreetype6-dev libopenblas-base libopenmpi-dev libjpeg-dev zlib1g-dev
sudo apt-get install -y python3-pip

# Update Pip
echo "Updating pip..."
python3 -m pip install --upgrade pip

# Install below necessary packages
# For numpy, first uninstall the version already installed, and then install numpy==1.19.0
echo "Installing pip dependencies for YOLO..."
pip3 install numpy==1.19.0
pip3 install pandas==0.22.0
pip3 install Pillow==8.4.0
pip3 install PyYAML==3.12
pip3 install scipy==1.5.4
pip3 install psutil
pip3 install tqdm==4.64.1
pip3 install imutils

# Install Pycuda
echo "Installing PyCuda..."
export PATH=/usr/local/cuda-10.2/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH
python3 -m pip install pycuda --user

# Install Seaborn
echo "Installing seaborn"
sudo apt install python3-seaborn

# Install torch & torchvision
echo "Installing PyTorch..."
wget https://nvidia.box.com/shared/static/fjtbno0vpo676a25cgvuqc1wty0fkkg6.whl -O torch-1.10.0-cp36-cp36m-linux_aarch64.whl
pip3 install torch-1.10.0-cp36-cp36m-linux_aarch64.whl
git clone --branch v0.11.1 https://github.com/pytorch/vision torchvision
cd torchvision
sudo python3 setup.py install 

# Project dependencies
echo "Installing pip dependencies for Server..."
pip3 install aiohttp==3.0.6
pip3 install cryptography==3.4.6
pip3 install Flask
pip3 install PyYAML
pip3 install requests

# Not required but good library
echo "Installing Jetson Stats..."
pip3 install jetson-stats==3.1.4

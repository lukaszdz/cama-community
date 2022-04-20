source .env-staging
scp -i $STAGING_PKEY .env-staging $STAGING_HOST:~/
scp -i $STAGING_PKEY .env-prod $STAGING_HOST:~/

$SSH_CONNECT 'bash -s' <<'ENDSSH'
    sudo apt update
    sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
    wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz
    tar -xf Python-3.9.0.tgz
    cd Python-3.9.0
    ./configure --enable-optimizations
    make -j 2
    sudo make altinstall
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    /usr/local/bin/python3.9 get-pip.py
    /usr/local/bin/python3.9 -m pip install --upgrade pip
    sudo apt-get install -y s3cmd opus-tools ffmpeg
    mkdir ~/cama-community-staging/
ENDSSH

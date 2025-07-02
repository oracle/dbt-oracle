sudo apt-get update
sudo apt-get install wget libaio1t64
sudo mkdir -p /opt/oracle
wget https://download.oracle.com/otn_software/linux/instantclient/2370000/instantclient-basiclite-linux.x64-23.7.0.25.01.zip -P /tmp
sudo unzip /tmp/instantclient-basiclite-linux.x64-23.7.0.25.01.zip -d /opt/oracle
export PATH="$PATH:/opt/oracle/instantclient_23_7"
export LD_LIBRARY_PATH="/opt/oracle/instantclient_23_7:$LD_LIBRARY_PATH"
sudo ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
sudo mkdir -p /opt/tns_admin
echo "DISABLE_OOB=ON" >> /opt/tns_admin/sqlnet.ora


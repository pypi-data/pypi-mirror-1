#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <string.h>

#if defined(__linux__)
#include <sys/vfs.h>
#elif defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__APPLE__)
#include <sys/param.h>
#include <sys/mount.h>
#include <sys/socket.h>
#include <sys/sysctl.h>
#include <sys/time.h>
#include <net/if.h>
#include <ifaddrs.h>
#endif

/* internal interface information structure */
typedef struct {
    char name[32];
    int filled;
    uint64_t rx;
    uint64_t tx;
    uint64_t rxp;
    uint64_t txp;
} IFINFO;

IFINFO getifinfo(char iface[32]);
int readproc(char iface[32]);
int readsysclassnet(char iface[32]);
#if defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__APPLE__)
int readifaddrs(char iface[32]);
#endif


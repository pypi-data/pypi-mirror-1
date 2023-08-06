#include <Python.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <linux/sockios.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <net/route.h>

#include "netinfo.h"
#include "iface.h"
#include "route.h"

#define IF_COUNT 64

PyMethodDef netinfo_methods[] = {
    /* iface.h */
    {"list_devs",  netinfo_list_devs, METH_VARARGS, "List network devices"},
    {"list_active_devs",  netinfo_list_active_devs, METH_VARARGS, "List active network devices"},
    {"get_hwaddr",  netinfo_get_hwaddr, METH_VARARGS, "Get hardware address"},
    {"get_ip",  netinfo_get_ip, METH_VARARGS, "Get ip address"},
    {"get_netmask",  netinfo_get_netmask, METH_VARARGS, "Get network mask"},
    {"get_broadcast",  netinfo_get_broadcast, METH_VARARGS, "Get broadcast address"},
    {"get_routes",  netinfo_get_routes, METH_VARARGS, "Get routes"},
    {"set_state",  netinfo_set_state, METH_VARARGS, "Set device state (up/down)"},
    {"set_ip",  netinfo_set_ip, METH_VARARGS, "Set ip address"},
    {"set_netmask",  netinfo_set_netmask, METH_VARARGS, "Set network mask"},
    {"set_broadcast",  netinfo_set_broadcast, METH_VARARGS, "Set broadcast address"},
    /* route.h */
    {"add_route",  netinfo_add_route, METH_VARARGS, "Add route"},
    {"del_route",  netinfo_del_route, METH_VARARGS, "Delete route"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initnetinfo(void)
{
    (void) Py_InitModule("netinfo", netinfo_methods);
}


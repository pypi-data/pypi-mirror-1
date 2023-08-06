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

#include "netinfo.h"

#define IF_COUNT 64

static PyObject *netinfo_list_devs(PyObject *self, PyObject *args);
static PyObject *netinfo_get_hwaddr(PyObject *self, PyObject *args);
static PyObject *netinfo_list_active_devs(PyObject *self, PyObject *args);
static PyObject *netinfo_get_ip(PyObject *self, PyObject *args);
static PyObject *netinfo_get_netmask(PyObject *self, PyObject *args);
static PyObject *netinfo_get_broadcast(PyObject *self, PyObject *args);
static PyObject *netinfo_get_routes(PyObject *self, PyObject *args);

static PyMethodDef netinfo_methods[] = {
    {"list_devs",  netinfo_list_devs, METH_VARARGS, "List network devices"},
    {"list_active_devs",  netinfo_list_active_devs, METH_VARARGS, "List active network devices"},
    {"get_hwaddr",  netinfo_get_hwaddr, METH_VARARGS, "Get hardware address"},
    {"get_ip",  netinfo_get_ip, METH_VARARGS, "Get ip address"},
    {"get_netmask",  netinfo_get_netmask, METH_VARARGS, "Get network mask"},
    {"get_broadcast",  netinfo_get_broadcast, METH_VARARGS, "Get broadcast address"},
    {"get_routes",  netinfo_get_routes, METH_VARARGS, "Get routes"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyObject *netinfo_list_active_devs(PyObject *self, PyObject *args)
{
    int ret, fd;
    struct ifreq *ifr, *ifend;
    struct ifreq ifs[IF_COUNT];
    struct ifconf ifc;
    int i = 1;
    PyObject *tuple = PyTuple_New(0);

    fd = socket(PF_INET6, SOCK_DGRAM, IPPROTO_IP); /* open a socket to examine */
    if (ret < 0)
        return NULL;
    ifc.ifc_len = sizeof(ifs);
    ifc.ifc_req = ifs;

    ret = ioctl(fd, SIOCGIFCONF, &ifc);
    if (ret < 0)
        return NULL;
    ifend = ifs + (ifc.ifc_len / sizeof(struct ifreq));
    for (ifr = ifc.ifc_req; ifr < ifend; ifr++)
    {
//         printf("dev: %s\n", ifr->ifr_name);
        _PyTuple_Resize(&tuple, i);
        PyTuple_SET_ITEM(tuple, i++-1, Py_BuildValue("s", ifr->ifr_name));
    }
    return tuple;
}

static PyObject *netinfo_list_devs(PyObject *self, PyObject *args)
{
    FILE *devlist = fopen("/proc/net/dev", "r");
    char buffer[256], *c, *end;
    int i = 1;
    PyObject *tuple = PyTuple_New(0);
    while (fgets(buffer, 256, devlist)) {
        end = strchr(buffer, ':');
        if (!end)
            continue;
        *end = '\0';
        for (c = buffer; *c == ' '; c++) ;
//         printf("dev: %s\n", c);
        _PyTuple_Resize(&tuple, i);
        PyTuple_SET_ITEM(tuple, i++-1, Py_BuildValue("s", c));
    }
    return tuple;
}

static PyObject *netinfo_get_addr(PyObject *self, PyObject *args, int cmd)
{
    int ret, fd;
    struct ifreq ifreq;
    char *dev;
    struct sockaddr_in *sin;
    char hwaddr[18];
    fd = socket(AF_INET, SOCK_DGRAM, 0); /* open a socket to examine */
    if (ret < 0) {
        PyErr_SetFromErrno(PyExc_Exception);
        return NULL;
    }
    ret = PyArg_ParseTuple(args, "s", &dev); /* parse argument */
    if (!ret)
        return NULL;
    memset(&ifreq, 0, sizeof(struct ifreq));
    strncpy(ifreq.ifr_name, dev, IFNAMSIZ-1);
    ifreq.ifr_addr.sa_family = AF_INET;
    ret = ioctl(fd, cmd, &ifreq, sizeof(struct ifreq));
    if (ret < 0) {
        PyErr_SetFromErrno(PyExc_Exception);
        return NULL;
    }
    switch (cmd) {
        case SIOCGIFADDR:
            sin = (struct sockaddr_in *)&(ifreq.ifr_ifru.ifru_addr);
            return Py_BuildValue("s", inet_ntoa(sin->sin_addr));
        case SIOCGIFNETMASK:
            sin = (struct sockaddr_in *)&(ifreq.ifr_ifru.ifru_netmask);
            return Py_BuildValue("s", inet_ntoa(sin->sin_addr));
        case SIOCGIFBRDADDR:
            sin = (struct sockaddr_in *)&(ifreq.ifr_ifru.ifru_broadaddr);
            return Py_BuildValue("s", inet_ntoa(sin->sin_addr));
        case SIOCGIFHWADDR:
            snprintf(hwaddr, 18, "%02X:%02X:%02X:%02X:%02X:%02X", 
                        (unsigned char)ifreq.ifr_ifru.ifru_hwaddr.sa_data[0],
                        (unsigned char)ifreq.ifr_ifru.ifru_hwaddr.sa_data[1],
                        (unsigned char)ifreq.ifr_ifru.ifru_hwaddr.sa_data[2],
                        (unsigned char)ifreq.ifr_ifru.ifru_hwaddr.sa_data[3],
                        (unsigned char)ifreq.ifr_ifru.ifru_hwaddr.sa_data[4],
                        (unsigned char)ifreq.ifr_ifru.ifru_hwaddr.sa_data[5]);
            return Py_BuildValue("s", hwaddr);
    }
    
}

static PyObject *netinfo_get_ip(PyObject *self, PyObject *args)
{
    return netinfo_get_addr(self, args, SIOCGIFADDR);
}

static PyObject *netinfo_get_netmask(PyObject *self, PyObject *args)
{
    return netinfo_get_addr(self, args, SIOCGIFNETMASK);
}

static PyObject *netinfo_get_broadcast(PyObject *self, PyObject *args)
{
    return netinfo_get_addr(self, args, SIOCGIFBRDADDR);
}

static PyObject *netinfo_get_hwaddr(PyObject *self, PyObject *args)
{
    return netinfo_get_addr(self, args, SIOCGIFHWADDR);
}





static PyObject *netinfo_get_routes(PyObject *self, PyObject *args)
{
    char buffer[1024], *tok, *c;
    int field = 0, i = 1;
    PyObject *dict, *tuple = PyTuple_New(0);
    FILE *file = fopen("/proc/net/route", "r");
    if (!file) {
        PyErr_SetFromErrno(PyExc_Exception);
        return NULL;
    }
    fgets(buffer, 1024, file);
//     strtok_r(buffer, " \t", &tok);
    while (fgets(buffer, 1024, file)) {
        dict = PyDict_New();
        field = 0;
        while (c = strtok_r(field ? NULL : buffer, " \t", &tok)) {
            switch (field++) {
                case 0:
                    printf("iface: %s\n", c);
                    PyDict_SetItemString(dict, "iface", Py_BuildValue("s", c));
                    break;
                case 1:
                    printf("dest: %s\n", c);
                    PyDict_SetItemString(dict, "dest", Py_BuildValue("s", c));
                    break;
                case 2:
                    printf("gateway: %s\n", c);
                    PyDict_SetItemString(dict, "gateway", Py_BuildValue("s", c));
                    break;
                case 7:
                    printf("netmask: %s\n", c);
                    PyDict_SetItemString(dict, "netmask", Py_BuildValue("s", c));
                    break;
                default:
                    break;
            }
        }
        _PyTuple_Resize(&tuple, i);
        PyTuple_SET_ITEM(tuple, i++-1, dict);
    }
    return tuple;
}


PyMODINIT_FUNC initnetinfo(void)
{
    (void) Py_InitModule("netinfo", netinfo_methods);
}


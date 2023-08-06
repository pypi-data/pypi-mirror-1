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

// add_route(dev, destination, gateway, netmask)
PyObject *netinfo_adddel_route(PyObject *self, PyObject *args, int action)
{
    int ret, fd;
    char *dev, *dest, *gateway, *netmask;
    struct sockaddr_in *sin;
    struct rtentry rtentry;
    fd = socket(AF_INET, SOCK_DGRAM, 0); /* open a socket to examine */
    if (fd < 0) {
        PyErr_SetFromErrno(PyExc_Exception);
        return NULL;
    }
    ret = PyArg_ParseTuple(args, "ssss", &dev, &dest, &gateway, &netmask); /* parse argument */
    if (!ret)
        return NULL;
    /* set up route entry */ 
    memset(&rtentry, 0, sizeof(struct rtentry));
    if (strlen(dev) > 0) /* null if no device specified (os guesses) */
        rtentry.rt_dev = dev;
    rtentry.rt_metric = 1;
    rtentry.rt_flags = RTF_UP;
    /* build destination */
    rtentry.rt_dst.sa_family = AF_INET;
    sin = (struct sockaddr_in *)&rtentry.rt_dst;
    inet_aton(dest, &sin->sin_addr);
    /* build gateway */
    rtentry.rt_gateway.sa_family = AF_INET;
    sin = (struct sockaddr_in *)&rtentry.rt_gateway;
    inet_aton(gateway, &sin->sin_addr);
    if (sin->sin_addr.s_addr)
        rtentry.rt_flags |= RTF_GATEWAY;
    /* build netmask */
    rtentry.rt_genmask.sa_family = AF_INET;
    sin = (struct sockaddr_in *)&rtentry.rt_genmask;
    inet_aton(netmask, &sin->sin_addr);
    if (sin->sin_addr.s_addr != 0xFFFFFFFF)
        rtentry.rt_flags |= RTF_HOST;
    /* add route */
    ret = ioctl(fd, action ? SIOCADDRT : SIOCDELRT, &rtentry);
    if (ret < 0) {
        PyErr_SetFromErrno(PyExc_Exception);
        return NULL;
    }
    return Py_None;
}

PyObject *netinfo_add_route(PyObject *self, PyObject *args)
{
    netinfo_adddel_route(self, args, 1);
}

PyObject *netinfo_del_route(PyObject *self, PyObject *args)
{
    netinfo_adddel_route(self, args, 0);
}

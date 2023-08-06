/* iface.c */
PyObject *netinfo_list_active_devs(PyObject *self, PyObject *args);
PyObject *netinfo_list_devs(PyObject *self, PyObject *args);
PyObject *netinfo_get_addr(PyObject *self, PyObject *args, int cmd);
PyObject *netinfo_get_ip(PyObject *self, PyObject *args);
PyObject *netinfo_get_netmask(PyObject *self, PyObject *args);
PyObject *netinfo_get_broadcast(PyObject *self, PyObject *args);
PyObject *netinfo_get_hwaddr(PyObject *self, PyObject *args);
PyObject *netinfo_get_routes(PyObject *self, PyObject *args);
PyObject *netinfo_set_state(PyObject *self, PyObject *args);
PyObject *netinfo_set_addr(PyObject *self, PyObject *args, int cmd);
PyObject *netinfo_set_ip(PyObject *self, PyObject *args);
PyObject *netinfo_set_netmask(PyObject *self, PyObject *args);
PyObject *netinfo_set_broadcast(PyObject *self, PyObject *args);
PyObject *netinfo_adddel_route(PyObject *self, PyObject *args, int action);
PyObject *netinfo_add_route(PyObject *self, PyObject *args);
PyObject *netinfo_del_route(PyObject *self, PyObject *args);

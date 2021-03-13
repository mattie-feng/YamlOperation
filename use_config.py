# -*- coding:utf-8 -*-
import yaml_operation
import pprint


def node_practice():
    node_config = yaml_operation.NodeConfig("config.yaml")
    # pprint.pprint(node_config.get_all_node())
    pprint.pprint(node_config.get_all_node_list())
    pprint.pprint(node_config.get_all_node_num())


def host_practice():
    host_config = yaml_operation.HostGroupConfig("config.yaml")
    pprint.pprint(host_config.get_str_iqn("<Host_Group_Name_1>"))


def service_practice():
    service_config = yaml_operation.ServiceGroupConfig("config.yaml")
    pprint.pprint(service_config.get_available_pv("<Service_Group_Name_1>"))
    pprint.pprint(service_config.get_sp("<Service_Group_Name_1>"))


if __name__ == '__main__':
    # node_practice()
    # host_practice()
    service_practice()
    pass

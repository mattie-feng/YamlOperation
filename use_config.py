# -*- coding:utf-8 -*-
import yaml_operation
import pprint

file_name = "config.yaml"


def practice():
    config = yaml_operation.ClusterConfig(file_name)
    # pprint.pprint(config.get_shared_portal_via_sg("<Service_Group_Name_11>"))
    # pprint.pprint(config.get_node_list_via_sg("<Service_Group_Name_11>"))
    # config.get_network_segment()
    # pprint.pprint(config.get_str_iqn("<Host_Group_Name_1>"))
    pprint.pprint(config.get_available_pv_size("<Node_Name_1>","HDD"))
    pprint.pprint(config.get_sp_available_size("<Node_Name_1>", "HDD"))
    # pprint.pprint(config.get_sp("<Service_Group_Name_1>"))


def test():
    config = yaml_operation.PolicyConfig("prepare.yaml")
    file_type = config.get_file_type()
    if "Prepare" == file_type:
        config.write_prepare_into_cluster()
    elif "Strategy" == file_type:
        print("Other operation")


if __name__ == '__main__':
    practice()
    # host_practice()
    # service_practice()
    # test()

    pass

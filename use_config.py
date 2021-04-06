# -*- coding:utf-8 -*-
import yaml_operation
import pprint

file_name = "config.yaml"


def practice():
    config = yaml_operation.ClusterConfig(file_name)
    # pprint.pprint(config.get_shared_portal_via_sg("<Service_Group_Name_11>"))
    # pprint.pprint(config.get_node_list_via_sg("<Service_Group_Name_11>"))
    # config.get_network_segment()
    # pprint.pprint(config.get_member_list("Host_Group"))
    # pprint.pprint(config.get_str_iqn("<Host_Group_Name_1>"))
    # pprint.pprint(config.get_available_pv_size("<Node_Name_1>","HDD"))
    # pprint.pprint(config.get_sp_available_size("<Node_Name_1>", "hdd"))
    pprint.pprint(config.get_volume_by_sp_name("sp_hdd_29180391"))
    pprint.pprint(config.get_volume_by_sp_name("sp_<Node_Name>_hdd_<Storagepool_Name_2>"))

    # pprint.pprint(config.get_target_via_portal("<Portal_Name_1>"))
    # pprint.pprint(config.get_available_vip("xx.xx.x1.0"))

    # config.add_value_by_key("VIP_Pool", "pool_xx_xx_x1_0", "available", value="xx.xx.xx.6")
    # config.add_value_by_key("Host_Group", value={"H3": ["a", "b"]})
    # config.add_value_by_key("Host_Group", "H3", value="f")
    # config.delete_value_by_key("Host_Group","H3")
    # config.delete_value_in_list("Host_Group", "H3", value="c")

    # pprint.pprint(config.get_sp("<Service_Group_Name_1>"))


def test():
    # config = yaml_operation.PolicyConfig("sg.yaml")
    config = yaml_operation.PolicyConfig("hg.yaml")
    # config = yaml_operation.PolicyConfig("vip.yaml")
    config2 = yaml_operation.ClusterConfig(file_name)
    kind = config.get_kind()
    creation_config = config.get_creation()
    # print(creation_config)
    if "Service Group" == kind:
        for sg in creation_config:
            config2.write_sg_into_cluster(sg["group_name"], sg["node"])
    if "Host Group" == kind:
        for hg in creation_config:
            config2.write_hg_into_cluster(hg["group_name"], hg["host_iqn"])
    if "VIP Pool" == kind:
        for vip in creation_config:
            config2.write_vip_pool_into_cluster(vip["network_segment"], vip["tag"], vip["ip"])


if __name__ == '__main__':
    practice()
    # host_practice()
    # service_practice()
    # test()

    # pass

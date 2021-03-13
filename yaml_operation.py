# -*- coding:utf-8 -*-
import pprint
import yaml


class NodeConfig(object):

    def __init__(self, yaml_file):
        self.config = YamlOperation(yaml_file)

    def get_all_node(self):
        node_dict = self.config.get_all_config()["Node"]
        return node_dict

    def get_all_node_list(self):
        all_node = self.config.get_value_by_key("Node").keys()
        return list(all_node)

    def get_all_node_num(self):
        node_len = self.config.get_length("Node")
        return node_len


class HostGroupConfig(object):
    def __init__(self, yaml_file):
        self.config = YamlOperation(yaml_file)

    def get_str_iqn(self, host_group):
        """通过HostGroup名字获取到对应的IQN字符串"""
        list_iqn = self.config.get_value_by_key("Host_Group", "<Host_Group_Name_1>")
        str_initiator_iqn = ' '.join(list_iqn)
        return str_initiator_iqn


class ServiceGroupConfig(object):
    def __init__(self, yaml_file):
        self.config = YamlOperation(yaml_file)

    def get_available_pv(self, service_group):
        """获取服务组的全部PV"""
        node_list = self.config.get_value_by_key("Service_Group", service_group, "node")
        available_pv = []
        if node_list:
            for node in node_list:
                available_pv.append({node: self.config.get_value_by_key("Node", node, "pv", "available")})
            return available_pv
        else:
            print("Can't get available PV via ", service_group)

    def get_sp(self, service_group):
        """获取服务组的全部Storagepool"""
        node_list = self.config.get_value_by_key("Service_Group", service_group, "node")
        all_sp = []
        if node_list:
            for node in node_list:
                all_sp.append({node: self.config.get_value_by_key("Node", node, "storagepool")})
            return all_sp
        else:
            print("Can't get Storagepool via ", service_group)


class YamlOperation(object):

    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.yaml_dict = self.read_yaml()

    # 读YAML文件，没有就进行创建
    def read_yaml(self):
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                yaml_dict = yaml.safe_load(f)
            return yaml_dict
        except FileNotFoundError:
            print("Please check the file name:", self.yaml_file)
        except TypeError:
            print("Error in the type of file name.")

    def get_all_config(self):
        return self.yaml_dict

    # 更新文件内容
    def update_yaml(self, dict_a):
        with open(self.yaml_file, 'w', encoding='utf-8') as f:
            # yaml.dump(dict_a, f, default_flow_style=False)
            yaml.dump(dict_a, f)

    def delete_value_by_key(self, *key_tuple):
        key_value = self.yaml_dict
        for key in key_tuple:
            if key == key_tuple[-1]:
                del key_value[key_tuple[-1]]
                break
            key_value = key_value[key]
        self.update_yaml(self.yaml_dict)

    def modify_value_by_key(self, *key_tuple, value):
        key_value = self.yaml_dict
        for key in key_tuple:
            if key == key_tuple[-1]:
                key_value[key_tuple[-1]] = value
            key_value = key_value[key]
        self.update_yaml(self.yaml_dict)

    def get_value_by_key(self, *key_tuple):
        value = self.yaml_dict
        try:
            for key in key_tuple:
                if key in value.keys():
                    value = value[key]
                else:
                    print("Error key!")
                    return False
            return value
        except AttributeError:
            print("Error key!!")

    def get_length(self, *value):
        try:
            return len(self.get_value_by_key(*value))
        except TypeError:
            print("Failed to get length.")

    # def create_init_yaml_config(self):
    #
    #     init_yaml_config = '''
    #     Host_Group:
    #     Service_Group:
    #     Cluster:
    #       Node:
    #       VIP_Pool:
    #     DRBD:
    #     Portal:
    #     Target:
    #     iLU:
    #     '''
    #
    #     self.yaml_dict = yaml.safe_load(init_yaml_config)
    #     self.update_yaml(self.yaml_dict)


# 通过conf.yaml配置文件获取到conf1.yaml配置文件中的配置
def read_conf_from_file():
    config1 = YamlOperation("conf.yaml")
    host_file = config1.get_value_by_key("Host_Group")

    config2 = YamlOperation(host_file)
    pprint.pprint(config2.read_yaml())
    pprint.pprint(config2.get_length("Host_Group"))


if __name__ == '__main__':
    config = YamlOperation("conf.yaml")
    config2 = YamlOperation("conf.yaml")

    # pprint.pprint(config.read_yaml())

    # pprint.pprint(config.get_value_by_key("Storagepool"))

    # pprint.pprint(type(config.get_value_by_key("Storagepool", "<Node_Name>_<Storagepool_Name_1>", "size")))
    # pprint.pprint(config.get_value_by_key("Node", "<Node_Name_1>", "pv"))

    # print(config.get_length("Host_Group", "HG1"))
    # print(config.get_length("Node"))

    # read_conf_from_file()

    # config.modify_value_by_key("Service_Group", "SG2", "node", value=['N1', 'N4', 'N5', 'N6'])
    # config2.modify_value_by_key("Service_Group", "SG2", "node", value=['N1', 'N5', 'N5', 'N6'])
    # config.modify_value_by_key("Storagepool", "<Node_Name>_<Storagepool_Name_2>", "used_size", value=None)
    # config.delete_value_by_key("Service_Group", "SG2")
    pass

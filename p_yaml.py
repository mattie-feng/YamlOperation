# -*- coding:utf-8 -*-
import pprint
import yaml


class YamlOperation(object):
    yaml_dict = None

    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        if self.yaml_dict is None:
            self.yaml_dict = self.read_yaml()

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

    def create_init_yaml_config(self):

        init_yaml_config = '''
        Host_Group:
        Service_Group:
        Cluster:
          Node:
          VIP_Pool:
        DRBD:
        Portal:
        Target:
        iLU:
        '''

        self.yaml_dict = yaml.safe_load(init_yaml_config)
        self.update_yaml(self.yaml_dict)

    # 更新文件内容
    def update_yaml(self, dict_a):
        with open(self.yaml_file, 'w', encoding='utf-8') as f:
            # yaml.dump(dict_a, f, default_flow_style=False)
            yaml.dump(dict_a, f)

    # 读YAML文件，没有就进行创建
    def read_yaml(self):
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                dict_yaml = yaml.safe_load(f)
            return dict_yaml
        except FileNotFoundError:
            self.create_init_yaml_config()
        except TypeError:
            print("Can't read file")


# 通过conf.yaml配置文件获取到conf1.yaml配置文件中的配置
def read_conf_from_file():
    config = YamlOperation("conf.yaml")
    host_file = config.get_value_by_key("Host_Group")

    config2 = YamlOperation(host_file)
    pprint.pprint(config2.read_yaml())
    pprint.pprint(config2.get_length("Host_Group"))


if __name__ == '__main__':
    # config = YamlOperation("conf2.yaml")

    # pprint.pprint(config.read_yaml())

    # pprint.pprint(config.get_value_by_key("Host_Group1"))
    # pprint.pprint(config.get_value_by_key("Service_Group", "SG1", "node"))

    # print(config.get_length("Host_Group", "HG1"))

    # read_conf_from_file()

    # config.modify_value_by_key("Service_Group", "SG2", "node", value=['N1', 'N2', 'N5', 'N6'])
    # config.delete_value_by_key("Service_Group", "SG2")
    pass

# -*- coding:utf-8 -*-
import pprint
import yaml


def get_vip_pool_name(str):
    vip_pool_name = "pool_" + "_".join(str.split("."))
    return vip_pool_name


class YamlOperation(object):
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file

    # 读YAML文件
    def read_yaml(self):
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                yaml_dict = yaml.safe_load(f)
            return yaml_dict
        except FileNotFoundError:
            print("Please check the file name:", self.yaml_file)
        except TypeError:
            print("Error in the type of file name.")

    # 更新文件内容
    def update_yaml(self, dict_a):
        with open(self.yaml_file, 'w', encoding='utf-8') as f:
            # yaml.dump(dict_a, f, default_flow_style=False)
            yaml.dump(dict_a, f)

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
    #     yaml_dict = yaml.safe_load(init_yaml_config)
    #     self.update_yaml(yaml_dict)


class ClusterConfig(YamlOperation):

    def __init__(self, yaml_file):
        super().__init__(yaml_file)
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

    def get_all_node_list(self):
        all_node = self.get_value_by_key("Node").keys()
        return list(all_node)

    def get_all_node_num(self):
        node_len = self.get_length("Node")
        return node_len

    def get_str_iqn(self, host_group):
        """通过HostGroup名字获取到对应的IQN字符串"""
        list_iqn = self.get_value_by_key("Host_Group", "<Host_Group_Name_1>")
        str_initiator_iqn = ' '.join(list_iqn)
        return str_initiator_iqn

    def get_available_pv(self, service_group):
        """获取服务组的全部PV"""
        node_list = self.get_value_by_key("Service_Group", service_group, "node")
        available_pv = []
        if node_list:
            for node in node_list:
                available_pv.append({node: self.get_value_by_key("Node", node, "pv", "available")})
            return available_pv
        else:
            print("Can't get available PV via ", service_group)

    def get_sp(self, service_group):
        """获取服务组的全部Storagepool"""
        node_list = self.get_value_by_key("Service_Group", service_group, "node")
        all_sp = []
        if node_list:
            for node in node_list:
                all_sp.append({node: self.get_value_by_key("Node", node, "storagepool")})
            return all_sp

    def get_all_sg_list(self):
        all_sg = self.get_value_by_key("Service_Group").keys()
        return list(all_sg)

    def get_network_segment(self):
        """获取文件的Kind字段，读取文件的类型"""
        list_network = []
        all_vip_pool = self.get_value_by_key("VIP_Pool").keys()
        for vip_pool in all_vip_pool:
            list_network.append(self.get_value_by_key("VIP_Pool", vip_pool, "network_segment"))
        return list_network

    # def get_available_vip_via_network_segment(self, str):
    #     """获取文件的Kind字段，读取文件的类型"""
    #     list_available_vip = []
    #     all_vip_pool = self.get_value_by_key("VIP_Pool").keys()
    #     for vip_pool in all_vip_pool:
    #         if vip_pool["network_segment"] == str:
    #             list_available_vip.append(self.get_value_by_key("VIP_Pool", vip_pool, "available"))
    #     print(list_available_vip)
    #     return list_available_vip


class StrategyConfig(YamlOperation):
    def __init__(self, yaml_file):
        super().__init__(yaml_file)
        self.yaml_dict = self.read_yaml()

    def get_file_type(self):
        """获取文件的Kind字段，读取文件的类型"""
        try:
            if self.yaml_dict["Kind"]:
                return self.yaml_dict["Kind"]
            else:
                print("Missing value of 'Kind'")
        except KeyError:
            print("Missing 'Kind'")

    # 读预准备配置文件，将其写到集群配置文件
    def write_prepare_into_cluster(self):
        """读取预准备文件的信息，更新到集群配置文件中"""
        cluster_file = self.yaml_dict["Cluster"]
        cluster_config = ClusterConfig(cluster_file)

        # self.write_sg_into_cluster(cluster_config)
        # self.write_hg_into_cluster(cluster_config)
        self.write_vip_pool_into_cluster(cluster_config)

    def write_sg_into_cluster(self, cluster_config):
        """读取预准备文件的服务组组信息，更新到集群配置文件中"""
        try:
            prepare_sg = self.yaml_dict["Service Group"]
            cluster_dict = cluster_config.read_yaml()
            sg_dict = {}
            for sg in prepare_sg:
                if sg["group_name"] in cluster_dict["Service_Group"].keys():
                    print(sg["group_name"], "already exists")
                else:
                    str = f'''
                    {sg["group_name"]}: 
                      node: {sg["node"]}
                      shared_portal: 
                      dedicate_portal: 
                      resource_set: 
                    '''
                    dict = yaml.safe_load(str)
                    sg_dict.update(dict)
            cluster_sg = cluster_config.get_value_by_key("Service_Group")
            cluster_sg.update(sg_dict)
            cluster_config.modify_value_by_key("Service_Group", value=cluster_sg)
        except(KeyError, TypeError):
            pass

    def write_hg_into_cluster(self, cluster_config):
        """读取预准备文件的主机组信息，更新到集群配置文件中"""
        try:
            prepare_hg = self.yaml_dict["Host Group"]
            cluster_dict = cluster_config.read_yaml()
            hg_dict = {}
            for hg in prepare_hg:
                if hg["group_name"] in cluster_dict["Host_Group"].keys():
                    print(hg["group_name"], "already exists")
                else:
                    hg_dict.update({hg["group_name"]: hg["host_iqn"]})
            cluster_hg = cluster_config.get_value_by_key("Host_Group")
            cluster_hg.update(hg_dict)
            cluster_config.modify_value_by_key("Host_Group", value=cluster_hg)
        except(KeyError, TypeError):
            pass

    def write_vip_pool_into_cluster(self, cluster_config):
        """读取预准备文件的VIP池信息，更新到集群配置文件中"""
        try:
            prepare_vip_pool = self.yaml_dict["VIP Pool"]
            cluster_dict = cluster_config.read_yaml()
            network_segment = cluster_config.get_network_segment()
            sg_dict = {}
            for vip_pool in prepare_vip_pool:
                if vip_pool["network_segment"] in network_segment:
                    for ip in vip_pool["IP"]:
                        # vip_pool_name = get_vip_pool_name(ip)
                        vip_pool_name = "<VIP_Pool_Name_1>"
                        if ip in cluster_config.get_value_by_key("VIP_Pool", vip_pool_name, "available"):
                            print(ip, "already exists")
                        elif ip in cluster_config.get_value_by_key("VIP_Pool", vip_pool_name, "used"):
                            print(ip, "already in use")
                        else:
                            list_available_ip = cluster_config.get_value_by_key("VIP_Pool", vip_pool_name, "available")
                            list_available_ip.append(ip)
                            cluster_config.modify_value_by_key("VIP_Pool", vip_pool_name, "available",
                                                               value=list_available_ip)
                else:
                    str = f'''{get_vip_pool_name(vip_pool["network_segment"])}: 
                        network_segment: {vip_pool["network_segment"]}
                        tag: {vip_pool["tag"]}
                        available: {vip_pool["IP"]} 
                        used: 
                    '''
                    dict = yaml.safe_load(str)
                    sg_dict.update(dict)
            # print(sg_dict)
            cluster_sg = cluster_config.get_value_by_key("VIP_Pool")
            cluster_sg.update(sg_dict)
            cluster_config.modify_value_by_key("VIP_Pool", value=cluster_sg)
        except(KeyError, TypeError):
            pass

    if __name__ == '__main__':
        pass

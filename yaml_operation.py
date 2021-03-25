# -*- coding:utf-8 -*-
import pprint
import yaml


def get_vip_pool_name(str):
    """通过传进来的网段组成VIP池的名称"""
    vip_pool_name = "pool_" + "_".join(str.split("."))
    return vip_pool_name


class YamlOperation(object):
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file

    def read_yaml(self):
        """读YAML文件"""
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                yaml_dict = yaml.safe_load(f)
            return yaml_dict
        except FileNotFoundError:
            print("Please check the file name:", self.yaml_file)
        except TypeError:
            print("Error in the type of file name.")

    def update_yaml(self, dict_a):
        """更新文件内容"""
        with open(self.yaml_file, 'w', encoding='utf-8') as f:
            # yaml.dump(dict_a, f, default_flow_style=False)
            yaml.dump(dict_a, f)


class ClusterConfig(YamlOperation):

    def __init__(self, yaml_file):
        super().__init__(yaml_file)
        self.yaml_dict = self.read_yaml()

    def get_value_by_key(self, *key_tuple):
        """根据传进来的Key，获取对应的value值"""
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
        """根据传进来的Key，获取对应的value值的长度"""
        try:
            return len(self.get_value_by_key(*value))
        except TypeError:
            print("Failed to get length.")

    def delete_value_by_key(self, *key_tuple):
        """根据传进来的Key，删除对应的value值"""
        key_value = self.yaml_dict
        for key in key_tuple:
            if key == key_tuple[-1]:
                del key_value[key_tuple[-1]]
                break
            key_value = key_value[key]
        self.update_yaml(self.yaml_dict)

    def delete_value_in_list(self, *key_tuple, value):
        config_value = self.get_value_by_key(*key_tuple)
        if config_value:
            if type(config_value) is list:
                config_value.remove(value)
                self.modify_value_by_key(*key_tuple, value=config_value)

    def modify_value_by_key(self, *key_tuple, value):
        """根据传进来的Key，修改对应的value值"""
        key_value = self.yaml_dict
        for key in key_tuple:
            if key == key_tuple[-1]:
                key_value[key_tuple[-1]] = value
            key_value = key_value[key]
        self.update_yaml(self.yaml_dict)

    def add_value_by_key(self, *key_tuple, value):
        config_value = self.get_value_by_key(*key_tuple)
        if config_value:
            if type(config_value) is list:
                config_value.append(value)
                self.modify_value_by_key(*key_tuple, value=config_value)
            elif type(config_value) is dict:
                config_value.update(value)
                self.modify_value_by_key(*key_tuple, value=config_value)
        else:
            if type(value) is dict:
                self.modify_value_by_key(*key_tuple, value=value)
            else:
                self.modify_value_by_key(*key_tuple, value=[value])

    def get_member_list(self, key):
        """获取集群中对应资源的所有成员，返回列表"""
        all_member = self.get_value_by_key(key).keys()
        return list(all_member)

    def get_all_member_num(self, key):
        """获取集群中对应资源的所有成员的数量"""
        member_len = self.get_length(key)
        return member_len

    def get_node_list_via_sg(self, sg):
        """通过服务组名得到该服务组的节点列表"""
        node_list = self.get_value_by_key("Service_Group", sg, "node")
        return list(node_list)

    def get_shared_portal_via_sg(self, sg):
        """通过服务组名得到该服务组的共享Portal"""
        shared_portal = self.get_value_by_key("Service_Group", sg, "shared_portal")
        return shared_portal

    def get_str_iqn(self, host_group):
        """通过HostGroup名字获取到对应的IQN字符串"""
        list_iqn = self.get_value_by_key("Host_Group", "<Host_Group_Name_1>")
        str_initiator_iqn = ' '.join(list_iqn)
        return str_initiator_iqn

    def get_available_pv_size(self, node, type):
        """获取节点上对应类型的全部可用PV以及剩余空间"""
        available_pv = {}
        try:
            pv_available = self.get_value_by_key("Node", node, "pv", "available")
            for pv in pv_available:
                pv_type = self.get_value_by_key("PV", pv, "type")
                if type == pv_type:
                    pv_size = self.get_value_by_key("PV", pv, "size")
                    available_pv.update({pv: pv_size})
            return available_pv
        except TypeError:
            pass

    def get_sp_available_size(self, node, type):
        """获取节点上对应类型的全部Storagepool以及剩余空间"""

        all_sp = {}
        try:
            sp_list = self.get_value_by_key("Node", node, "storagepool")
            for sp in sp_list:
                if type in sp:
                    size = self.get_value_by_key("Storagepool", sp, "size")
                    used_size = self.get_value_by_key("Storagepool", sp, "used_size")
                    available_size = size - used_size
                    all_sp.update({sp: available_size})
            return all_sp
        except TypeError:
            pass

    def get_network_segment(self):
        """读取集群中的全部VIP网段，返回列表"""
        list_network = []
        all_vip_pool = self.get_member_list("VIP_Pool")
        for vip_pool in all_vip_pool:
            list_network.append(self.get_value_by_key("VIP_Pool", vip_pool, "network_segment"))
        return list_network

    def get_target_via_portal(self, portal):
        list_target = self.get_value_by_key("Portal", portal, "target")
        return list_target

    def get_available_vip(self, network_segment):
        """获取一个可用的VIP，并将其移到已使用的分类下"""
        list_network = self.get_network_segment()
        if network_segment in list_network:
            vip_pool = get_vip_pool_name(network_segment)
            list_available_vip = self.get_value_by_key("VIP_Pool", vip_pool, "available")
            if list_available_vip:
                available_vip = list_available_vip.pop()
                self.add_value_by_key("VIP_Pool", vip_pool, "available", value=available_vip)
                self.delete_value_in_list("VIP_Pool", vip_pool, "used", value=available_vip)
                return available_vip
            else:
                print("Can't get available vip.")

    # def get_all_vip_via_segment(self, segment):
    #     """根据网段获取到该网段下的全部VIP"""
    #     vip_pool_name = get_vip_pool_name(segment)
    #     available_vip = self.get_value_by_key("VIP_Pool", vip_pool_name, "available")
    #     used_vip = self.get_value_by_key("VIP_Pool", vip_pool_name, "used")
    #     if available_vip and used_vip is not None:
    #         available_vip.extend(used_vip)
    #         return available_vip
    #     elif available_vip:
    #         return available_vip
    #     elif used_vip:
    #         return used_vip

    def write_sg_into_cluster(self, group_name, list_node):
        """读取服务组信息，更新到集群配置文件中"""
        try:
            str = f'''
            {group_name}: 
              node: {list_node}
              shared_portal: 
              dedicate_portal: []
              resource_set: []
            '''
            dict = yaml.safe_load(str)
            self.add_value_by_key("Service_Group", value=dict)
            print("Success in creating Service Group:", group_name)
        except(KeyError, TypeError):
            pass

    def write_hg_into_cluster(self, group_name, list_iqn):
        """读取主机组信息，更新到集群配置文件中"""
        try:
            hg_dict = {group_name: list_iqn}
            self.add_value_by_key("Host_Group", value=hg_dict)
            print("Success in creating Host Group:", group_name)
        except(KeyError, TypeError):
            pass

    def write_vip_pool_into_cluster(self, segment, tag, list_ip):
        """读取VIP池信息，更新到集群配置文件中"""
        try:
            # prepare_vip_pool = self.yaml_dict["VIP Pool"]
            # cluster_dict = cluster_config.read_yaml()
            # network_segment = cluster_config.get_network_segment()
            # sg_dict = {}
            # for vip_pool in prepare_vip_pool:
            #     if vip_pool["network_segment"] in network_segment:
            #         for ip in vip_pool["IP"]:
            #             # vip_pool_name = get_vip_pool_name(ip)
            #             vip_pool_name = "<VIP_Pool_Name_1>"
            #             if ip in cluster_config.get_value_by_key("VIP_Pool", vip_pool_name, "available"):
            #                 print(ip, "already exists")
            #             elif ip in cluster_config.get_value_by_key("VIP_Pool", vip_pool_name, "used"):
            #                 print(ip, "already in use")
            #             else:
            #                 list_available_ip = cluster_config.get_value_by_key("VIP_Pool", vip_pool_name, "available")
            #                 list_available_ip.append(ip)
            #                 cluster_config.modify_value_by_key("VIP_Pool", vip_pool_name, "available",
            #                                                    value=list_available_ip)
            vip_pool_name = get_vip_pool_name(segment)
            str = f'''
            {vip_pool_name}: 
              network_segment: {segment}
              tag: {tag}
              available: {list_ip} 
              used: []
            '''
            dict = yaml.safe_load(str)
            self.add_value_by_key("VIP_Pool", value=dict)
            print("Success in create VIP Pool:", vip_pool_name)
        except(KeyError, TypeError):
            pass


class PolicyConfig(YamlOperation):
    def __init__(self, yaml_file):
        super().__init__(yaml_file)
        self.yaml_dict = self.read_yaml()

    def get_kind(self):
        """读取文件的Kind字段，返回文件类型"""
        try:
            if self.yaml_dict["Kind"]:
                return self.yaml_dict["Kind"]
            else:
                print("Missing value of 'Kind'")
        except (KeyError, TypeError):
            print("Missing 'Kind'")

    def get_creation(self):
        """读取文件的Creation字段，返回列表"""
        try:
            if self.yaml_dict["Creation"]:
                return self.yaml_dict["Creation"]
        except KeyError:
            print("Missing config which is used to create resource.")

    if __name__ == '__main__':
        pass

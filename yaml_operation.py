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
                    return
            return value
        except (AttributeError, TypeError):
            pass

    def get_length(self, *value):
        """根据传进来的Key，获取对应的value值的长度"""
        try:
            return len(self.get_value_by_key(*value))
        except TypeError:
            print("Failed to get length.")

    def modify_value_by_key(self, *key_tuple, value):
        """根据传进来的Key，修改对应的value值"""
        key_value = self.yaml_dict
        for key in key_tuple:
            if key == key_tuple[-1]:
                key_value[key_tuple[-1]] = value
            key_value = key_value[key]
        self.update_yaml(self.yaml_dict)

    def delete_value_by_key(self, *key_tuple):
        """根据传进来的Key，删除对应的字典"""
        key_value = self.yaml_dict
        for key in key_tuple:
            if key == key_tuple[-1]:
                del key_value[key_tuple[-1]]
                break
            key_value = key_value[key]
        self.update_yaml(self.yaml_dict)

    def delete_value_in_list(self, *key_tuple, value):
        """根据传进来的Key，删除对应的列表中的某个值"""
        config_value = self.get_value_by_key(*key_tuple)
        if config_value:
            if type(config_value) is list:
                config_value.remove(value)
                self.modify_value_by_key(*key_tuple, value=config_value)

    def add_value_by_key(self, *key_tuple, value):
        """根据传进来的Key，添加某个值到对应的字典或者列表中"""
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
        """根据资源类型，获取集群中对应资源的所有成员，返回列表"""
        try:
            all_member = self.get_value_by_key(key).keys()
            return list(all_member)
        except TypeError:
            pass

    def get_all_member_num(self, key):
        """根据资源类型，获取集群中对应资源的所有成员的数量"""
        try:
            member_len = self.get_length(key)
            return member_len
        except TypeError:
            pass

    def get_node_list_via_sg(self, sg):
        """通过服务组名得到该服务组的节点列表"""
        try:
            node_list = self.get_value_by_key("Service_Group", sg, "node")
            return list(node_list)
        except TypeError:
            pass

    def get_shared_portal_via_sg(self, sg):
        """通过服务组名得到该服务组的共享Portal"""
        try:
            shared_portal = self.get_value_by_key("Service_Group", sg, "shared_portal")
            return shared_portal
        except TypeError:
            pass

    def get_str_iqn(self, host_group):
        """通过HostGroup名字获取到对应的IQN字符串"""
        try:
            list_iqn = self.get_value_by_key("Host_Group", host_group)
            str_initiator_iqn = ' '.join(list_iqn)
            return str_initiator_iqn
        except TypeError:
            pass

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
        """获取节点上对应类型的全部Storagepool以及剩余空间（以及是否是limited）"""

        all_sp = {"sp_limited": {}, "sp_normal": {}}
        try:
            sp_list = self.get_value_by_key("Node", node, "storagepool")
            for sp in sp_list:
                if type in sp:
                    size = self.get_value_by_key("Storagepool", sp, "size")
                    used_size = self.get_value_by_key("Storagepool", sp, "used_size")
                    available_size = size - used_size
                    limited_type = self.get_value_by_key("Storagepool", sp, "limited")
                    if limited_type is True:
                        all_sp["sp_limited"].update({sp: available_size})
                    elif limited_type is False:
                        all_sp["sp_normal"].update({sp: available_size})
            return all_sp
        except TypeError:
            pass

    def get_volume_by_sp_name(self, sp_name):
        """根据存储池的名称获取到其使用的volume名"""
        try:
            volume = self.get_value_by_key("Storagepool", sp_name, "volume")
            return volume
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
        try:
            list_target = self.get_value_by_key("Portal", portal, "target")
            return list_target
        except TypeError:
            pass

    def get_available_vip(self, vip_pool_name):
        """根据VIP池的名称从VIP池获取到一个可用的VIP"""
        try:
            list_available_vip = self.get_value_by_key("VIP_Pool", vip_pool_name, "available")
            if list_available_vip:
                available_vip = list_available_vip[0]
                return available_vip
            else:
                print("Can't get available vip.")
        except TypeError:
            pass

    def mark_vip_as_used(self, vip_pool_name, vip):
        """根据VIP池的名称和VIP，将该VIP从可选部分移到已使用部分"""
        try:
            self.delete_value_in_list("VIP_Pool", vip_pool_name, "available", value=vip)
            self.add_value_by_key("VIP_Pool", vip_pool_name, "used", value=vip)
        except Exception:
            pass

    def write_sg_into_cluster(self, group_name, list_node):
        """更新服务组配置到数据库中"""
        try:
            str = f'''
            {group_name}: 
              node: {list_node}
              shared_portal: 
              dedicate_portal: []
              resource_set: []
            '''
            dict_sg = yaml.safe_load(str)
            self.add_value_by_key("Service_Group", value=dict_sg)
            print("Success in creating Service Group:", group_name)
        except(KeyError, TypeError):
            pass

    def write_hg_into_cluster(self, group_name, list_iqn):
        """更新主机组配置到数据库中"""
        try:
            dict_hg = {group_name: list_iqn}
            self.add_value_by_key("Host_Group", value=dict_hg)
            print("Success in creating Host Group:", group_name)
        except(KeyError, TypeError):
            pass

    def write_vip_pool_into_cluster(self, vip_pool_name, segment, tag, list_ip):
        """更新VIP池配置到数据库中"""
        try:
            # vip_pool_name = get_vip_pool_name(segment)
            str = f'''
            {vip_pool_name}: 
              network_segment: {segment}
              tag: {tag}
              available: {list_ip} 
              used: []
            '''
            dict_vip_pool = yaml.safe_load(str)
            self.add_value_by_key("VIP_Pool", value=dict_vip_pool)
            print("Success in creating VIP Pool:", vip_pool_name)
        except(KeyError, TypeError):
            pass

    # def write_sp_into_cluster(self, name):
    #     """更新Storagepool配置到数据库中"""
    #     try:
    #         str = f'''
    #                 {name}:
    #                 '''
    #         dict_sp = yaml.safe_load(str)
    #         self.add_value_by_key("Storagepool", value=dict_sp)
    #     except(KeyError, TypeError):
    #         pass
    #
    # def write_mirror_into_cluster(self, name):
    #     """更新Mirror配置到数据库中"""
    #     try:
    #         str = f'''
    #                 {name}:
    #
    #                 '''
    #         dict_mirror = yaml.safe_load(str)
    #         self.add_value_by_key("Mirror", value=dict_mirror)
    #     except(KeyError, TypeError):
    #         pass
    #
    # def write_portal_into_cluster(self, name):
    #     """更新Portal配置到数据库中"""
    #     try:
    #         str = f'''
    #                 {name}:
    #                 '''
    #         dict_portal = yaml.safe_load(str)
    #         self.add_value_by_key("Portal", value=dict_portal)
    #     except(KeyError, TypeError):
    #         pass
    #
    # def write_target_into_cluster(self, name):
    #     """更新Target配置到数据库中"""
    #     try:
    #         str = f'''
    #                 {name}:
    #                 '''
    #         dict_target = yaml.safe_load(str)
    #         self.add_value_by_key("Target", value=dict_target)
    #     except(KeyError, TypeError):
    #         pass
    #
    # def write_ilu_into_cluster(self, name):
    #     """更新iSCSILogicalUnit配置到数据库中"""
    #     try:
    #         str = f'''
    #                 {name}:
    #                 '''
    #         dict_ilu = yaml.safe_load(str)
    #         self.add_value_by_key("iLU", value=dict_ilu)
    #     except(KeyError, TypeError):
    #         pass
    #
    # def write_resource_set_into_cluster(self, name, list_resource, host_group, ):
    #     """更新Resource Set配置到数据库中"""
    #     try:
    #         str = f'''
    #                 {name}:
    #                     resource:
    #                     host_group:
    #                     servie_group:
    #                         name:
    #                         portal_type:
    #                         portal:
    #                         target:
    #                 '''
    #         dict_resource_set = yaml.safe_load(str)
    #         self.add_value_by_key("Resource_Set", value=dict_resource_set)
    #     except(KeyError, TypeError):
    #         pass


class PolicyConfig(YamlOperation):
    def __init__(self, yaml_file):
        super().__init__(yaml_file)
        self.yaml_dict = self.read_yaml()

    def get_kind(self):
        """读取文件的Kind字段，返回文件类型"""
        try:
            if self.yaml_dict["Kind"]:
                return self.yaml_dict["Kind"]
        except (KeyError, TypeError):
            print("Missing config of 'Kind'")

    def get_creation(self):
        """读取文件的Creation字段，返回列表"""
        try:
            if self.yaml_dict["Creation"]:
                return self.yaml_dict["Creation"]
        except KeyError:
            print("Missing config of 'Creation'")


if __name__ == '__main__':
    pass

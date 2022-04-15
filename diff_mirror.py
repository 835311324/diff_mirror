
import os
import collections
import rpmfile
import json
import argparse

def get_rpm_info(rf):
    r=collections.namedtuple('rpm', ['name', 'arch','version'])
    try:
        with rpmfile.open(rf) as rpm:
            r.arch = rpm.headers.get('arch').decode("utf-8")
            r.name = rpm.headers.get('name').decode("utf-8")
            r.version = rpm.headers.get('version').decode("utf-8")
    except:
        return  None

    return r

def get_rpm_list(rpm_dir_path):
    rpm_list = []
    rpm_file_paths = get_rpm_file_paths(rpm_dir_path)
    for rpm_file in rpm_file_paths:
        r = get_rpm_info(rpm_file)
        if r == None:
            continue
        ele="{}/{}".format(r.name,r.version)
        if ele not in rpm_list:
            rpm_list.append(ele)
    return rpm_list

def diff_rpm_list(rpm_list1,rpm_list2):
    data={
        "version_not_match": {},
        "rpm_list1_only_exist": [],
        "rpm_list2_only_exist": [],
        "match":[]
    }
    for r1 in rpm_list1:
        for i,r2 in enumerate(rpm_list2):
            # 名字与版本都不同
            if r1!=r2:
                # 名字相同 版本不同
                if os.path.dirname(r1)==os.path.dirname(r2):
                    data['version_not_match'][os.path.dirname(r1)]=[r1,r2]
                    break

                # 遍历到列表最后一个元素，仍未匹配名字成功，判断包在r2列表不存在
                else:
                    if i == len(rpm_list2) - 1:
                        data['rpm_list1_only_exist'].append(r1)
            else:
                data["match"].append(r1)
                break


    for r1 in rpm_list2:
        for i,r2 in enumerate(rpm_list1):
            if os.path.dirname(r1) == os.path.dirname(r2):
                break
                # 遍历到列表最后一个元素，仍未匹配名字成功，判断包在r2列表不存在
            else:
                if i == len(rpm_list1) - 1 :
                    data['rpm_list2_only_exist'].append(r1)

    # 去重
    data["match"]=list(set(data["match"]))

    return data

def get_rpm_file_paths(file_dir):
    for root,_,files in os.walk(file_dir):
        for f in files:
            if os.path.splitext(f)[-1] == '.rpm':
                yield "{}/{}".format(root,f)


def main():
    parser = argparse.ArgumentParser(description='diff mirror')
    parser.add_argument('--rpm_list_path1', type=str,help='rpm_list_path1')
    parser.add_argument('--rpm_list_path2', type=str,help='rpm_list_path2')
    args = parser.parse_args()

    rpm_list_path1=args.rpm_list_path1
    rpm_list_path2 = args.rpm_list_path2
    rpm_list_path1_rpm=get_rpm_list(rpm_list_path1)
    rpm_list_path2_rpm =get_rpm_list(rpm_list_path2)

    d=diff_rpm_list(rpm_list_path1_rpm,rpm_list_path2_rpm)
    print(json.dumps(d,indent=4,ensure_ascii=False))

if __name__ == '__main__':
    main()

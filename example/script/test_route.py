# test_script.py 示例测试脚本

def place_cb(sp_file):
    return f"运行用户定义的 Place callback {sp_file}"


def route_cb(place_file):
    return f"运行用户定义的 Route callback {place_file}"


print("用户脚本开始执行")

open_api.set_place_call_back(place_cb)
open_api.set_route_call_back(route_cb)
open_api.run()

print("用户脚本执行完成")
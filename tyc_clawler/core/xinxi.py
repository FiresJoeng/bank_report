from pocketbase import PocketBase

# 初始化 Pocketbase 客户端
pb = PocketBase("http://localhost:8090")

# 登录管理员账户（如果需要）
pb.admins.auth_with_password("2658914209@qq.com", "qwer123456.")

# 获取数据
records = pb.collection("focus_points").get_full_list()

# 打印数据
for record in records:
    print(record)
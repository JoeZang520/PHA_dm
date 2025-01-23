def book_orange(self, equip_number):
    found_color = False
    all_equips = []  # 用于存储所有需要升级的装备信息
    coordinate = (244, 610)
    offset = 77  # 每次增加的横坐标偏移量
    for i in range(20):
        orange = (173, 87, 62)
        tolerance = 25

        result1 = self.image_tool.color(coordinate, orange, tolerance)
        if result1:
            print("找到橙色")
            found_color = True
            self.image_tool.picture("X")
            x, y = coordinate
            self.action.click(x, y)  # 固定位置的一件装备

            # 检查装备是否需要加入收藏
            self.image_tool.picture("bag", offset=(370, -140))  # 收藏快捷方式
            # 判断是否需要点击空白处或红色亮点，检查装备是否需要加入收藏
            if self.image_tool.picture("knife_without_spot", threshold=0.94):  # 未找到需要加入图鉴的装备
                time.sleep(1)
                if self.image_tool.text("攻击力"):
                    self.image_tool.picture("knife_without_spot", threshold=0.94)
                    self.image_tool.picture("knife", offset=(0, -120))  # 随便点击空白处

                    # 创建字典来存储装备信息
                    equips = {}
                    equip = self.image_tool.read_text((368, 132, 551, 157))
                    if equip is not None:
                        equip_key = f"equip{i + 1}"  # 使用动态的键名，如 equip1, equip2, ...
                        equips[equip_key] = equip
                        all_equips.append(equips)  # 将当前装备信息添加到列表中
                        # 更新横坐标
                        coordinate = (coordinate[0] + offset, coordinate[1])

        if not found_color:
            print("未找到橙色")
            break

    return all_equips  # 返回所有需要升级的装备信息
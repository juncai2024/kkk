import random

def simulate_gift_box_draws(num_draws, probabilities):
    draws = [random.choices(range(6), weights=probabilities)[0] for _ in range(num_draws)]
    return sum(draws)

def main():
    # 配置每个数量的概率
    probabilities = [0.2, 0.3, 0.25, 0.13, 0.07, 0.05]  # 概率分别对应抽取0-5个物品

    # 模拟30次抽取，并统计结果
    num_simulations = 60
    total_items = sum(simulate_gift_box_draws(30, probabilities) for _ in range(num_simulations))

    # 计算平均值
    average_items = total_items / num_simulations
    print("平均抽取到的物品数量:", average_items)

if __name__ == "__main__":
    main()

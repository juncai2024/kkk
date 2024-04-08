import random

def simulate_draws():
    numbers = [1, 2, 3, 4, 5, 6]
    probabilities = [0.4, 0.2, 0.1, 0.1, 0.05, 0.05]

    total_draws = 50
    draws_result = {num: 0 for num in numbers}

    for _ in range(total_draws):
        drawn_number = random.choices(numbers, probabilities)[0]
        draws_result[drawn_number] += 1

    return draws_result

result = simulate_draws()
print("抽取结果：", result)

# 打印键*值
for key, value in result.items():
    print(f"{key} * {value} = {key * value}")

# 计算乘积的总和
product_sum = sum(key * value for key, value in result.items())
print("键*值的总和：", product_sum)

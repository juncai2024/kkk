numbers = [0, 1, 2, 3, 4, 5, 6]
probabilities = [0.2, 0.1, 0.1, 0.3, 0.2, 0.1, 0]

# 计算加权平均值
expected_value = sum(number * probability for number, probability in zip(numbers, probabilities))

print(f"Expected value: {expected_value}")
def has_close_elements(numbers, threshold):
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j:
                distance = abs(numbers[i] - numbers[j])
                if distance < threshold:
                    return True
    return False

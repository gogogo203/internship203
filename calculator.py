def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

# Example usage
if __name__ == "__main__":
    num1 = float(input("Enter the first number: "))
    num2 = float(input("Enter the second number: "))
    
    operation = input("Enter operation (multiply/divide): ").strip().lower()
    
    if operation == "multiply":
        print(f"Result: {multiply(num1, num2)}")
    elif operation == "divide":
        try:
            print(f"Result: {divide(num1, num2)}")
        except ValueError as e:
            print(e)
    else:
        print("Invalid operation.")
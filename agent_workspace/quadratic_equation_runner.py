import math

def quadratrix_equation(a, b, c):
    try:
        if a == 0:
            raise ValueError("a cannot be zero for a valid quadratic equation.")
        
        discriminant = b**2 - 4*a*c
        
        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2 * a)
            x2 = (-b - math.sqrt(discriminant)) / (2 * a)
            return x1, x2
        elif discriminant == 0:
            x = -b / (2 * a)
            return x, x
        else:
            real_part = -b / (2 * a)
            imaginary_part = math.sqrt(-discriminant) / (2 * a)
            return real_part, imaginary_part
    except Exception as e:
        return f"Error: {e}"

# Example usage:
a = float(input("Enter the value of a: "))
b = float(input("Enter the value of b: "))
c = float(input("Enter the value of c: "))

results = quadratrix_equation(a, b, c)
print(results)
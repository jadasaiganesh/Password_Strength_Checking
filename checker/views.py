import re
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# List of common weak passwords
common_weak_passwords = {
    "123456", "password", "qwerty", "abc123", "letmein", "123123",
    "iloveyou", "admin", "welcome", "monkey", "football", "login", "passw0rd"
}

# ✅ **List of common Indian names (first names + some surnames)**
common_names = {
    "Amit", "Rahul", "Suresh", "Raj", "Anil", "Vijay", "Ravi", "Kumar", "Santosh", "Deepak", "Vikas", "Manoj",
    "Prakash", "Sanjay", "Abhishek", "Sunil", "Shyam", "Mahesh", "Ramesh", "Ajay", "Pankaj", "Arun", "Vinod",
    "Narendra", "Mohit", "Rohit", "Sachin", "Shivam", "Dinesh", "Bharat", "Gopal", "Pradeep", "Siddharth",
    "Meena", "Pooja", "Anjali", "Neha", "Priya", "Divya", "Kiran", "Suman", "Komal", "Aishwarya", "Sneha",
    "Swati", "Kavita", "Ritu", "Shreya", "Deepika", "Radhika", "Payal", "Nikita", "Varsha", "Bhavana", "Tina",
    "Sharma", "Verma", "Patel", "Gupta", "Jain", "Singh", "Yadav", "Nair", "Iyer", "Chopra"
}

# ✅ **List of all Indian states, union territories, and major cities**
indian_places = {
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Jaipur", "Lucknow",
    "Kanpur", "Nagpur", "Indore", "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad"
}

# ✅ **Function to check if a password contains personal or weak patterns**
def is_weak_password(password):
    password_lower = password.lower()

    # 1️⃣ **Common Weak Passwords**
    if password_lower in common_weak_passwords:
        return True, "Avoid using common passwords like '123456' or 'password'."

    # 2️⃣ **Common Indian Names**
    if any(name.lower() in password_lower for name in common_names):
        return True, "Avoid using personal names in passwords."

    # 3️⃣ **Indian City/State Names**
    if any(place.lower() in password_lower for place in indian_places):
        return True, "Avoid using city or state names in passwords."

    # 4️⃣ **Date of Birth Patterns (DDMMYYYY, YYYYMMDD, etc.)**
    if re.search(r"\b(?:\d{2}[/-]?\d{2}[/-]?\d{4}|\d{4}[/-]?\d{2}[/-]?\d{2})\b", password):
        return True, "Avoid using your birthdate in your password."

    # 5️⃣ **Indian Mobile Number Patterns (10-digit)**
    if re.fullmatch(r"9[0-9]{9}|8[0-9]{9}|7[0-9]{9}", password):
        return True, "Avoid using your phone number in your password."

    # 6️⃣ **Aadhaar Number (12-digit)**
    if re.fullmatch(r"[2-9]{1}[0-9]{11}", password):
        return True, "Avoid using Aadhaar numbers in your password."

    # 7️⃣ **PAN Card Format (ABCDE1234F)**
    if re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", password):
        return True, "Avoid using PAN numbers in your password."

    # 8️⃣ **Indian Vehicle Number (e.g., KA01AB1234, MH12XY5678)**
    if re.search(r"\b[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}\b", password):
        return True, "Avoid using vehicle numbers in your password."

    # 9️⃣ **Keyboard Patterns (e.g., qwerty, asdfgh)**
    keyboard_patterns = ["qwerty", "asdfgh", "zxcvbn", "123qwe", "123asd"]
    if any(pattern in password_lower for pattern in keyboard_patterns):
        return True, "Avoid using easy keyboard sequences like 'qwerty' or 'asdfgh'."

    return False, ""

# ✅ **Function to check password strength**
def check_strength(password):
    password_lower = password.lower()

    # **Check if password is weak due to personal info**
    is_weak, message = is_weak_password(password)
    if is_weak:
        return "Weak", [message, "Choose a unique password with special characters."]

    # **Check for character variety**
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

    # **Check length**
    length = len(password)

    # ✅ **Strong Password Criteria**
    if (
        length >= 12 and   # ✅ At least 12 characters
        has_upper and      # ✅ Contains uppercase letter
        has_lower and      # ✅ Contains lowercase letter
        has_digit and      # ✅ Contains a number
        has_special and    # ✅ Contains a special character
        not re.search(r"(.)\1{3,}", password) and  # ❌ Avoids repeated characters (e.g., "aaaa1234")
        not re.search(r"(123|abc|password|qwerty|asdf)", password_lower)  # ❌ Avoids common patterns
    ):
        return "Strong", []

    # ✅ **Medium Password Criteria**
    if (
        length >= 8 and
        (has_upper or has_lower) and
        (has_digit or has_special)
    ):
        return "Medium", [
            "Consider making your password longer (12+ characters).",
            "Include a mix of uppercase, numbers, and special characters."
        ]

    # ✅ **Weak Password Criteria**
    return "Weak", [
        "Use at least 12 characters.",
        "Include uppercase letters, numbers, and special characters.",
        "Avoid common words or patterns like '1234' or 'qwerty'."
    ]

@csrf_exempt
def check_password_strength(request):
    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        if not password:
            return JsonResponse({"error": "Password cannot be empty"}, status=400)

        strength, suggestions = check_strength(password)
        return JsonResponse({"strength": strength, "suggestions": suggestions})

    return JsonResponse({"error": "Invalid request method"}, status=400)

def home(request):
    return render(request, "checker/index.html")

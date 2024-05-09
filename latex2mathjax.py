def convert_latex_to_mathjax(string,count_slash=1):
    result = ''
    if count_slash == 1:
        odd_replacement = '\\('
        even_replacement = '\\)'
    else:
        odd_replacement = '\\\\('
        even_replacement = '\\\\)'
    dollar_count = 0

    if "$" not in string:
        # check if first character is backslash and second character is (
        if string[0] == '\\' and string[1] == '(' and "value" in string:
            return string
        else:
            return odd_replacement + string + even_replacement
    
    for char in string:
        if char == '$':
            dollar_count += 1
            if dollar_count % 2 == 0:
                result += even_replacement
            else:
                result += odd_replacement
        else:
            result += char
    return result



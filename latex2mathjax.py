def convert_latex_to_mathjax(string,count_slash=1):
    result = ''
    if count_slash == 1:
        odd_replacement = '\\('
        even_replacement = '\\)'
    else:
        odd_replacement = '\\\\('
        even_replacement = '\\\\)'
    dollar_count = 0

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



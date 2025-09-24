# Read file and modify content
filename = 'C:\\Users\\20245580\\LabCode\\Codes_For_Experiments\\codes\\exp_1.tsp'
with open(filename, 'r') as file:
    lines = file.readlines()

# Modify the line that contains the target text
for i, line in enumerate(lines):
    # if target_text in line:
    #     lines[i] = new_line + '\n'  # Replace the line
    #     break  # Remove this break if you want to replace all matching lines
    print(f"line number {i}, content:\n{line}")
    print(type(line))

    if i == 3:
        value = 0.1616161
        lines[i] = 'deta_t = ' + str(value) + '\n'  
        break

# Write the modified lines back to the file
with open(filename, 'w') as file:
    file.writelines(lines)

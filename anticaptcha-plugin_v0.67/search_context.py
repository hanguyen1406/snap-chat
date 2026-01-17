
import os

file_path = r"d:\Code\Python\snap chat\anticaptcha-plugin_v0.67\js\content_scripts2.js"
keywords = ["auto_submit_form", "funcaptcha", "FunCaptcha"]

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    with open(r"d:\Code\Python\snap chat\anticaptcha-plugin_v0.67\search_results.txt", 'w', encoding='utf-8') as out_f:
        for keyword in keywords:
            out_f.write(f"--- Searching for: {keyword} ---\n")
            start_index = 0
            while True:
                index = content.find(keyword, start_index)
                if index == -1:
                    break
                
                start_context = max(0, index - 500)
                end_context = min(len(content), index + 500)
                out_f.write(f"Match at index {index}:\n")
                out_f.write(content[start_context:end_context])
                out_f.write("\n" + "-" * 20 + "\n")
                
                start_index = index + 1
            
except Exception as e:
    print(f"Error: {e}")

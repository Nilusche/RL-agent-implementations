import os
from gologparser import parser, parsed_elements
from gologcompiler import create_environment_from_parsed_elements, run_procedure

def main():
    file_name = 'blocksworld.gpp'

    #print current directory
    print(os.getcwd())

    # Check if the file exists
    
    if not os.path.isfile(file_name):
        print(f"Error: {file_name} not found in the current directory.")
        return
    
    # Open and read the file
    with open(file_name, 'r') as file:
        code = file.read()
    
    # Parse the code
    parser.parse(code)
    
    # Create the environment from parsed elements
    env = create_environment_from_parsed_elements(parsed_elements)
    
    # Run the main procedure
    run_procedure(env, 'main')

if __name__ == "__main__":
    main()

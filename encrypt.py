from socketserver import ThreadingUnixDatagramServer
import sys
import numpy as np

#defining some punctuations to take out of the string
def preprocess(in_str,punc = '''!,()[]-/.?'''):
    #takes out whitespace
    out_str = in_str.replace(" ","")
    for ele in out_str:
        if ele in punc:
            out_str = out_str.replace(ele, "")
    return out_str

#takes in the key 
def substute(in_str,key):
    out_str = ""
    key_len = len(key)
    counter = 0
    #ord gets the unicode number of the char
    for entry in in_str:
        key_entry = key[counter%key_len]
        ord_input = ord(entry)
        ord_key = ord(key_entry)
        #mod by 26 to get the alphabet location
        ord_out = ((ord_input+ord_key)%26)+ord("A")
        #returns the string character of a number 
        out_entry = chr(ord_out)
        out_str+=out_entry
        counter += 1

    return out_str

#takes the substituted string and creates a 4x4 matrix
def put_string_into_matrix(str, m,n):
    
    counter  = 0
    matrices = []
    while counter<len(str):
        #creates a blank matrix filled with 'A' to make it uniform
        matrix = np.full((m,n),"A",dtype=np.dtype('U100'))
        #loops through to add in the string to the matrix
        for i in range(m):
            for j in range(n):
                if counter>=len(str):
                    break         
                matrix[i,j]=str[counter]
                counter+=1
                
            if counter>=len(str):
                    break
        matrices.append(matrix)
    return matrices

#pretty prints the matrix to match how the teachers is 
def print_matrices(matrices,out_file,add_space=False):
    for matrix in matrices:
        out_file.write("\n")
        for row in matrix:
            print_str = ""
            for entry in row:
                print_str+=entry+(" " if add_space else "")
            out_file.write(print_str+"\n")

#will shift the columns in the matrix 
def shift_matrices(matrices):
    #create empty matrix 
    modified_matricies = []
    for matrix in matrices:
        counter = 0
        #create copy to edit 
        modified_matrix = matrix.copy()
        for i in range(matrix.shape[0]):
            row = matrix[i]
            #shifts the rows to the left hence the - sign
            shifted_row = np.roll(row,-counter)
            #put the shifted row in the new matrix
            modified_matrix[i]=shifted_row
            counter+=1
        modified_matricies.append(modified_matrix)
    return modified_matricies

#convert from binary to hex 
def convert_char(char):
    #takes out the 0b infront of all binary numbers 
    binary = bin(char).replace("b","")
    if binary.count("1")%2==1:
        #if there is an odd amount of ones, change the parity bit to 1
        binary="1"+binary[1:]
    #gets the hex value of the binary number and takes out the 0x
    hex_rep = hex(int(binary,2)).replace("0x","")
    return hex_rep


#gets the parity bit
def get_parity_bit(matrices):
    modified_matricies = []
    for matrix in matrices:
        modified_matrix = matrix.copy()
        #the shape gets the row or column from matrix, 0=row, 1=column
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                char = ord(str(matrix[i,j]))
                #will get the hex values and put those values in the output matrix 
                converted_hex = convert_char(char)
                modified_matrix[i,j] = converted_hex
        modified_matricies.append(modified_matrix)
    return modified_matricies

#creates the rgf matrix
def RGF_mul(x,y):
    int_rep = int(x,16)
    bin_rep = bin(int_rep)[2:]
    while len(bin_rep)<=7:
        bin_rep="0"+bin_rep
    bin_output = ""
    mul_2_bin_output=""
    if y==1:
        return x
    
    #bin_rep_ls = bin_rep[0]+bin_rep[2:]+bin_rep[1]
    if bin_rep[0]==0:
        mul_2_bin_output = bin_rep
    else:
        bin_rep_ls = bin_rep[0]+bin_rep[2:]+bin_rep[1]
        xor_argument = "00011011"
        for i in range(len(bin_rep_ls)):
            mul_2_bin_output+=str(int(bool(int(bin_rep_ls[i],2))^bool(int(xor_argument[i],2))))
    
    if y==2:
        bin_output = mul_2_bin_output
    elif y==3:
        bin_output =""
        for i in range(len(bin_rep_ls)):
            bin_output+=str(int(bool(int(bin_rep[i],2))^bool(int(mul_2_bin_output[i],2))))
    
    hex_out = hex(int(bin_output,2))[2:]

    #convert bin_out to hex
    return hex_out


def hex_xor(x,y):

    bin_x = bin(int(x,16))[2:]
    while len(bin_x)<=7:
        bin_x="0"+bin_x

    bin_y = bin(int(y,16))[2:]
    while len(bin_y)<=7:
        bin_y="0"+bin_y
    bin_output = ""
    for i in range(len(bin_x)):
        bin_output+=str(int(bool(int(bin_x[i],2))^bool(int(bin_y[i],2))))
    hex_output = hex(int(bin_output,2))[2:]
    return hex_output


#creates the rg matrix 
def multiply_rg_field(col):
    circ_mds = np.asarray([
        [2,3,1,1],
        [1,2,3,1],
        [1,1,2,3],
        [3,1,1,2]
    ])

    output_col = col.copy()

    for i in range(circ_mds.shape[0]):
        # print("-----------------------------------")
        row = circ_mds[i]
        entry = "00000000"
        for j in range(row.shape[0]):
            hex_output = RGF_mul(col[j],circ_mds[i,j])
            entry =  hex_xor(hex_output,entry)
        output_col[i]=entry

    return output_col


def mix_columns(matrices):

    modified_matricies = []
    for matrix in matrices:
        modified_matrix = matrix.copy()
        for j in range(matrix.shape[1]):
            col = matrix[:,j]
            new_col = multiply_rg_field(col)
            modified_matrix[:,j] = new_col
        modified_matricies.append(modified_matrix)          
    return modified_matricies

#this will create an output file to print the results to
if __name__ == "__main__":
    out_file_path = "output.txt"
    out_file = open(out_file_path,"a")

    #takes in two input files, the input and key txt so it can run the program
    input_file = sys.argv[1]
    key_file = sys.argv[2]
    with open(input_file) as f:
        input_text = f.read()
    with open(key_file) as f:
        key_text = f.read()

    # printing original string
    #out_file.write("Original: ".ljust(16," ") + input_text+"\n")

    
    # printing result
    preprocesed_string = preprocess(input_text)
    out_file.write("Preprocessing: ".ljust(16," ") + preprocesed_string+"\n")


    # substitute
    substituted_string = substute(preprocesed_string,key_text)
    out_file.write("Substitution: "+ substituted_string+"\n")

    #pad 
    padded_result = put_string_into_matrix(substituted_string,4,4)
    out_file.write("\nPadding : \n" )
    print_matrices(padded_result,out_file)

    #shift 
    shifted_result = shift_matrices(padded_result)
    out_file.write("\nShiftRows : \n" )
    print_matrices(shifted_result,out_file)

    #parity bit
    parity_bit = get_parity_bit(shifted_result)
    out_file.write("\nParity : \n" )
    print_matrices(parity_bit,out_file,True)

    #mix
    mixed_columns = mix_columns(parity_bit)
    out_file.write("\nmixColumns : \n" )
    print_matrices(mixed_columns,out_file,True)


    out_file.close()
	

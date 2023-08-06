# Copyright(c) gert.cuykens@gmail.com
# source: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/426069/index_txt

import Image, ImageFont, ImageDraw

def makeCode(e):
    
    A = {0 : "0001101", 1 : "0011001", 2 : "0010011", 3 : "0111101", 4 : "0100011", 
         5 : "0110001", 6 : "0101111", 7 : "0111011", 8 : "0110111", 9 : "0001011"}
    
    B = {0 : "0100111", 1 : "0110011", 2 : "0011011", 3 : "0100001", 4 : "0011101",
         5 : "0111001", 6 : "0000101", 7 : "0010001", 8 : "0001001", 9 : "0010111"}

    c = {0 : "1110010", 1 : "1100110", 2 : "1101100", 3 : "1000010", 4 : "1011100",
         5 : "1001110", 6 : "1010000", 7 : "1000100", 8 : "1001000", 9 : "1110100"}

    f = {0 : (A,A,A,A,A,A), 1 : (A,A,B,A,B,B), 2 : (A,A,B,B,A,B), 3 : (A,A,B,B,B,A), 4 : (A,B,A,A,B,B),
         5 : (A,B,B,A,A,B), 6 : (A,B,B,B,A,A), 7 : (A,B,A,B,A,B), 8 : (A,B,A,B,B,A), 9 : (A,B,B,A,B,A)}

    f = f[e[0]]

    strCode = 'L0L'
    for i in range(0,6):
        strCode += f[i][e[i+1]]
        
    strCode += '0L0L0'
    for i in range (7,13):
        strCode += c[e[i]]

    strCode += 'L0L'
    return (strCode)

def computeChecksum(v):
    weight=[1,3]*6
    magic=10
    sum = 0
    for i in range(12): 
        sum = sum + int(v[i]) * weight[i]
    z = ( magic - (sum % magic) ) % magic
    return z

def ean13(v):

    t=''
    if  len(v)<12:
        for i in xrange(0,12-len(v)): t=t+'0'
        v=t+v
    else: v=v[0:12]

    e=[]
    for digit in v: e.append(int(digit))
    e.append(computeChecksum(e))
    
    c=''
    for digit in e: c+="%d"%digit
    
    bits = makeCode(e)
        
    height = 50
    position = 8

    import os
    font = ImageFont.load(os.path.join(os.path.dirname(__file__),"courB08.pil"))
    
    im   = Image.new("1",(len(bits)+position,height))
    draw = ImageDraw.Draw(im)
    draw.rectangle(((0,0),(im.size[0],im.size[1])),fill=256)

    draw.text((0, height-9), c[0], font=font, fill=0)
    draw.text((position+7, height-9), c[1:7], font=font, fill=0)
    draw.text((len(bits)/2+6+position, height-9), c[7:], font=font, fill=0)
    
    for bit in range(len(bits)):
        if  bits[bit] == '1': draw.rectangle(((bit+position,0),(bit+position,height-10)),fill=0)
        elif bits[bit] == 'L': draw.rectangle(((bit+position,0),(bit+position,height-3)),fill=0)
    
    from StringIO import StringIO
    f=StringIO()
    im.save(f,'png')
    data = f.getvalue()

    return data

def test():
    assert(makeCode([0,0,0,0,0,0,0,0,0,0,0,0,0]) == 'L0L0001101000110100011010001101000110100011010L0L0111001011100101110010111001011100101110010L0L')
    assert(makeCode([1,1,1,1,1,1,1,1,1,1,1,1,6]) == 'L0L0011001001100101100110011001011001101100110L0L0110011011001101100110110011011001101010000L0L')
    assert(makeCode([2,2,2,2,2,2,2,2,2,2,2,2,2]) == 'L0L0010011001001100110110011011001001100110110L0L0110110011011001101100110110011011001101100L0L')
    assert(makeCode([3,3,3,3,3,3,3,3,3,3,3,3,8]) == 'L0L0111101011110101000010100001010000101111010L0L0100001010000101000010100001010000101001000L0L')
    assert(makeCode([4,4,4,4,4,4,4,4,4,4,4,4,4]) == 'L0L0100011001110101000110100011001110100111010L0L0101110010111001011100101110010111001011100L0L')
    assert(makeCode([5,5,5,5,5,5,5,5,5,5,5,5,0]) == 'L0L0110001011100101110010110001011000101110010L0L0100111010011101001110100111010011101110010L0L')
    assert(makeCode([6,6,6,6,6,6,6,6,6,6,6,6,6]) == 'L0L0101111000010100001010000101010111101011110L0L0101000010100001010000101000010100001010000L0L')
    assert(makeCode([7,7,7,7,7,7,7,7,7,7,7,7,2]) == 'L0L0111011001000101110110010001011101100100010L0L0100010010001001000100100010010001001101100L0L')
    assert(makeCode([8,8,8,8,8,8,8,8,8,8,8,8,8]) == 'L0L0110111000100101101110001001000100101101110L0L0100100010010001001000100100010010001001000L0L')
    assert(makeCode([9,9,9,9,9,9,9,9,9,9,9,9,4]) == 'L0L0001011001011100101110001011001011100010110L0L0111010011101001110100111010011101001011100L0L')   

if  __name__ == "__main__":
    test()
    print ean13("")
    print ean13("9782212110708")
    print ean13("978221211070")
    print ean13("00001")
    print ean13("12345678901234")


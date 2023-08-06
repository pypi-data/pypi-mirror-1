from Ft.Xml import MarkupWriter
from Ft.Xml import Domlette

SVG_NAMESPACE=u"http://www.w3.org/2000/svg"

#Scalable proportions for Trigrams,Gua, and Yao
TRIGRAM_SCALE = 5
TRIGRAM_HEIGHT=3*TRIGRAM_SCALE
TRIGRAM_WIDTH=6*TRIGRAM_SCALE
YIN_WIDTH=(2.0/5) * TRIGRAM_WIDTH
YIN_SPACING = (1.0/5) * TRIGRAM_WIDTH
YAO_SPACING = float(TRIGRAM_HEIGHT) / 3


#Mapping from binary value to the name of the corresponding Trigram (used for labeling)
trigram_metadata={
    7:u'Heaven',
    0:u'Earth',
    6:u'Lake',
    2:u'Water',
    5:u'Fire',
    4:u'Thunder',
    3:u'Wind',
    1:u'Mountain'
}

#Trigram values of FuXi's arrangement in clockwise order (starting from the top)
FUXI_CIRCULAR_ARRANGEMENT=[7,3,2,1,0,4,5,6]

#Burrowed from http://www.daniweb.com/code/snippet285.html
def Denary2Binary(n):
    '''convert denary integer n to binary string bStr'''
    bStr = ''
    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr    

#Draws a Yao line, depending on if it's a ying or yang
def drawYao(writer,yang=True):
    yaoStyle=u'stroke: black;color: black'
    if yang:
        rect_attributes={u'x':u'0',
                         u'y':u'0',
                         u'height':unicode(TRIGRAM_HEIGHT/6),
                         u'width':unicode(TRIGRAM_WIDTH),
                         u'style':yaoStyle
        }
        writer.startElement(u"rect",namespace=SVG_NAMESPACE,attributes=rect_attributes)
        writer.endElement(u"rect")
    else:
        rect_attributes={u'y':u'0',
                         u'height':unicode(TRIGRAM_HEIGHT/6),
                         u'width':unicode(YIN_WIDTH),
                         u'style':yaoStyle
        }
        rect_attributes[u'x'] = u'0'
        writer.startElement(u"rect",namespace=SVG_NAMESPACE,attributes=rect_attributes)
        writer.endElement(u"rect")
        rect_attributes[u'x'] = unicode(YIN_SPACING + YIN_WIDTH)
        writer.startElement(u"rect",namespace=SVG_NAMESPACE,attributes=rect_attributes)
        writer.endElement(u"rect")            

#Takes a binary value and an instance of a MarkupWriter and draws the corresponding Trigram
def drawTrigram(writer,value):    
    #Binary values are left-padded so there are always 3 digits (1 per yao line - yin or yang)
    #1 - Yang (straight line)
    #0 - Yin (dashed line - 2 segments)
    trigramValue='0'*(3-len(value))+value    
    
    #Index of the yao are essentially the relative Y SVG coordinates (which differ from cartesian coordinates)
    #This function starts from the bottom of the Trigram (the leftmost binary digit) and progresses *up*
    #to the top (the rightmost digit)
    #This is how the Trigrams / Gua are traditionally read (bottom up)
    idx=2        
    for yao in trigramValue:
        groupAttributes={}        
        groupAttributes[u'transform']=u'translate(0,%s)'%(idx*YAO_SPACING)
        writer.startElement(u"g",
                            namespace=SVG_NAMESPACE,
                            attributes=groupAttributes)     
        drawYao(writer,yao == '1')        
        writer.endElement(u"g")
        idx -= 1    

#Takes  a writer instance and decimal value and draws the corresponding fully developed Gua (Hexagram) 
def drawGua(writer,value):
    #Convert the decimal value to it's binary equivalent (note the resulting binary value is not leftmost padded)
    binaryValue = Denary2Binary(value)        
    
    #If the value is less than 7 then the lower trigram (the leftmost 3 digits of the binary value) are all 0's
    #Note: although the trigrams individually draw from bottom up, the Gua is drawn top down (upper trigram then lower trigram)
    #This is against the convention of how the Gua are traditionally read (lower trigram first - the inner, subjective motivation for change then
    #upper gua afterwards - the outter, objective situation through which change occurs)
    if value <= 7:
        drawTrigram(writer,binaryValue)
        writer.startElement(u"g",
                        namespace=SVG_NAMESPACE,
                        attributes={u'transform':u'translate(0,%s)'%(YAO_SPACING*3)})   
        drawTrigram(writer,'000')
        writer.endElement(u"g")
    
    #If the value is > 7 then the lower trigram (leftmost 3 digits) can be determined by first padding the binary value 
    #with 6 - N 0's (where N is the length of the concise binary representation of the given decimal value) and then
    #taking the leftmost 3 digits of the result
    elif value > 7:
        binaryValue = '0'*(6-len(binaryValue))+binaryValue
        drawTrigram(writer,binaryValue[3:])
        writer.startElement(u"g",
                        namespace=SVG_NAMESPACE,
                        attributes={u'transform':u'translate(0,%s)'%(YAO_SPACING*3)})   
        drawTrigram(writer,binaryValue[:3])
        writer.endElement(u"g")
        
#This is an example of how the Gua/Trigram drawing functions can be used to draw the common
#Visual arrangements of the Trigrams/Gua.  This is probably the most fundamental of such arrangements:
#FuXi's early heaven arrangement. 
def drawFuXiCircles(radius=TRIGRAM_HEIGHT*5):
    writer = MarkupWriter(open('FuXi.svg','w'), indent=u"yes")
    writer.startDocument()        
    writer.startElement(u'svg',
                        namespace=SVG_NAMESPACE)
                        
    writer.startElement(u"g",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'translate(250,250)'})   
                            
    #Here is where the power lies!  Incrementing through the order of 8 trigrams, rotating 45 degrees per item (360 / 8 = 45).  
    #Draw the Trigram with the english translation of it's symbol above it (also rotated)
    for trigram in FUXI_CIRCULAR_ARRANGEMENT:
        angle=FUXI_CIRCULAR_ARRANGEMENT.index(trigram)*45
        
        writer.startElement(u"g",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'rotate(%s) translate(0,-%s)'%(angle,radius)})   
        writer.startElement(u"g",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'translate(-%s,-%s)'%(float(TRIGRAM_WIDTH) / 2,float(TRIGRAM_HEIGHT) / 2)})   
        drawTrigram(writer,Denary2Binary(trigram))
        writer.startElement(u"text",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'translate(-%s,0)'%(float(TRIGRAM_WIDTH) / 3),
                                         u'x':u'0',
                                         u'y':u'-10',
                                         u'style':u'font-size: 14;color: black'})   
        writer.text(trigram_metadata[trigram])
        writer.endElement(u'text')
        writer.endElement(u"g")
        writer.endElement(u"g")    
    
    writer.endElement(u"g")
    writer.endElement(u'svg')
    writer.endDocument()

#Another demonstration of a classic arrangement drawn using the gua/trigram plotting functions
#This is ShaoYong's Square.  Probably the most useful (in my opinion) arrangement for 
#observing the relationships between the fully developed 64 gua.  Within each row, the lower trigrams 
#are all of the same kind (he refered to them as the 'palace' of earth, mountain, etc..) and within each column
#the upper trigrams are also of the same kind.  So, essentially it is a 2 dimensional plot of the 64 gua where
#the X coordinate is the upper gua and the Y coordinate is the lower gua.  This incredibly numeric symmetry comes
#from simply drawing the gua in acending binary order from 0 - 63, 8 per line!  I've added the english names
#of the corresponding coordinates so a student can match up the lower/upper gua (by name) to find
#the gua formed.  
def drawShaoYongSquare(GuaSpacing=float(TRIGRAM_WIDTH) / 2):
    writer = MarkupWriter(open('ShaoYong.svg','w'), indent=u"yes")
    writer.startDocument()        
    writer.startElement(u'svg',
                        namespace=SVG_NAMESPACE)
                        
    writer.startElement(u"g",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'translate(250,100)'})   
    
    for xIndex in range(8):
        writer.startElement(u"text",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'translate(%s,-%s) rotate(-90)'%(
                                (TRIGRAM_WIDTH + GuaSpacing) * xIndex + float(TRIGRAM_WIDTH) / 1.5,
                                float(TRIGRAM_HEIGHT) / 2
                                )})
        writer.text(trigram_metadata[xIndex])
        writer.endElement(u"text")        

    palaceLeftPadding = (TRIGRAM_WIDTH + GuaSpacing) * 8
    for yIndex in range(8):
        writer.startElement(u"text",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'translate(%s,%s)'%(
                                palaceLeftPadding,
                                (TRIGRAM_HEIGHT * 2 + GuaSpacing) * yIndex + TRIGRAM_HEIGHT
                                )})
        writer.text(trigram_metadata[yIndex])
        writer.endElement(u"text")        
    

    
    for yIndex in range(8):
        for xIndex in range(8):
            binaryValue = yIndex*8 + xIndex
            writer.startElement(u"g",
                            namespace=SVG_NAMESPACE,
                            attributes={u'transform':u'translate(%s,%s)'%(
                                            (TRIGRAM_WIDTH + GuaSpacing) * xIndex,
                                            (TRIGRAM_HEIGHT * 2 + GuaSpacing) * yIndex)
                                        })   
            drawGua(writer,binaryValue)
            writer.endElement(u'g')
    

    writer.endElement(u'g')
    writer.endElement(u'svg')
    writer.endDocument()
    
if __name__ == '__main__':    
    drawFuXiCircles()
    drawShaoYongSquare()

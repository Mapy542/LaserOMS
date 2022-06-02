

def LoadPricingStyles():
    try:
        with open('./Pricing_Styles.txt', 'r') as f:
            PricingStyles = f.read().split("\n")
            f.close()
            stylenames = []
            stylemultiplyers = []
            styleincreases = []
            for i in range(len(PricingStyles)):
                style = PricingStyles[i].split(",")
                stylenames.append(style[0])
                stylemultiplyers.append(float(style[1]))
                styleincreases.append(int(style[2])*100)
        return stylenames, stylemultiplyers, styleincreases
    except:
        print("Error loading Pricing Styles")
        return None

def Recalculate(base_price):
    stylenames, stylemultiplyers, styleincreases = LoadPricingStyles()
    otherpricestyles = []
    for i in range(len(stylenames)):
        otherpricestyles.append(stylenames[i], base_price * stylemultiplyers[i] + styleincreases[i])
    return otherpricestyles
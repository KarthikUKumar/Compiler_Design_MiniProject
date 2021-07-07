file=open('sample.txt','r')
operators=[]
keyw=[]
ide=[]
num=[]
k=["int","main","for","if","end","begin"]
op=["<",">","=","!"]
for line in file:
	for word in line.split():
		if word in ["=",">","<"]:
			operators.append(word)
		elif word.isalnum():
			if word in k:
				keyw.append(word)
			else:
				if word.isdigit():
					num.append(word)
				else:
					ide.append(word)
		else:
			flag=0
			j=0
			for x in list(word):
				if x in op and flag==0:
					flag=1
					l=x
					continue
				if x in ["=","-","+","%","/","*"] and flag==0:
					operators.append(x)
					continue
				if(x in ["="] and flag==1):
					flag=0
					operators.append(l+x)
				if(x.isalnum() and j==0):
					str=""
					j=1
					str+=x
					continue
				if(x.isalnum() and j==1):
					str+=x
					continue;
				if(x.isalnum()!="True" and j==1):
					if str in k:
						keyw.append(str)
					else:
						if str.isdigit():
							num.append(str)
						else:
							ide.append(str)
					j=0
print "There are total of",len(operators),"Operators. They are:"
for w in operators:
	print(w)
print "There are total of",len(keyw),"Keywords. They are:"
for w in keyw:
	print(w)
print "There are total of",len(ide),"Identifiers. They are:"
for w in ide:
	print(w)
print "There are total of",len(num),"Numbers. They are:"
for w in num:
	print(w)
file.close()

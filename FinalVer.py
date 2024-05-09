# %%
import re

class RppParser:
    def __init__(self, code):
        self.code = code
        self.outputs = {}
        self.variables = []
        self.operators = ["+", "-", "*", "/"]

    def parse(self):
        # حذف کامنت ها
        self.code = re.sub(r"//.*?\n", "", self.code)
        
        # حذف فضای خالی اضافی
        self.code = re.sub(r"\n(?:\s*\n)*", "", self.code)
        self.code = re.sub(r"\s+", " ", self.code)
        
        # تقسیم کد به دستورات
        self.statements = self.code.split(";")
        
        # پردازش هر دستور
        for statement in self.statements:  
           # print('statement:',statement)
            self.process_statement(statement)
        
    def double_operators(self,match):
            preCharacter = 0
            for character in match[1]:
                if character in self.operators and preCharacter in self.operators:
                        raise ValueError("Grammar error: Two operators in a row in the phrase '%s'" % (match[1]))
                
                preCharacter = character

    def undefined_variables(self,match):
                for character in match[1]:
                  if  character not in self.variables  and character.isalpha():
                    raise ValueError("Grammar error: Variable '%s' is undefined in the expression '%s'"  % (character, match[1]))
    
    def unbalanced_parentheses(self,match):
        opening_parentheses = 0
        for character in match[1]:
              if character == "(":
                  opening_parentheses += 1
              elif character == ")":
                 opening_parentheses -= 1
        if opening_parentheses != 0:
            raise ValueError("Grammar error: Unbalanced parentheses in the phrase '%s'"  % (match[1]))
        
    def double_assignment_operator(self,match):
          if match[0].count("=") > 1:
                raise ValueError("Grammar error: Two assignment operators in a row in the expression '%s'"  % (match[0]))
          
    def check_grammar(self, statement):
             # دستور تخیصیص باشد
             if not(re.match(r"(.+)=(.+)", statement)):
                 # ارور گرامری
                raise ValueError("Invalid R++ grammar at %s", statement)
            
    def check_grammar_secondP(self, matches):
            # سمت دوم با عملگر شروع نشود 
            if matches[0] in self.operators:
                # ارور گرامری
                raise ValueError("Grammar error in the expression '%s': \nOperations must not start with an operator" % (matches))
            # دو طرف تساوی فاصله وجود داشته باشد
            if matches.count('=')!= 0 :
                  # ارور گرامری
                raise ValueError("Grammar error in the expression '%s': \nThere should be a space on both sides of the assignment operator" % matches)
            # دو طرف عملگر پر باشد
            if matches[-1] in self.operators :
                  # ارور گرامری
                raise ValueError("Grammar error in the expression '%s': \nThe operator must have spaces on both sides" % matches)
            # بین ; و عبارت فاصله وجود نداشته باشد
            if matches[-1] == ' ' :
                  # ارور گرامری
                raise ValueError("Grammar error in the expression '%s':\n There should be no space between ; and the expression" % matches)
            preCharacter = '-'
            for character in matches:
                #handling 2+3x
                #and 2+x3
                #and (2*4)x
                #and x(2*4)
                #and (2*4)2
                #and 2(2*4)
                #and (2*)
                if (character.isalpha() and preCharacter.isnumeric()) or (character.isnumeric() and preCharacter.isalpha()) or (character.isalpha() and preCharacter==')') or (character=='(' and preCharacter.isalpha()) or (character.isnumeric() and preCharacter==')') or (character=='(' and preCharacter.isnumeric()) or (character==')' and preCharacter in self.operators):
                       # ارور گرامری
                        raise ValueError("Grammar error in the expression '%s': Operator missing" % matches) 
                preCharacter = character
                #بین عملگرو عدد یا متغیر فاصله نباشد
            if matches.count(' ') != 0:
                       # ارور گرامری
                        raise ValueError("Grammar error in the expression '%s': \n There should be no space between the operator and the number or variable" % matches)

    def check_grammar_firstP(self, match):
            # سمت راست تساوی فقط متغیر باشد 
            if any(char.isdigit() for char in match):
                       # ارور گرامری
                        raise ValueError("Grammar error in the expression '%s':\n The right side of the equal sign must be a variable only" % match)
            # سمت راست تساوی فقط متغیر باشد 
            if(any(operator in match for operator in self.operators)):
                       # ارور گرامری
                        raise ValueError("Grammar error in the expression '%s':\n The right side of the equal sign must be a variable only" % match)
            if match == ' ':
                       # ارور گرامری
                        raise ValueError("Grammar error in the expression '%s'" % match)
            
                 
    def process_statement(self, statement):
            # بررسی گرامر 
            self.check_grammar(statement)
            #جدا کردن دو بخش عملیات 
            matches = re.findall(r"(.+)\s+(.+)", statement)
            #بررسی ارور های ممکن
            #بررسی گرامر بخش دوم
            self.check_grammar_secondP(matches[0][1])
            #بخش اول حاوی عدد نباشد
            self.check_grammar_firstP(matches[0][0])
            #ارور عملگر های پشت سر هم
            self.double_operators(matches[0])
            #ارور عملگر های تخصیص پشت سر هم
            self.double_assignment_operator(matches[0])
            #ارور پرانتز های نامتوازن
            self.unbalanced_parentheses(matches[0])
            #ارور متغیر تعریف نشده
            self.undefined_variables(matches[0]) 
            #حل عملیات در صورت نبود خطا
            self.assign(matches[0][0][0],matches[0][1])

    def assign(self, variable, expression): 
        # حل عملیات 
        value = self.evaluate(expression)
      
        # ذخیره مقدار در متغیر
        self.outputs[variable] = value

        # ذخیره متغیر
        self.variables.append(variable)
    
    def cal(self,a,op,b):
          a = float(a)
          b = float(b)
          if op == "+":
            return(a + b)
          elif op == "-":
            return(a - b)
          elif op == "*":
            return(a * b)
          elif op == "/":
            return(a / b)
            
    def eval(self, expression):
     a = ''
     b = ''
     hasOperation = False
     for i, token in enumerate(expression):
      if token.isdigit():
        if i != 0 and expression[i - 1] in ["+", "-", "*", "/"]:
          # if its the first operation
          if b == '':
            op = tempOp
            b = b + token
          else:
            #int(a),str(op),int(b)
            a = self.cal(a,op,b)
            op = tempOp
            b = ''
            b = b + token
        else:
          #if a is done
          if b != '':
            b = b + token
          #if its the first number
          else:
            a = a + token 
      elif token in ["+", "-", "*", "/"]:
        if i != 0 and expression[i - 1] not in ["+", "-", "*", "/"]:
          tempOp = token
          hasOperation = True
     if  hasOperation:
            return self.cal(a,op,b)
     return a
    


    def evaluate(self, expression):
        # تبدیل عملگرهای R++ به عملگرهای استاندارد
        expression = re.sub(r"\/|\*", lambda m: {"/": "*", "*": "/"}[m.group(0)], expression)

        expression = re.sub(r"\-|\+", lambda m: {"-": "+", "+": "-"}[m.group(0)], expression)
        # جایگذاری مقدار های مجهول در عملیات با مقادیر انها
        for variable, value in self.outputs.items():
          if variable in self.outputs:
             expression = expression.replace(variable, str(value))
        # حل عملیات داده شده
        if expression.count('(') >=1:
            return eval(expression)
        else:
            return self.eval(expression) 



# %%
def main():
    # Reading the input code from the file
    with open("input.txt", "r") as f:
        code = f.read()

    # Checking the input lines count
    line_count = len(code.split("\n"))
    if line_count < 4 or line_count > 10:
        print("The input lines count should be between 4 and 10.")
        return

    # Building the compiler
    parser = RppParser(code)

    # Processing the code
    parser.parse()

    # Printing the values of the variables
    for variable, value in parser.outputs.items():
        print(f"{variable} = {value}")

if __name__ == "__main__":
    main()





from flask import Flask, render_template, request, jsonify
import operator

app = Flask(__name__)

# Define operator functions
ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

# Define precedence and associativity
precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
associativity = {'+': 0, '-': 0, '*': 0, '/': 0}

# Tokenizer function
def tokenize(expression):
    tokens = []
    num = ''
    for char in expression:
        if char.isdigit() or char == '.':
            num += char
        else:
            if num:
                tokens.append(num)
                num = ''
            if char in ops or char in '()':
                tokens.append(char)
    if num:
        tokens.append(num)
    return tokens

# Shunting yard algorithm to convert infix to postfix
def infix_to_postfix(expression):
    output = []
    stack = []
    tokens = tokenize(expression)
    
    for token in tokens:
        if token.isdigit() or '.' in token:  # To handle decimals
            output.append(token)
        elif token in ops:
            while (stack and stack[-1] in ops and 
                   ((associativity[token] == 0 and precedence[token] <= precedence[stack[-1]]) or
                    (associativity[token] == 1 and precedence[token] < precedence[stack[-1]]))):
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Remove '('
    
    while stack:
        output.append(stack.pop())
    
    return output

# Evaluate postfix expression
def evaluate_postfix(postfix_expr):
    stack = []
    
    for token in postfix_expr:
        if token.isdigit() or '.' in token:  # To handle decimals
            stack.append(float(token))
        elif token in ops:
            b = stack.pop()
            a = stack.pop()
            result = ops[token](a, b)
            stack.append(result)
    
    return round(stack.pop(), 2)  # Round result to 2 decimal points

# Evaluate prefix expression
def evaluate_prefix(prefix_expr):
    stack = []
    
    for token in reversed(prefix_expr):
        if token.isdigit() or '.' in token:  # To handle decimals
            stack.append(float(token))
        elif token in ops:
            a = stack.pop()
            b = stack.pop()
            result = ops[token](a, b)
            stack.append(result)
    
    return round(stack.pop(), 2)  # Round result to 2 decimal points

# Calculator endpoint to evaluate expressions
@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    expression = data['expression']
    notation = data['notation']
    
    try:
        if notation == 'infix':
            postfix_expr = infix_to_postfix(expression)
            result = evaluate_postfix(postfix_expr)
        elif notation == 'postfix':
            postfix_expr = tokenize(expression)
            result = evaluate_postfix(postfix_expr)
        elif notation == 'prefix':
            prefix_expr = tokenize(expression)
            result = evaluate_prefix(prefix_expr)
        else:
            return jsonify({"error": "Invalid notation type!"})
        return jsonify({"result": result})
    except ZeroDivisionError:
        return jsonify({"error": "Division by zero!"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Render homepage
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

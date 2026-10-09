# SymPy 速查手册

> 本文档覆盖 Starter Kit 中用到的 SymPy 函数，帮你快速上手和扩展。

## 基础设置

```python
from sympy import *

# 定义符号变量
x, y, z, t = symbols('x y z t')
n, k = symbols('n k', integer=True)
a, b, c = symbols('a b c', positive=True)

# 定义函数
f = Function('f')
```

## 微积分

### 求导

```python
diff(x**3 + 2*x, x)                  # → 3*x**2 + 2
diff(sin(x)*cos(x), x)               # → -sin(x)**2 + cos(x)**2
diff(x**3, x, 2)                     # 二阶导数 → 6*x
diff(exp(x*y), x, y)                 # 混合偏导
```

### 积分

```python
integrate(x**2, x)                    # 不定积分 → x**3/3
integrate(x**2, (x, 0, 1))           # 定积分 → 1/3
integrate(exp(-x**2), (x, -oo, oo))  # → sqrt(pi)

# 多重积分
integrate(x*y, (x, 0, 1), (y, 0, 1))
```

### 极限

```python
limit(sin(x)/x, x, 0)                # → 1
limit((1 + 1/n)**n, n, oo)           # → E
limit(1/x, x, 0, '+')               # 右极限 → oo
limit(1/x, x, 0, '-')               # 左极限 → -oo
```

### 级数

```python
series(exp(x), x, 0, 5)              # Taylor 展开 → 1 + x + x²/2 + ...
summation(1/k**2, (k, 1, oo))        # → pi**2/6
```

## 方程求解

### 代数方程

```python
solve(x**2 - 5*x + 6, x)             # → [2, 3]
solve(x**3 - 1, x)                   # → [1, -1/2 - sqrt(3)*I/2, ...]
solve([x + y - 3, x - y - 1], [x, y])  # 方程组 → {x: 2, y: 1}

# 或用 linsolve
linsolve([x + y - 3, x - y - 1], [x, y])
```

### 不等式

```python
from sympy import solve_univariate_inequality, S
solve_univariate_inequality(x**2 - 4 < 0, x)   # → (-2, 2)
```

## 线性代数

### 矩阵构建

```python
A = Matrix([[1, 2], [3, 4]])
I = eye(3)                            # 单位矩阵
Z = zeros(2, 3)                       # 零矩阵
```

### 基本运算

```python
A.det()                               # 行列式
A.inv()                               # 逆矩阵
A.T                                   # 转置
A.rref()                              # 行最简形
A.rank()                              # 秩
A.nullspace()                         # 零空间
```

### 特征值与特征向量

```python
A.eigenvals()                         # {特征值: 重数}
A.eigenvects()                        # [(特征值, 重数, [特征向量])]
A.diagonalize()                       # (P, D) 使得 A = P*D*P^-1
```

### 分解

```python
A.cholesky()                          # Cholesky 分解
A.LUdecomposition()                   # LU 分解
A.QRdecomposition()                   # QR 分解
A.singular_value_decomposition()      # SVD
```

## 微分方程

### 常微分方程 (ODE)

```python
f = Function('f')
x = Symbol('x')

# y' + y = 0
ode = Eq(f(x).diff(x) + f(x), 0)
dsolve(ode, f(x))                     # → f(x) = C1*exp(-x)

# y'' + y = 0
ode2 = Eq(f(x).diff(x, 2) + f(x), 0)
dsolve(ode2, f(x))                    # → f(x) = C1*sin(x) + C2*cos(x)

# 带初始条件
dsolve(ode, f(x), ics={f(0): 1})
```

## 表达式操作

```python
simplify(expr)                         # 通用化简
expand(expr)                           # 展开
factor(expr)                           # 因式分解
cancel(expr)                           # 约分
apart(expr)                            # 部分分式分解
together(expr)                         # 合并分式
trigsimp(expr)                         # 三角函数化简
```

## LaTeX 输出

```python
from sympy import latex

expr = Integral(x**2, x)
print(latex(expr))                     # → \int x^{2}\, dx

# 带样式
latex(expr, mode='equation')           # 包裹在 equation 环境中
```

## 表达式解析

```python
from sympy.parsing.sympy_parser import parse_expr

expr = parse_expr("x**2 + 2*x + 1")   # 字符串 → SymPy 表达式
```

## 常用常量

```python
pi          # π = 3.14159...
E           # e = 2.71828...
I           # 虚数单位 i
oo          # 无穷大 ∞
S.Half      # 精确分数 1/2
Rational(1, 3)  # 精确分数 1/3
```

## 数值计算

```python
expr = sqrt(2)
float(expr)                            # → 1.4142135...
expr.evalf(50)                         # 50 位精度
N(pi, 100)                            # 100 位 π
```

## 扩展提示

### 添加新的求解类型

```python
# 在 solve.py 中添加
def solve_laplace_transform(problem):
    from sympy import laplace_transform, inverse_laplace_transform
    s = Symbol('s')
    F = laplace_transform(f_expr, t, s)
    return F

# 注册
SOLVERS["laplace"] = solve_laplace_transform
```

### 接入 LLM 求解器

```python
# 伪代码
def solve_with_llm(problem):
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": f"请详细解答以下数学题，给出步骤和最终答案：\n{problem['text']}"
        }]
    )
    # 解析 LLM 回复，提取步骤和答案
    return parse_llm_solution(response.content[0].text)
```

## 参考链接

- [SymPy 官方文档](https://docs.sympy.org/latest/)
- [SymPy Tutorial](https://docs.sympy.org/latest/tutorials/intro-tutorial/index.html)
- [SymPy Cheat Sheet (PDF)](https://github.com/sympy/sympy/wiki)

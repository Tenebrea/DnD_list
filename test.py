import re
from random import *

roll = "1d6+3"
result = 0
start = 0
end = 1
roll = roll.replace(" ", "")
a1 = re.split(r"[+-/*]", roll)
a2 = re.findall(r"[+-*/]", roll)


if re.match(r"[0-9]*?d[0-9]*?", a1[0]):
  for i in range(int(a1[0].split("d")[0])):
    result+=randint(1, int(a1[0].split("d")[1]))
elif re.match(r"[0-9]*?", a1[0]):
  result+=int(a1[0])
else:
  result = "error"

for i in a2:
  match i:
    case "+":
      if re.match(r"[0-9]*?d[0-9]*?", i):
        for j in range(int(a1[0].split("d")[0])):
          result+=randint(1, int(a1[0].split("d")[1]))
      elif re.match(r"[0-9]*?", a1[0]):
        result+=int(a1[0])
      else:
        result = "error"

    case "-":
      if re.match(r"[0-9]*?d[0-9]*?", i):
        for j in range(int(a1[0].split("d")[0])):
          result-=randint(1, int(a1[0].split("d")[1]))
      elif re.match(r"[0-9]*?", a1[0]):
        result-=int(a1[0])
      else:
        result = "error"

    case "/":
      if re.match(r"[0-9]*?d[0-9]*?", i):
        for j in range(int(a1[0].split("d")[0])):
          result//=randint(1, int(a1[0].split("d")[1]))
      elif re.match(r"[0-9]*?", a1[0]):
        result//=int(a1[0])
      else:
        result = "error"

    case "*":
      if re.match(r"[0-9]*?d[0-9]*?", i):
        for j in range(int(a1[0].split("d")[0])):
          result*=randint(1, int(a1[0].split("d")[1]))
      elif re.match(r"[0-9]*?", a1[0]):
        result*=int(a1[0])
      else:
        result = "error"
print(result)
import pandas as pd
import numpy as np
from ortools.linear_solver import pywraplp

table = pd.read_csv('form_answers.csv')

table.drop('Carimbo de data/hora', inplace=True, axis=1)

tutores = table[table['Você é:'] == 'Tutor']
bichos = table[table['Você é:'] == 'Bicho']

tutores.reset_index(inplace=True, drop=True)
bichos.reset_index(inplace=True, drop=True)

tutores = tutores.sample(frac=1)

num_tutores = len(tutores)
num_bichos = len(bichos)

assert (tutores.columns == bichos.columns).all()
ncols = len(tutores.columns)

def give_score(row0,row1):
  score = 0

  for k in range(2,ncols):
    diff = abs(row0[k]-row1[k])
    if diff == 0:
      score += 10
    elif diff == 1:
      score += 8
    elif diff == 2:
      score += 4
    elif diff == 3:
      score += 1
  
  return score

profit = []
for i in range(num_tutores):
  profit_temp = []
  for j in range(num_bichos):
    profit_temp.append(give_score(tutores.iloc[i], bichos.iloc[j]))
  profit.append(profit_temp)

solver = pywraplp.Solver.CreateSolver('SCIP')

x = {}
for i in range(num_tutores):
  for j in range(num_bichos):
    x[i,j] = solver.IntVar(0,1,'')

for i in range(num_tutores):
  solver.Add(solver.Sum([x[i,j] for j in range(num_bichos)]) <= 1) #each tutor has at most one bicho

for j in range(num_bichos):
  solver.Add(solver.Sum([x[i,j] for i in range(num_tutores)]) >= 1) #each bicho has at least one tutor

for j in range(num_bichos):
  solver.Add(solver.Sum([x[i,j] for i in range(num_tutores)]) <= 1) #each bicho has at most one tutor

objective_terms = []
for i in range(num_tutores):
  for j in range(num_bichos):
    objective_terms.append(profit[i][j]*x[i,j])
solver.Maximize(solver.Sum(objective_terms))

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
  for i in range(num_tutores):
    for j in range(num_bichos):
      if x[i,j].solution_value() > 0.5:
        print('%s vai ser o tutor de %s' % (tutores.iloc[i][0], bichos.iloc[j][0]))
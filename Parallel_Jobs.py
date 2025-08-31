from decimal import *

import tinydb

import Finance_Window


def RevenueCalculations(database: tinydb.TinyDB):
    YearlyRevenue, MonthlyRevenue = Finance_Window.GetRevenueStats(database)

    # convert to string for json serialization
    for year in YearlyRevenue:
        YearlyRevenue[year] = str(YearlyRevenue[year])
        for month in MonthlyRevenue[year]:
            MonthlyRevenue[year][month] = str(MonthlyRevenue[year][month])

    transient = {
        "transient_name": "Revenue_Calculations",
        "yearly_revenue": YearlyRevenue,
        "monthly_revenue": MonthlyRevenue,
    }
    return transient


def ExpenseCalculations(database: tinydb.TinyDB):
    YearlyExpenses, MonthlyExpenses = Finance_Window.GetExpenseStats(database)

    # convert to string for json serialization
    for year in YearlyExpenses:
        YearlyExpenses[year] = str(YearlyExpenses[year])
        for month in MonthlyExpenses[year]:
            MonthlyExpenses[year][month] = str(MonthlyExpenses[year][month])

    transient = {
        "transient_name": "Expense_Calculations",
        "yearly_expenses": YearlyExpenses,
        "monthly_expenses": MonthlyExpenses,
    }
    return transient

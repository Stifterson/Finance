import numpy as np
import matplotlib.pyplot as plt

class TeachersSalaryComparison():
    """
    Data from 2024
    """
    SALARY_ZH = {"1": 97839,
                 "2": 101458,
                 "3": 104219,
                 "4": 107837,
                 "5": 111453,
                 "6": 115072,
                 "7": 118689,
                 "8": 121449,
                 "9": 125068,
                 "10": 128686,
                 "11": 132305,
                 "12": 133855,
                 "13": 135405,
                 "14": 136957,
                 "15": 138503,
                 "16": 140057,
                 "17": 141605,
                 "18": 143158,
                 "19": 144706,
                 "20": 146258,
                 "21": 147811,
                 "22": 149358,
                 "23": 150909,
                 "24": 152460,
                 "25": 154010,
                 "26": 155561,
                 "27": 157113}

    SALARY_TG = {"1": 79556.75,
                 "2": 81393,
                 "3": 83228.60,
                 "4": 85064.85,
                 "5": 88736.70,
                 "6": 90572.30,
                 "7": 92408.55,
                 "8": 94244.15,
                 "9": 96080.40,
                 "10": 97916.65,
                 "11": 99752.25,
                 "12": 101588.50,
                 "13": 103424.10,
                 "14": 104538.20,
                 "15": 105651.65,
                 "16": 106765.75,
                 "17": 107879.20,
                 "18": 108993.3,
                 "19": 110106.75,
                 "20": 111220.85,
                 "21": 112334.30,
                 "22": 113448.40,
                 "23": 114561.85,
                 "24": 115675.95,
                 "25": 116789.40,
                 "26": 117903.50,
                 "27": 119017.60,
                 "28": 120131.05}

    SALARY_SG = {"1": 74763.90,
                 "2": 78382.05,
                 "3": 82000.10,
                 "4": 82000.10,
                 "5": 85375.30,
                 "6": 88751.85,
                 "7": 92128.65,
                 "8": 95505.30,
                 "9": 98881.95,
                 "10": 98881.95,
                 "11": 98881.95,
                 "12": 98881.95,
                 "13": 102017.15,
                 "14": 105152.50,
                 "15": 108287.85,
                 "16": 111423.10,
                 "17": 114558.30,
                 "18": 114558.30,
                 "19": 114558.30,
                 "20": 114558.30,
                 "21": 114558.30,
                 "22": 115763.90,
                 "23": 117090.15,
                 "24": 118295.60,
                 "25": 119502.65,
                 "26": 120828.90,
                 "27": 122034.45}

    def __init__(self):
        """
        Init functions and plots
        """
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 4))

        self.plot_salary(axes[0])
        self.plot_salarydifference(axes[1])

        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_salary(self, ax):
        ax.plot(self.SALARY_ZH.keys(), self.SALARY_ZH.values(), '-', color='tomato', label="ZH")
        ax.plot(self.SALARY_TG.keys(), self.SALARY_TG.values(), '-', color='mediumpurple', label="TG")
        ax.plot(self.SALARY_SG.keys(), self.SALARY_SG.values(), '-', color='cornflowerblue', label="SG")

        ax.set_ylim(0, 160000)
        ax.set_ylabel("Salary per Year / CHF")
        ax.set_xlabel("Years of Work / a")
        ax.grid(color='lightgrey')
        ax.legend()


    def plot_salarydifference(self, ax):
        min_len = min([self.SALARY_ZH.keys(), self.SALARY_SG.keys(), self.SALARY_TG.keys()], key=len)
        diff_zh_sg, diff_zh_tg, diff_sg_tg = [0], [0], [0]
        for key in min_len:
            salary_zh = self.SALARY_ZH[key]
            salary_sg = self.SALARY_SG[key]
            salary_tg = self.SALARY_TG[key]
            diff_zh_sg.append(diff_zh_sg[-1] + salary_zh - salary_sg)
            diff_zh_tg.append(diff_zh_tg[-1] + salary_zh - salary_tg)
            diff_sg_tg.append(diff_sg_tg[-1] + salary_sg - salary_tg)

        ax.plot(min_len, diff_zh_sg[:-1], '-', color='tomato', label="ZH-SG")
        ax.plot(min_len, diff_zh_tg[:-1], '-', color='mediumpurple', label="ZH-TG")
        ax.plot(min_len, diff_sg_tg[:-1], '-', color='cornflowerblue', label="SG-TG")

        ax.set_ylabel("Salary per Year / CHF")
        ax.set_xlabel("Years of Work / a")
        ax.grid(color='lightgrey')
        ax.legend()


if __name__ == "__main__":
    salary = TeachersSalaryComparison()